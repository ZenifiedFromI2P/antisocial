import hashlib

def whirlpool(target):
    h = hashlib.new('whirlpool')
    h.update(target)
    return h.digest()
