from app.cryptosuites import CRYPTOSUITES
from config import settings
from fastapi import HTTPException


class DataIntegrity:
    def __init__(self):
        pass

    def get_issuer(self, credential):
        return (
            credential["issuer"]
            if isinstance(credential["issuer"], str)
            else credential["issuer"]["id"]
        )

    def default_options(self):
        return {
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "proofPurpose": "assertionMethod",
            "verificationMethod": f"did:key:{settings.MULTIKEY}#{settings.MULTIKEY}",
        }

    async def issue_credential(self, credential, options):
        issuer = self.get_issuer(credential)
        multikey = settings.MULTIKEY
        cryptosuite = CRYPTOSUITES[options["cryptosuite"]]
        options["proofPurpose"] = "assertionMethod"
        if 'did:key:' in issuer:
            options["verificationMethod"] = f"{issuer}#{multikey}"
        else:
            options["verificationMethod"] = f"{issuer}#key-0"
            

        secured_document = credential.copy()
        input_document = credential.copy()
        existing_proofs = input_document.pop("proof", None)
        existing_proofs = (
            existing_proofs if isinstance(existing_proofs, list) else [existing_proofs]
        )
        if "previousProof" in options:
            matching_proofs = []
            previous_proof = (
                options["previousProof"]
                if isinstance(options["previousProof"], list)
                else [options["previousProof"]]
            )
            for proof_id in previous_proof:
                proof = next(
                    (proof for proof in existing_proofs if proof["id"] == proof_id),
                    None,
                )
                if not proof:
                    raise ""
                matching_proofs.append(proof)
            input_document["proof"] = matching_proofs
        new_proof = await cryptosuite().add_proof(credential, options)
        existing_proofs.append(new_proof)
        return await cryptosuite().add_proof(credential, options)

    async def verify_credential(self, vc, options):
        all_proofs = vc.pop("proof", None)
        all_proofs = all_proofs if isinstance(all_proofs, list) else [all_proofs]
        all_verifications = []
        for proof in all_proofs:
            if proof["cryptosuite"] not in CRYPTOSUITES:
                raise HTTPException(status_code=400, detail="Unsupported cryptosuite.")
            cryptosuite = CRYPTOSUITES[proof["cryptosuite"]]()
            verified = await cryptosuite.verify_proof(
                unsecured_document=vc, proof=proof
            )
            all_verifications.append(verified)
        verification_results = {"verified": all(all_verifications)}
        return verification_results
