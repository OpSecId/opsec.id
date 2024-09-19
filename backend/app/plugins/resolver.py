from app.plugins import AskarWallet
from multiformats import multibase


class Resolver:
    def __init__(self):
        pass
    def multikey_to_bytes(self, multikey):
        return bytes(bytearray(multibase.decode(multikey))[2:])
    
    def resolve_verification_method(self, verification_method):
        if verification_method.startswith("did:key:"):
            multikey = verification_method.split('#')[-1]
            return self.multikey_to_bytes(multikey)
        if verification_method.startswith("did:web:"):
            pass