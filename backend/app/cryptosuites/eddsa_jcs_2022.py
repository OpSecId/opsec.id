"""EddsaJcs2022 cryptosuite."""

from hashlib import sha256
import json
import canonicaljson
from multiformats import multibase
from app.plugins.askar import AskarWallet
from app.plugins.resolver import Resolver


class CryptoSuiteException(Exception):
    """Base exception for cryptosuites."""


class EddsaJcs2022:
    """EddsaJcs2022 suite."""

    def __init__(self):
        """Create new EddsaJcs2022 Cryptosuite instance.
        https://www.w3.org/TR/vc-di-eddsa/#eddsa-rdfc-2022
        """
        super().__init__()

    async def add_proof(self, document, proof_options):
        """Data Integrity Add Proof Algorithm.
        https://www.w3.org/TR/vc-data-integrity/#add-proof
        """
        
        existing_proof = document.pop("proof", [])
        
        secured_document = document.copy()
        secured_document["proof"] = (
            [existing_proof] if isinstance(existing_proof, dict) else existing_proof
        )

        # try:
        hash_data = (
            sha256(canonicaljson.encode_canonical_json(proof_options)).digest()
            + sha256(canonicaljson.encode_canonical_json(document)).digest()
        )
        proof_bytes = AskarWallet().key.sign_message(hash_data)

        proof = proof_options.copy()
        proof["proofValue"] = multibase.encode(proof_bytes, "base58btc")

        secured_document["proof"].append(proof)

        return secured_document
        # except Exception:
        #     raise CryptoSuiteException()

    async def verify_proof(self, unsecured_document, proof):
        """Data Integrity Verify Proof Algorithm.
        https://www.w3.org/TR/vc-data-integrity/#verify-proof
        """
        proof_options = proof.copy()
        proof_value = proof_options.pop("proofValue")
        signature = multibase.decode(proof_value)

        hash_data = (
            sha256(canonicaljson.encode_canonical_json(proof_options)).digest()
            + sha256(canonicaljson.encode_canonical_json(unsecured_document)).digest()
        )
        public_bytes = Resolver().resolve_verification_method(proof["verificationMethod"])
        key = await AskarWallet().get_verification_key(public_bytes)
        # try:
        if key.verify_signature(message=hash_data, signature=signature):
            return True
        return False
        # except:
        #     raise CryptoSuiteException()

        # except Exception:
        #     raise CryptoSuiteException()
