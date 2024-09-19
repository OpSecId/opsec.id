from aries_askar import Store, Key, KeyAlg
from aries_askar.bindings import LocalKeyHandle
from fastapi import HTTPException
from config import settings
from multiformats import multibase
import hashlib
import json
from app.models.did_document import DidDocument, VerificationMethod, Service

PREFIXES = {"ed25519": "ed01"}
ALGORITHMS = {"6M": "ed25519"}


class AskarWallet:
    def __init__(self):
        self.db = settings.ASKAR_DB
        self.store_key = Store.generate_raw_key(
            hashlib.md5(settings.DOMAIN.encode()).hexdigest()
        )

    async def provision(self, recreate=False):
        await Store.provision(self.db, "raw", self.store_key, recreate=recreate)
        store = await Store.open(self.db, "raw", self.store_key)
        key = Key(LocalKeyHandle()).from_seed(KeyAlg.ED25519, settings.SECRET_KEY)
        # key = Key(LocalKeyHandle()).from_seed(KeyAlg.P256, self.store_key)
        # key = Key(LocalKeyHandle()).from_seed(KeyAlg.P384, self.store_key)
        did_web = f'did:web:{settings.DOMAIN}'
        multikey = self.key_to_multikey(key)
        did_doc = DidDocument(
            id=did_web,
            authentication=[f'{did_web}#key-01'],
            assertionMethod=[f'{did_web}#key-01'],
            verificationMethod=[VerificationMethod(
                id=f'{did_web}#key-01',
                controller=did_web,
                publicKeyMultibase=multikey,
            )],
            service=[Service(
                id=f'{did_web}#vc-api',
                type='LinkedDomains',
                serviceEndpoint=f'https://{settings.DOMAIN}',
            )],
        ).model_dump()
        try:
            async with store.session() as session:
                await session.insert(
                    "key",
                    multikey,
                    key.get_secret_bytes(),
                    {"~plaintag": "a", "enctag": "b"},
                )
                await session.insert(
                    "didDocument",
                    did_web,
                    json.dumps(did_doc),
                    {"~plaintag": "a", "enctag": "b"},
                )
        except:
            pass
        

    def key_to_multikey(self, key):
        return multibase.encode(
            bytes.fromhex(
                f"{PREFIXES[key.algorithm.value]}{key.get_public_bytes().hex()}"
            ),
            "base58btc",
        )

    def multikey_to_bytes(self, multikey):
        return bytes(bytearray(multibase.decode(multikey))[2:])

    def alg_from_multikey(self, multikey):
        for algorithm in ALGORITHMS:
            if multikey[1:].startswith(algorithm):
                return ALGORITHMS[algorithm]
        raise HTTPException(status_code=400, detail="Couldn't derive algorithm.")

    async def get_key(self, multikey):
        store = await Store.open(self.db, "raw", self.store_key)
        try:
            async with store.session() as session:
                secret_bytes = await session.fetch(
                    "key",
                    multikey,
                )
                return Key(LocalKeyHandle()).from_secret_bytes(
                    self.alg_from_multikey(multikey), secret_bytes.value
                )
        except:
            raise HTTPException(status_code=400, detail="No signing key found.")

    async def get_verification_key(self, public_bytes):
        try:
            return Key(LocalKeyHandle()).from_public_bytes(
                alg="ed25519", public=public_bytes
            )
        except:
            raise HTTPException(status_code=400, detail="Couldn't derive verificaiton key.")

    # async def get_verification_key(self, public_bytes):
    #     try:
    #         return Key(LocalKeyHandle()).from_public_bytes(public_bytes)
    #     except:
    #         raise HTTPException(status_code=400, detail="Couldn't derive verificaiton key.")


class AskarStorage:
    def __init__(self):
        self.db = settings.ASKAR_DB
        self.key = Store.generate_raw_key(
            hashlib.md5(settings.DOMAIN.encode()).hexdigest()
        )

    async def provision(self, recreate=False):
        await Store.provision(self.db, "raw", self.key, recreate=recreate)

    async def open(self):
        return await Store.open(self.db, "raw", self.key)

    async def fetch(self, category, data_key):
        store = await self.open()
        try:
            async with store.session() as session:
                data = await session.fetch(category, data_key)
            return json.loads(data.value)
        except:
            return None

    async def store(self, category, data_key, data):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.insert(
                    category,
                    data_key,
                    json.dumps(data),
                    {"~plaintag": "a", "enctag": "b"},
                )
        except:
            raise HTTPException(status_code=404, detail="Couldn't store record.")

    async def update(self, category, data_key, data):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.replace(
                    category,
                    data_key,
                    json.dumps(data),
                    {"~plaintag": "a", "enctag": "b"},
                )
        except:
            raise HTTPException(status_code=404, detail="Couldn't update record.")
