from django.shortcuts import render
from django.views.generic import View
from .forms import GroupSeedForm as GSF
from .forms import UserSeedForm as USF
import nacl.signing as signfool
import nacl.public as pubfool
from nacl.encoding import Base64Encoder as b64
import antisocial.tools.db as db
from antisocial.tools.serversync import sendgroup
import json
import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as KDF
from cryptography.hazmat.backends import default_backend

def whirlpool(target):
    h = hashlib.new('whirlpool')
    h.update(target)
    return h.digest()

def index(request):
    return render(request, 'helper.html', {})

# Create your views here.
class StrapGroup(View):
    def get(self, request):
        return render(request, 'group.html', {'form': GSF()})
    def post(self, request):
        form = GSF(request.POST)
        pubk = None
        privk = None
        pubfp = None
        privfp = None
        edseed = None
        if not form.is_valid():
            raise RuntimeError("Invalid HTML form submitted")
        seed = form.cleaned_data['seed']
        if seed == 'none':
            gke = pubfool.PrivateKey.generate()
            gks = signfool.SigningKey.generate()
            db.set('gke', gke)
            db.set('gks', gks)
            seed = base64.b64encode(json.dumps(dict(gke={'public_key': base64.b64encode(gke.public_key._public_key).decode(), 'private_key': base64.b64encode(gke._private_key).decode()},
                                   gks={'seed': base64.b64encode(gks._seed).decode()})).encode()).decode()
            pubk = gke.public_key._public_key
            privk = gke._private_key
            edseed = gks._seed
            sk = gks.verify_key.encode(encoder=b64)
            ek = gke.public_key.encode(encoder=b64)
            gkfp = base64.b64encode(whirlpool(sk+ek))
            db.set('gkfp', gkfp.decode())
            sendgroup(gkfp, sk, ek)
        else:
            seed = base64.b64decode(seed).decode()
            seed = json.loads(seed)
            # Format of seed:
            # {'public_key': 'base64-encoded PublicKey', 'private_key': 'base64-encoded PrivateKey'}
            pub = pubk = base64.b64decode(seed['gke']['public_key'])
            if len(pub) != 32:
                return "Error: Public key's length should be 32 bytes, check your input"
            priv = privk = base64.b64decode(seed['gke']['private_key'])
            if len(priv) != 32:
                return "Error: Private key's length should be 32 bytes, check your input tool"
            # Construct a PublicKey object
            pub = pubfool.PublicKey(pub)
            # Construct a Private Key object
            priv = pubfool.PrivateKey(priv)
            priv.public_key = pub
            edseed = base64.b64decode(seed['gks']['seed'])
            gks = signfool.SigningKey(seed=edseed)
            sk = gks.verify_key.encode(encoder=b64)
            ek = priv.public_key.encode(encoder=b64)
            gkfp = base64.b64encode(whirlpool(sk+ek))
            # Save the key
            db.set('gke', priv)
            db.set('gks', gks)
            db.set('gkfp', gkfp.decode())
            # I think it's already sent to the server because it was off a seed
            # Create a seed
        pubfp = base64.b64encode(whirlpool(pubk)).decode()
        privfp = base64.b64encode(whirlpool(privk)).decode()
        edseed = base64.b64encode(whirlpool(edseed)).decode()
        return render(request, 'group.post.html', {'edseed': edseed,
                                                   'pubfp': pubfp,
                                                   'privfp': privfp,
                                                   'seed': seed,
                                                   })

class UserKG(View):
    def get(self, request):
        return render(request, 'user.get.html', {'form': USF()})
    def post(self, request):
        form = USF(request.POST)
        if not form.is_valid():
            raise RuntimeError("Invalid HTML Form submitted")
        password = form.cleaned_data['password']
        pseudonym = form.cleaned_data['pseudonym']
        kdf = KDF(
            algorithm=hashes.Whirlpool(),
            length=int(32+32), # 32: Edwards25519 seed, second 32: Curve25519 seed
            salt=whirlpool(pseudonym.encode()),
            iterations=int(1e6),
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        edkey = signfool.SigningKey(key[0:32]) # Use the first 32-bytes of the derived key as Edwards25519 seed
        cvkp = pubfool.PrivateKey(key[32:64]) # Use the second half as Curve25519 seed
        sig = db.get('gks').sign(cvkp.public_key.encode(encoder=b64))
        db.set("user-edkeys", edkey)
        db.set("user-cvkeys", cvkp)
        db.set("user-keysig", sig)
        edkey_fingerprint = base64.b64encode(whirlpool(edkey._signing_key)).decode()
        cvkey_fingerprint = base64.b64encode(whirlpool(cvkp._private_key)).decode()
        ctx = dict(edkey_fp=edkey_fingerprint, cvkey_fp=cvkey_fingerprint, sig=base64.b64encode(sig).decode())
        return render(request, 'user.post.html', ctx)
