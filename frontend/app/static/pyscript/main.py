from aries_askar import Store, Key, KeyAlg
from aries_askar.bindings import LocalKeyHandle
import acapy_agent
from pyscript import window, document


def create_key(event):
    key = Key(LocalKeyHandle()).generate(KeyAlg.ED25519)
