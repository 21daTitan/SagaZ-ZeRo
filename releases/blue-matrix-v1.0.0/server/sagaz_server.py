#!/usr/bin/env python3
"""HooLeeSh33t: local-only static frontend and optional gated chat proxy.

This is NOT the full agent/core. Execution, uploads, external integrations and
BYOK per-user accounts must be connected to the actual SagaZ Core separately.
Python 3.9+; no third-party dependencies. Secrets are server environment only.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import logging
import mimetypes
import os
from pathlib import Path
import secrets
import sys
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from time import monotonic, time
from urllib.parse import parse_qsl, unquote, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

PROJECT = Path(__file__).resolve().parent.parent
APP_ROOT = (PROJECT / 'apps').resolve()
CORE_ROOT = Path(os.environ.get('SAGAZ_CORE_ROOT', PROJECT.parents[1])).resolve()
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))
try:
    from sagaz.cti import CTIError, search as cti_search, summary as cti_summary
    from sagaz.gateway.policy import LOCAL_UI
    from sagaz.gateway.service import Gateway
    CTI_GATEWAY = Gateway(CORE_ROOT / 'projects' / 'hooleesh33t' / 'state')
except ImportError:
    CTIError = RuntimeError
    cti_search = cti_summary = None
    LOCAL_UI = CTI_GATEWAY = None
CTI_READY = CTI_GATEWAY is not None
HOST = os.environ.get('SAGAZ_BIND', '127.0.0.1')
PORT = int(os.environ.get('SAGAZ_PORT', '8765'))
UPSTREAM = os.environ.get('SAGAZ_UPSTREAM_URL', 'https://api.openai.com/v1/chat/completions').strip()
MODEL = os.environ.get('SAGAZ_MODEL', 'gpt-4.1-mini').strip()
API_KEY = os.environ.get('SAGAZ_API_KEY', '').strip()
ADMIN_PASSWORD = os.environ.get('SAGAZ_ADMIN_PASSWORD', '')
SESSION_SECRET = os.environ.get('SAGAZ_SESSION_SECRET', '')
COOKIE_SECURE = os.environ.get('SAGAZ_COOKIE_SECURE', '0') == '1'
SESSION_READY = bool(ADMIN_PASSWORD and len(SESSION_SECRET) >= 32)
AUTH_READY = bool(API_KEY and SESSION_READY)
SESSION_TTL = 12 * 3600
COOKIE_NAME = 'sagaz_sid'
LOCK = Lock()
HISTORY = {}
LOGIN_ATTEMPTS = {}
LOG = logging.getLogger('sagaz')


def safe_upstream():
    p = urlsplit(UPSTREAM)
    return (p.scheme == 'https' or (p.scheme == 'http' and p.hostname in ('localhost', '127.0.0.1'))) and bool(p.netloc) and not (p.username or p.password)


def new_session():
    payload = '%d:%s' % (int(time()), secrets.token_hex(18))
    encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip('=')
    signature = hmac.new(SESSION_SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return encoded + '.' + signature


def verify_session(cookie_header):
    if not SESSION_READY or not cookie_header:
        return None
    try:
        jar = SimpleCookie()
        jar.load(cookie_header)
        token = jar[COOKIE_NAME].value
        encoded, signature = token.rsplit('.', 1)
        expected = hmac.new(SESSION_SECRET.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload = base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)).decode()
        ts = int(payload.split(':', 1)[0])
        if not (0 <= time() - ts <= SESSION_TTL):
            return None
        return token
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        return None


class App(BaseHTTPRequestHandler):
    server_version = 'SagaZWeb/1.0'
    sys_version = ''

    def log_message(self, fmt, *args):
        LOG.info('%s - %s', self.client_address[0], fmt % args)

    def headers_common(self, ctype, length, code=200, *, cookie=None):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(length))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        if cookie is not None:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()

    def send_json(self, code, body, *, cookie=None):
        data = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode()
        self.headers_common('application/json; charset=utf-8', len(data), code, cookie=cookie)
        self.wfile.write(data)

    def json_input(self):
        try:
            n = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return None
        if n < 2 or n > 20000:
            return None
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return None
        try:
            x = json.loads(self.rfile.read(n).decode('utf-8'))
            return x if isinstance(x, dict) else None
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def get_session(self):
        return verify_session(self.headers.get('Cookie', ''))

    def good_origin(self):
        origin = self.headers.get('Origin', '')
        if not origin:
            return True  # nonbrowser clients still need session + custom header
        p = urlsplit(origin)
        host = self.headers.get('Host', '')
        if p.netloc != host or p.scheme not in ('http', 'https'):
            return False
        return True

    def do_GET(self):
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == '/healthz':
            return self.send_json(200, {'ok': True, 'service': 'sagaz-web-preview'})
        if path == '/api/v1/status':
            active = bool(self.get_session())
            return self.send_json(200, {
                'service': 'sagaz-zero', 'chat': bool(AUTH_READY and active and safe_upstream()),
                'auth_required': SESSION_READY, 'authenticated': active,
                'model': MODEL if active and AUTH_READY else None,
                'capabilities': ['chat'] if active and AUTH_READY and safe_upstream() else [],
                'preview': True,
            })
        if path in ('/api/cti/summary', '/api/cti/search'):
            if not SESSION_READY or not self.get_session():
                return self.send_json(401, {'error': 'authentication_required'})
            if not self.good_origin():
                return self.send_json(403, {'error': 'request_not_allowed'})
            if not CTI_READY:
                return self.send_json(503, {'error': 'cti_unavailable'})
            tool = 'sagaz_cti_summary' if path.endswith('/summary') else 'sagaz_cti_search'
            operation = 'cti_summary' if path.endswith('/summary') else 'cti_search'
            try:
                LOCAL_UI.check_tool(tool)
                params = parse_qsl(parsed.query, keep_blank_values=True, max_num_fields=4)
                if path.endswith('/summary'):
                    if params:
                        raise ValueError('invalid_parameters')
                    CTI_GATEWAY.require(LOCAL_UI, operation)
                    return self.send_json(200, cti_summary())
                values = {}
                for key, value in params:
                    if key not in ('q', 'limit') or key in values:
                        raise ValueError('invalid_parameters')
                    values[key] = value
                if 'q' not in values:
                    raise ValueError('missing_query')
                limit = 20
                if 'limit' in values:
                    if not values['limit'].isascii() or not values['limit'].isdigit():
                        raise ValueError('invalid_limit')
                    limit = int(values['limit'])
                CTI_GATEWAY.require(LOCAL_UI, operation)
                return self.send_json(200, cti_search(values['q'], limit))
            except PermissionError:
                return self.send_json(403, {'error': 'permission_denied'})
            except ValueError as exc:
                return self.send_json(400, {'error': str(exc)})
            except CTIError:
                return self.send_json(503, {'error': 'cti_unavailable'})
        if path in ('/', '/index.html', '/creator', '/creator/'):
            target = ('/apps/dsant-creator-v1/index.html'
                      if path in ('/creator', '/creator/') else
                      '/apps/hooleesh33t-matrix-v1/index.html')
            self.send_response(302)
            self.send_header('Location', target)
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return
        if not path.startswith('/apps/'):
            return self.send_json(404, {'error': 'not_found'})
        file = (PROJECT / unquote(path.lstrip('/'))).resolve()
        if not file.is_relative_to(APP_ROOT) or file.suffix.lower() not in ('.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.webp', '.ico') or not file.is_file():
            return self.send_json(404, {'error': 'not_found'})
        data = file.read_bytes()
        ctype = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
        if ctype.startswith('text/') or ctype in ('application/javascript',):
            ctype += '; charset=utf-8'
        self.headers_common(ctype, len(data))
        self.wfile.write(data)

    def do_POST(self):
        path = urlsplit(self.path).path
        # Prevent a cross-site form POST; no CORS, no implicit credential use.
        if self.headers.get('X-SagaZ-Request') != '1' or not self.good_origin():
            return self.send_json(403, {'error': 'request_not_allowed'})
        if path == '/api/v1/login':
            if not SESSION_READY:
                return self.send_json(503, {'error': 'authentication_not_configured'})
            addr = self.client_address[0]
            now = monotonic()
            with LOCK:
                attempts = [t for t in LOGIN_ATTEMPTS.get(addr, []) if now - t < 600]
                if len(attempts) >= 5:
                    return self.send_json(429, {'error': 'try_later'})
            data = self.json_input()
            if not data or not isinstance(data.get('password'), str) or not hmac.compare_digest(data['password'], ADMIN_PASSWORD):
                with LOCK:
                    LOGIN_ATTEMPTS[addr] = (attempts + [now])[-5:]
                return self.send_json(401, {'error': 'incorrect_credentials'})
            with LOCK:
                LOGIN_ATTEMPTS.pop(addr, None)
            token = new_session()
            cookie = f'{COOKIE_NAME}={token}; Path=/; Max-Age={SESSION_TTL}; HttpOnly; SameSite=Strict'
            if COOKIE_SECURE:
                cookie += '; Secure'
            return self.send_json(200, {'ok': True}, cookie=cookie)
        if path == '/api/v1/logout':
            cookie = f'{COOKIE_NAME}=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict'
            if COOKIE_SECURE:
                cookie += '; Secure'
            return self.send_json(200, {'ok': True}, cookie=cookie)
        session = self.get_session()
        if not session:
            return self.send_json(401, {'error': 'authentication_required'})
        if path == '/api/v1/chat/reset':
            with LOCK:
                HISTORY.pop(session, None)
            return self.send_json(200, {'ok': True})
        if path != '/api/v1/chat':
            return self.send_json(404, {'error': 'not_found'})
        if not AUTH_READY:
            return self.send_json(503, {'error': 'chat_not_configured'})
        if not safe_upstream():
            return self.send_json(503, {'error': 'upstream_not_allowed'})
        payload = self.json_input()
        msg = payload.get('message') if payload else None
        if not isinstance(msg, str) or not msg.strip() or len(msg) > 12000:
            return self.send_json(400, {'error': 'invalid_message'})
        with LOCK:
            previous = list(HISTORY.get(session, []))[-16:]
        messages = [{'role': 'system', 'content': 'Você é SagaZ-ZeRo, assistente operacional by dSant. Seja preciso. Não afirme executar tarefas externas sem ferramentas autorizadas. Comandos e ações críticas exigem aprovação.'}] + previous + [{'role': 'user', 'content': msg.strip()}]
        data = json.dumps({'model': MODEL, 'messages': messages, 'max_tokens': 1000}).encode()
        req = Request(UPSTREAM, data=data, headers={
            'Authorization': 'Bearer ' + API_KEY, 'Content-Type': 'application/json',
            'User-Agent': 'SagaZ-ZeRo-Web/1.0'
        }, method='POST')
        try:
            with urlopen(req, timeout=45) as res:
                response = json.loads(res.read(1024 * 1024).decode())
            reply = response['choices'][0]['message']['content']
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError('invalid upstream response')
        except (HTTPError, URLError, ValueError, KeyError, IndexError, json.JSONDecodeError, TimeoutError) as e:
            LOG.warning('Falha de provedor: %s', type(e).__name__)
            return self.send_json(502, {'error': 'provider_unavailable'})
        with LOCK:
            if len(HISTORY) > 300:  # bounded memory, no persistence
                HISTORY.clear()
            HISTORY[session] = (previous + [{'role': 'user', 'content': msg.strip()}, {'role': 'assistant', 'content': reply}])[-16:]
        return self.send_json(200, {'reply': reply})


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    if API_KEY and not SESSION_READY:
        raise SystemExit('ERRO: para ativar chat, defina SAGAZ_ADMIN_PASSWORD e SAGAZ_SESSION_SECRET (>= 32 caracteres).')
    if AUTH_READY and not safe_upstream():
        raise SystemExit('ERRO: URL do provedor não permitida. Use HTTPS ou HTTP em localhost.')
    if HOST not in ('127.0.0.1', 'localhost', '::1'):
        LOG.warning('ATENÇÃO: endereço de escuta externo configurado. Exija HTTPS, autenticação e proxy seguro.')
    LOG.info('HooLeeSh33t em http://%s:%s | chat=%s', HOST, PORT, 'autenticado' if AUTH_READY else 'desativado (prévia)')
    ThreadingHTTPServer((HOST, PORT), App).serve_forever()

if __name__ == '__main__':
    main()
