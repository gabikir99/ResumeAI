import hashlib
from flask import Request

def get_fingerprint(req: Request) -> str:
    """Generate a simple fingerprint from request headers."""
    user_agent = req.headers.get('User-Agent', '')
    accept_lang = req.headers.get('Accept-Language', '')
    ip = req.headers.get('X-Forwarded-For', req.remote_addr or '')
    raw = f"{ip}|{user_agent}|{accept_lang}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()