from config import settings

EXAMPLE_CREDENTIAL = {
    "@context": ["https://www.w3.org/ns/credentials/v2"],
    "type": ["VerifiableCredential"],
    "issuer": {
        "id": settings.DID_KEY,
        "name": "Open Security and Identity inc."
    },
    "credentialSubject": {
        "name": "Alice"
    },
}