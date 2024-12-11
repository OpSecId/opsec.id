import base64
from app.plugins import AskarWallet
from aries_askar import Key
import json
from config import settings
# import jwt


class VcJose:
    def __init__(self):
        pass

    def get_issuer(self, credential):
        return (
            credential["issuer"]
            if isinstance(credential["issuer"], str)
            else credential["issuer"]["id"]
        )

    def b64_encode(self, message):
        return base64.urlsafe_b64encode(message).decode().rstrip("=")

    def b64_decode(self, message):
        return base64.urlsafe_b64decode(message).decode()

    async def sign(self, headers, payload):
        encoded_headers = self.b64_encode(json.dumps(headers).encode())
        encoded_payload = self.b64_encode(json.dumps(payload).encode())
        signature = AskarWallet().key.sign_message(
            f"{encoded_headers}.{encoded_payload}".encode()
        )

        encoded_signature = self.b64_encode(signature)

        return f"{encoded_headers}.{encoded_payload}.{encoded_signature}"

    async def verify(self, headers, payload, signature):
        encoded_headers = self.b64_decode(headers)
        encoded_payload = self.b64_decode(headers)
        encoded_signature = self.b64_decode(headers)
        public_bytes = ""
        key = Key.from_public_bytes(alg=headers["alg"], public=public_bytes)
        # verified = key.verify_signature(message=f"{encoded_headers}.{encoded_payload}".encode(), signature=encoded_signature)
        pass

    async def issue_credential(self, credential):
        issuer = self.get_issuer(credential)
        multikey = issuer.lstrip("did:key:")
        headers = {
            "alg": "EdDSA",
            "kid": multikey,
            "typ": "vc+ld+json",
            "cty": "vc+ld+json",
        }
        jwt_token = await self.sign(headers, credential)
        return {
            "@context": "https://www.w3.org/ns/credentials/v2",
            "id": f"data:application/vc+jwt,{jwt_token}",
            "type": "EnvelopedVerifiableCredential",
        }

    def verify_credential(self, credential):
        jwt_token = credential["id"].split(",")[-1]
        jwt_headers = jwt_token.split(".")[0]
        jwt_payload = jwt_token.split(".")[1]
        jwt_signature = jwt_token.split(".")[2]

    async def create_presentation(self, presentation):
        # TODO, find a better way to derive multikey
        multikey = settings.MULTIKEY
        headers = {
            "alg": "EdDSA",
            "kid": multikey,
            "typ": "vp+ld+json",
            "cty": "vp+ld+json",
        }
        jwt_token = await self.sign(headers, presentation)
        return {
            "@context": "https://www.w3.org/ns/credentials/v2",
            "id": f"data:application/vp+jwt,{jwt_token}",
            "type": "EnvelopedVerifiablePresentation",
        }

    def verify_presentation(self):
        pass
