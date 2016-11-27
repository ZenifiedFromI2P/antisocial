from django.shortcuts import render, redirect
from django.views.generic import View
from antisocial.tools.crypto import whirlpool
from nacl.encoding import Base64Encoder as b64
from nacl.exceptions import BadSignatureError as BadSig
from .forms import FPForm
from urllib.parse import quote
import nacl.signing as signfool
import antisocial.tools.db as db
import antisocial.tools.serversync as server
import base64
import binascii

debase = lambda content: base64.b64decode(content)

# Create your views here.
class Feedstream(View):
    def get(self, request, key):
        if key == 'self':
            key = db.get('user-edkeys').verify_key.encode(encoder=b64)
            key = quote(key)
            return redirect(to="/feeds/{key}".format(key=key))
        stream = server.HTTP().POST('/get/feed', {'key': key})
        key = signfool.VerifyKey(key, b64)
        hits = list()
        for feed in stream:
            valid = True
            try:
                key.verify(feed['message'].encode(), debase(feed['sig']))
            except Exception:
                valid = False
            if valid:
                hits.append(feed['message'])
        hits.reverse()
        ctx = dict(hits=hits, key=key.encode(encoder=b64))
        return render(request, 'feeds.get.html', ctx)

class NewFP(View):
    def get(self, request):
        f = FPForm()
        return render(request, 'user.get.html', dict(form=f))
    def post(self, request):
        f = FPForm(request.POST)
        if not f.is_valid():
            raise RuntimeError("Invalid HTML form submitted")
        msg = f.cleaned_data['message']
        msig = db.get('user-edkeys').sign(msg.encode())
        msig = msig._signature
        msig = base64.b64encode(msig).decode()
        key = db.get('user-edkeys').verify_key.encode(encoder=b64).decode()
        j = {'msg': msg, 'sig': msig, 'key': key}
        server.HTTP().POST('/new/fp', j)
        return render(request, 'feeds.post.html', dict(j=j, msig=msig, feed=key))
