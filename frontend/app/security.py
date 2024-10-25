import os
import datetime
from urllib.parse import urlparse

from app.services import AskarStorage
import asyncio
import webauthn
from flask import request
from redis import Redis
from app.models.user import WebAuthnCredential

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

REGISTRATION_CHALLENGES = Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=0, #password=REDIS_PASSWORD
)

def _hostname():
    return str(urlparse(request.base_url).hostname)

def prepare_credential_creation(user):
    public_credential_creation_options = webauthn.generate_registration_options(
        rp_id=_hostname(),
        rp_name="OpSecId Discovery Wallet Demo",
        user_id=user['uid'],
        user_name=user['username'],
    )
    
    # Redis stores the binary challenge value.
    REGISTRATION_CHALLENGES.set(user['uid'], public_credential_creation_options.challenge)
    REGISTRATION_CHALLENGES.expire(user['uid'], datetime.timedelta(minutes=10))

    return webauthn.options_to_json(public_credential_creation_options)

def verify_and_save_credential(user, registration_credential):
    """Verify that a new credential is valid for the """
    expected_challenge = REGISTRATION_CHALLENGES.get(user['uid'])

    # If the credential is somehow invalid (i.e. the challenge is wrong),
    # this will raise an exception. It's easier to handle that in the view
    # since we can send back an error message directly.
    auth_verification = webauthn.verify_registration_response(
        credential=registration_credential,
        expected_challenge=expected_challenge,
        expected_origin=f"https://{_hostname()}",
        expected_rp_id=_hostname(),
    )

    # At this point verification has succeeded and we can save the credential
    credential = WebAuthnCredential(
        uid=user['uid'],
        credential_public_key=auth_verification.credential_public_key,
        credential_id=auth_verification.credential_id,
    ).model_dump()
    asyncio.run(AskarStorage().store('webauthn:credential', auth_verification.credential_id, credential))