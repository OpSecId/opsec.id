from flask import Blueprint, render_template, request, session, make_response, abort
import json
import requests
import datetime
from app.models.user import User
from app import security
import uuid
from app.services import AskarStorage
import asyncio
from webauthn.helpers.structs import RegistrationCredential
from webauthn.helpers.exceptions import InvalidRegistrationResponse

bp = Blueprint("auth", __name__)



@bp.route("/register", methods=["GET", "POST"])
def register():
    user = User(
        uid=str(uuid.uuid4()),
        username=str(uuid.uuid4())
    ).model_dump()
    asyncio.run(AskarStorage().store('user', user['uid'], user))
    pcco_json = security.prepare_credential_creation(user)
    res = make_response(
        render_template(
            "auth/_partials/register_credential.html",
            public_credential_creation_options=pcco_json,
        )
    )
    session['registration_user_uid'] = user['uid']

    return res

@bp.route("/login")
def login():
    return render_template(
        "pages/login.jinja",
        title='OpSecId'
    )

@bp.route("/add-credential", methods=["POST"])
def add_credential():
    user_uid = session.get("registration_user_uid")
    if not user_uid:
        abort(make_response("Error user not found", 400))
    user = asyncio.run(AskarStorage().fetch('user', user_uid))
    registration_credential = RegistrationCredential.parse_raw(request.get_data())
    try:
        security.verify_and_save_credential(user, registration_credential)
        session["registration_user_uid"] = None
        res = make_response('{"verified": true}', 201)
        res.set_cookie(
            "user_uid",
            user['uid'],
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=datetime.timedelta(days=30),
        )
        return res
    except InvalidRegistrationResponse:
        abort(make_response('{"verified": false}', 400))
    return None

