from flask import Blueprint, render_template, url_for, current_app, session, request, jsonify, redirect
import json
import uuid
import httpx
from flask_rq import job
from urllib.parse import unquote

bp = Blueprint("main", __name__)


@bp.before_request
def before_request_callback():
    # current_app.logger.info(f"[{request.method}] {request.path}")
    if "client_id" not in session:
        return redirect(url_for('auth.login'))
        session['client_id'] = str(uuid.uuid4())
        session['credentials'] = {}
        session['endpoint'] = current_app.config['ENDPOINT']
        session['invitation'] = 'https://didcomm.link/invitations/123'


@bp.route("/", methods=["GET"])
def index():
    current_app.logger.warning(session['credentials'])
    return render_template(
        "pages/index.jinja",
        title='OpSecId',
    )
    
@bp.route("/webhook/scanner", methods=["POST"])
def webhook_scanner():
    proccess_scanner_request(request)
    return jsonify({'status': 'ok'})


@job
def proccess_scanner_request(request):
    current_app.logger.warning("JOB LAUNCHED")
    payload = request.form['payload']
    if request.form['client_id'] != session['client_id']:
        return jsonify({'status': 'failed'})
    if isinstance(payload, str):
        if payload.startswith('https://'):
            # VC-PLAYGROUND INTERACTION
            if payload.startswith('https://vcplayground.org'):
                exchange_url = payload.split('/')[-1]
                exchange_url = unquote(exchange_url)
                # optional, see available protocols
                # r = httpx.get(f'{exchange_url}/protocols')
                r = httpx.post(exchange_url, data={})
                vp = r.json()['verifiablePresentation']
                for vc in vp['verifiableCredential']:
                    if not session['credentials'].get(vc['id']):
                        session['credentials'][vc['id']] = vc
            headers = {'accept': 'application/vc'}
            r = httpx.get(payload, headers=headers)
            if r.status_code == 200:
                vc = r.json()
                if not session['credentials'].get(vc['id']):
                    session['credentials'][vc['id']] = vc