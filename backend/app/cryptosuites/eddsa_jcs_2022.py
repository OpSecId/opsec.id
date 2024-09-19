"""EddsaJcs2022 cryptosuite."""

from hashlib import sha256
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
        Args:
            profile: Key profile to use.
        """
        super().__init__()

    async def _serialization(self, hash_data, options):
        """Data Integrity Proof Serialization Algorithm.
        https://www.w3.org/TR/vc-di-eddsa/#proof-serialization-eddsa-jcs-2022
        """
        multikey = options['verificationMethod'].split('#')[-1]
        key = await AskarWallet().get_key(multikey)
        proof_bytes = await key.sign_message(hash_data)
        return proof_bytes

    async def add_proof(self, document, proof_options):
        """Data Integrity Add Proof Algorithm.
        https://www.w3.org/TR/vc-data-integrity/#add-proof
        Args:
            document: The data to sign.
            proof_options: The proof options.
        Returns:
            secured_document: The document with a new proof attached
        """

        existing_proof = document.pop("proof", [])
        assert isinstance(existing_proof, list) or isinstance(existing_proof, dict)
        existing_proof = (
            [existing_proof] if isinstance(existing_proof, dict) else existing_proof
        )

        assert proof_options["type"] == "DataIntegrityProof"
        assert proof_options["cryptosuite"] == "eddsa-jcs-2022"
        assert proof_options["proofPurpose"]
        assert proof_options["verificationMethod"]

        # try:
        hash_data = (
            sha256(canonicaljson.encode_canonical_json(document)).digest()
            + sha256(canonicaljson.encode_canonical_json(proof_options)).digest()
        )
        multikey = proof_options['verificationMethod'].split('#')[-1]
        key = await AskarWallet().get_key(multikey)
        proof_bytes = key.sign_message(hash_data)

        proof = proof_options.copy()
        proof["proofValue"] = multibase.encode(proof_bytes, "base58btc")

        secured_document = document.copy()
        secured_document["proof"] = existing_proof
        secured_document["proof"].append(proof)

        return secured_document
        # except Exception:
        #     raise CryptoSuiteException()

    async def verify_proof(self, unsecured_document, proof):
        """Data Integrity Verify Proof Algorithm.
        https://www.w3.org/TR/vc-data-integrity/#verify-proof
        Args:
            unsecured_document: The data to check.
            proof: The proof.
        Returns:
            verification_response: Whether the signature is valid for the data
        """
        try:
            assert proof["type"] == "DataIntegrityProof"
            assert proof["cryptosuite"] == "eddsa-jcs-2022"
            assert proof["proofPurpose"]
            assert proof["proofValue"]
            assert proof["verificationMethod"]

            proof_options = proof.copy()
            proof_value = proof_options.pop("proofValue")
            signature = multibase.decode(proof_value)

            hash_data = (
                sha256(canonicaljson.encode_canonical_json(unsecured_document)).digest()
                + sha256(canonicaljson.encode_canonical_json(proof_options)).digest()
            )
            public_bytes = Resolver().resolve_verification_method(proof["verificationMethod"])
            key = await AskarWallet().get_verification_key(public_bytes)
            
            try:
                if key.verify_signature(message=hash_data, signature=signature):
                    return True
                return False
            except:
                raise CryptoSuiteException()

        except Exception:
            raise CryptoSuiteException()
