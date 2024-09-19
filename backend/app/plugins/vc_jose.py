import base64
from app.plugins import AskarWallet
import json
from config import settings

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
    
    async def sign(self, headers, payload):
        encoded_headers = self.b64_encode(json.dumps(headers).encode())
        encoded_payload = self.b64_encode(json.dumps(payload).encode())
        key = await AskarWallet().get_key(headers['kid'])
        signature = key.sign_message(f"{encoded_headers}.{encoded_payload}".encode())
        
        encoded_signature = self.b64_encode(signature)
        
        return f"{encoded_headers}.{encoded_payload}.{encoded_signature}"

    async def issue_credential(self, credential):
        issuer = self.get_issuer(credential)
        multikey = issuer.lstrip('did:key:')
        headers = {
            'alg': 'EdDSA',
            'kid': multikey,
            'typ': 'vc+ld+json',
            'cty': 'vc+ld+json'
        }
        jwt = await self.sign(headers, credential)
        return {
            "@context": "https://www.w3.org/ns/credentials/v2",
            "id": f"data:application/vc+jwt,{jwt}",
            "type": "EnvelopedVerifiableCredential"
        }

    def verify_credential(self, credential):
        pass

    async def create_presentation(self, presentation):
        # TODO, find a better way to derive multikey
        multikey = settings.MULTIKEY
        headers = {
            'alg': 'EdDSA',
            'kid': multikey,
            'typ': 'vp+ld+json',
            'cty': 'vp+ld+json'
        }
        jwt = await self.sign(headers, presentation)
        return {
            "@context": "https://www.w3.org/ns/credentials/v2",
            "id": f"data:application/vp+jwt,{jwt}",
            "type": "EnvelopedVerifiablePresentation"
        }

    def verify_presentation(self):
        pass
