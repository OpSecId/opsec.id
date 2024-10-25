from flask import Flask, jsonify, session, flash, redirect, send_file, request
from flask_session import Session
from flask_cors import CORS
from flask_rq import RQ
from flask_qrcode import QRcode
from flask_github import GitHub
from config import Config
from app.errors import bp as errors_bp
from app.routes.auth import bp as auth_bp
from app.routes.main import bp as main_bp
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    @app.route('/manifest.json')
    def serve_manifest():
        return send_file('manifest.json', mimetype='application/manifest+json')
    
    @app.route('/sw.js')
    def serve_sw():
        return send_file('sw.js', mimetype='application/javascript')
    
    # limiter = Limiter(get_remote_address)
    # limiter.init_app(app)
    
    # CORS(app)
    QRcode(app)
    Session(app)
    RQ(app)
    
    app.register_blueprint(errors_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    @app.route("/.well-known/did.json", methods=["GET"])
    def main_did_doc():
        did_doc = {}
        return jsonify(did_doc)
    
    return app