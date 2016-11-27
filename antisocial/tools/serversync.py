from antisocial.tools.crypto import whirlpool
from antisocial.tools.config import get as confget
import os
import requests
import base64
import json
import sys


baseurl = "http://localhost:6060"
baseurl_tor = 'http://oat5zooqn3cd365v.onion'
baseurl_i2p = 'http://lcfjoiulgyepizrl464rggjx6knjajsth4srem7aq3zeka6bzzta.b32.i2p'

def geturl():
    res = confget('mode', 'clearnet')
    if res == "clearnet":
        return baseurl, {}
    elif res == 'tor':
        torhost = confget("torhost", "localhost")
        torport = confget("torport", 9050)
        proxy = dict(http='socks5://{host}:{port}'.format(host=torhost, port=torport))
        return baseurl_tor, proxy
    elif res == 'i2p':
        i2phost = confget("i2phost", "localhost")
        i2pport = confget("i2pport", 4444)
        proxy = dict(http='http://{host}:{port}/'.format(host=i2phost, port=i2pport))
        return baseurl_i2p, proxy
    else:
        print("This mode hasn't been implemented")
        sys.exit(3)

class HTTP(object):
    def POST(self, suffix, data):
        burl, proxy = geturl()
        url = burl + suffix
        ojson = json.dumps(data)
        try:
            resp = requests.post(url, data=ojson, proxies=proxy)
        except Exception as e:
            sys.exit(5)
        fp = open('error.html', 'w')
        fp.write(resp.text)
        fp.close()
        return resp.json()


def getps(groupkh):
    payload = dict()
    payload['gkh'] = groupkh
    io = HTTP().POST('/get/stream', payload)
    return io

def sendgroup(gkh, edpub, cvpub):
    payload = dict()
    payload['gkh'] = gkh.decode()
    payload['edpub'] = edpub.decode()
    payload['cvpub'] = cvpub.decode()
    io = HTTP().POST("/new/group", payload)
    return io
