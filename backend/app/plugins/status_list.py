import requests, random
from config import settings
from bitstring import BitArray
import gzip, base64
import uuid
from app.plugins.askar import AskarStorage
from app.plugins.data_integrity import DataIntegrity
from app.utils import id_from_string
from multiformats import multibase


class BitstringStatusList:
    def __init__(self):
        self.store = AskarStorage()
        self.did_web = f"did:web:{settings.DOMAIN}"
        self.did_key = f"did:key:{settings.MULTIKEY}"
        self.id = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.did_key))
        self.endpoint = f"https://{settings.DOMAIN}/credentials/status/{self.id}"
        self.lenght = 200000

    def generate(self, bitstring):
        # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-generation-algorithm
        statusListBitarray = BitArray(bin=bitstring)
        statusListCompressed = gzip.compress(statusListBitarray.bytes)
        # statusList_encoded = base64.urlsafe_b64encode(statusListCompressed).decode("utf-8").rstrip("=")
        statusList_encoded = multibase.encode(statusListCompressed, "base64url")
        return statusList_encoded

    def expand(self, encoded_list):
        # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
        # statusListCompressed = base64.urlsafe_b64decode(encoded_list)
        statusListCompressed = multibase.decode(encoded_list)
        statusListBytes = gzip.decompress(statusListCompressed)
        statusListBitarray = BitArray(bytes=statusListBytes)
        statusListBitstring = statusListBitarray.bin
        return statusListBitstring

    async def create(self):
        # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-bitstringstatuslistcredential
        status_list_credential = {
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
            ],
            "type": ["VerifiableCredential", "BitstringStatusListCredential"],
            "issuer": self.did_key,
            "credentialSubject": {
                "type": "BitstringStatusList",
                "encodedList": self.generate(str(0) * self.lenght),
                "statusPurpose": ["revocation", "suspension"],
            },
        }
        print(f"Status List: {self.endpoint}")
        await AskarStorage().store(
            "statusListCredential", self.id, status_list_credential
        )
        await AskarStorage().store("statusListEntries", self.id, [0, self.lenght - 1])

    async def create_entry(self, purpose="revocation"):
        # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential
        storage = AskarStorage()
        status_entries = await storage.fetch("statusListEntries", self.id)
        # Find an unoccupied index
        status_index = random.choice(
            [e for e in range(self.lenght - 1) if e not in status_entries]
        )
        status_entries.append(status_index)
        await storage.update("statusListEntries", self.id, status_entries)

        credential_status_entry = {
            "id": f"{self.endpoint}#{status_index}",
            "type": "BitstringStatusListEntry",
            "statusPurpose": purpose,
            "statusListIndex": str(status_index),
            "statusListCredential": self.endpoint,
        }

        return credential_status_entry

    def get_credential_status(self, vc, statusType):
        # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
        statusListIndex = vc["credentialStatus"]["statusListIndex"]
        statusListCredentialUri = vc["credentialStatus"]["statusListCredential"]

        r = requests.get(statusListCredentialUri)
        statusListCredential = r.json()
        statusListBitstring = self.expand(
            statusListCredential["credentialSubject"]["encodedList"]
        )
        statusList = list(statusListBitstring)
        credentialStatusBit = statusList[statusListIndex]
        return True if credentialStatusBit == "1" else False

    async def change_credential_status(
        self, vc, statusBit, did_label, statusListCredentialId
    ):
        statusList_index = vc["credentialStatus"]["statusListIndex"]

        dataKey = askar.statusCredentialDataKey(did_label, statusListCredentialId)
        statusListCredential = await askar.fetch_data(
            settings.ASKAR_PUBLIC_STORE_KEY, dataKey
        )
        statusListEncoded = statusListCredential["credentialSubject"]["encodedList"]
        statusListBitstring = self.expand(statusListEncoded)
        statusList = list(statusListBitstring)

        statusList[statusList_index] = statusBit
        statusListBitstring = "".join(statusList)
        statusListEncoded = self.generate(statusListBitstring)

        statusListCredential["credentialSubject"]["encodedList"] = statusListEncoded

        did = vc["issuer"] if isinstance(vc["issuer"], str) else vc["issuer"]["id"]
        verkey = agent.get_verkey(did)
        options = {
            "verificationMethod": f"{did}#verkey",
            "proofPurpose": "AssertionMethod",
        }
        # Remove old proof
        statusListCredential.pop("proof")
        statusListCredential = agent.sign_json_ld(statusListCredential, options, verkey)

        return statusListCredential


async def get_status_list_credential(did_label, statusListCredentialId):
    try:
        dataKey = askar.statusCredentialDataKey(did_label, statusListCredentialId)
        statusListCredential = await askar.fetch_data(
            settings.ASKAR_PUBLIC_STORE_KEY, dataKey
        )
    except:
        return ValidationException(
            status_code=404,
            content={"message": "Status list not found"},
        )
    return statusListCredential
