from django.shortcuts import render
from django.views.generic import View
from .forms import PostForm as PF
from antisocial.tools.crypto import whirlpool
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as KDF
from cryptography.hazmat.backends import default_backend
from nacl.encoding import Base64Encoder as b64
import nacl.signing as signfool
import nacl.public as pubfool
import antisocial.tools.db as db
import antisocial.tools.serversync as server
import json
import base64
import hashlib
import os

debase = lambda something: base64.b64decode(something)

# Create your views here.
class Stream(View):
    def get(self, request):
        gks = db.get('gks')
        stream = server.getps(db.get('gkfp'))
        gke = db.get('gke')
        box = pubfool.Box(gke, gke.public_key)
        hits = list()
        for post in stream:
            valid = True # Valid signature, will be flipped to False on error
            try:
                post = json.loads(box.decrypt(debase(post['encrypted']), debase(post['nonce'])).decode())
                print(post)
            except Exception: # Multiple exceptions can happen which can show malformed message, such as non-UTF8 characters, bad JSON, bad nonce, bad ciphertext, etc. just miss and move on
                continue
            try:
                gks.verify_key.verify(post['msg'].encode(), debase(post['sig']))
                uks = signfool.VerifyKey(post['gangsta']['edpub'].encode(), encoder=b64)
                uks.verify(post['msg'].encode(), debase(post['usig']))
                post['KH'] = base64.b64encode(whirlpool(post['gangsta']['edpub'].encode()+post['gangsta']['cvpub'].encode())).decode()
            except BadSignatureError:
                valid = False
            except Exception:
                continue
            if valid:
                hits.append(post)
                pass
            pass
        hits.reverse()
        ctx = dict(hits=hits)
        return render(request, 'stream.get.html', ctx)

class NewPost(View):
    def get(self, request):
        return render(request, 'newpost.get.html', {'form': PF()})
    def post(self, request):
        form = PF(request.POST, request.FILES)
        if not form.is_valid():
            raise RuntimeError("Invalid HTML form submitted")
        message = form.cleaned_data['message']
        name = form.cleaned_data['name']
        image = form.cleaned_data['image']
        if message == 'none':
            raise KeyError("Message doesn't exist")
        gks = db.get('gks')
        gke = db.get('gke')
        sig = gks.sign(message.encode())
        usig = db.get("user-edkeys").sign(message.encode())
        box = pubfool.Box(gke, gke.public_key)
        gangsta = {
            'name': name,
            'edpub': db.get("user-edkeys").verify_key.encode(encoder=b64).decode(),
            'cvpub': db.get("user-cvkeys").public_key.encode(encoder=b64).decode(),
        }
        payload = {
            'msg': sig.message.decode(),
            'sig': base64.b64encode(sig.signature).decode(),
            'usig': base64.b64encode(usig.signature).decode(),
            'gangsta': gangsta,
        }
        if image is not None:
            buf = image.read()
            payload ['image'] = base64.b64encode(buf).decode()
        else:
            payload['image'] = None
        nonce = os.urandom(24)
        payload = json.dumps(payload)
        payload = box.encrypt(plaintext=payload.encode(), nonce=nonce)

        realpayload = {
            'key': db.get('gkfp'),
            'encrypted': base64.b64encode(payload._ciphertext).decode(),
            'nonce': base64.b64encode(nonce).decode(),
        }
        server.HTTP().POST("/new/post", realpayload)
        ctx = dict(sig=base64.b64encode(sig.signature).decode())
        return render(request, "newpost.post.html", ctx)
