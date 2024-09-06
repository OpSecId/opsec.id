from aries_askar import Store, Key, KeyAlg
from aries_askar.bindings import LocalKeyHandle
from fastapi import HTTPException
from config import settings
import hashlib
import json

class AskarWallet:
    def __init__(self):
        self.db = settings.ASKAR_DB
        self.store_key = Store.generate_raw_key(
            hashlib.md5(settings.DOMAIN.encode()).hexdigest()
        )

    async def provision(self, recreate=False):
        await Store.provision(self.db, "raw", self.store_key, recreate=recreate)
        key = Key(LocalKeyHandle()).from_seed(KeyAlg.ED25519, self.store_key)
        key = Key(LocalKeyHandle()).from_seed(KeyAlg.P256, self.store_key)
        key = Key(LocalKeyHandle()).from_seed(KeyAlg.P384, self.store_key)


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

