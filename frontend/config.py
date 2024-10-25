import redis
import os

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    COPYRIGHT = '© OpSecId 2024.'
    DOMAIN = 'opsecid.ca'
    CONTACT_EMAIL = 'contact@opsecid.ca'
    CONTACT_ADDRESS = 'Gatineau, QC, Canada'
    
    DOMAIN = os.getenv('DOMAIN')
    ENDPOINT = f"https://{DOMAIN}"
    
    ASKAR_DB = os.getenv('POSTGRES_DB')
    
    # GITHUB_CLIENT_ID = 'Iv23li6pps0uhORINsHO'
    # GITHUB_CLIENT_SECRET = 'bb30b3361c29b26079d387f5cc28b5b7a88e32db'
    
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url('redis://redis:6379')
    SESSION_COOKIE_NAME  = 'opsecid'
    
    RQ_DEFAULT_HOST = 'redis'
    # RQ_DEFAULT_PORT = ''
    # RQ_DEFAULT_PASSWORD = ''
    # RQ_DEFAULT_DB = ''
    # RQ_LOW_URL = 'redis://redis:6379/1'
    