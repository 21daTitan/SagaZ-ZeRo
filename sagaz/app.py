"""SagaZ: local blue console, built independently for dSantCreator."""
import argparse
from datetime import datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sys
import threading
from urllib.parse import urlparse, parse_qs
import uuid

ROOT=Path(__file__).resolve().parents[1]

# Keep the launcher usable as a script and the public API used by existing callers.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sagaz.services import CORE, prepare_task, research
from sagaz.catalog import skills, connection
from sagaz.cti import search as cti_search, summary as cti_summary
from sagaz.attribution import credits
from sagaz.gateway.service import Gateway
from sagaz.gateway.policy import authenticate, Denied
from sagaz.gateway.router import ProviderUnavailable
from sagaz.gateway.protocols import ProtocolError


class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,state_root=None):
        self.session=secrets.token_urlsafe(32)
        self.state_root=Path(state_root) if state_root else ROOT/'projects/sagaz'
        self.busy=threading.BoundedSemaphore(2)
        self.gateway=Gateway(self.state_root)
        super().__init__(address,Handler)


class Handler(BaseHTTPRequestHandler):
    server_version='SagaZ/3.7'
    def log_message(self,*args):pass
    def valid_host(self):
        port=self.server.server_port
        return self.headers.get('Host') in (f'127.0.0.1:{port}',f'localhost:{port}')
    def send(self,status,data,kind='application/json; charset=utf-8',cookie=False):
        body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
        if cookie:self.send_header('Set-Cookie',f'sagaz_session={self.server.session}; HttpOnly; SameSite=Strict; Path=/')
        self.end_headers();self.wfile.write(body)
    def project(self,ident):
        if not isinstance(ident,str) or not (len(ident)==32 and all(c in '0123456789abcdef' for c in ident)):raise ValueError('ID inválido')
        path=self.server.state_root/ident
        if path.is_symlink():raise ValueError('Projeto inválido')
        return path
    def scope(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie',''))
        except Exception:
            return authenticate(None,self.server.session,None,None)
        item = cookie.get('sagaz_session')
        token = self.headers.get('Authorization','')
        bearer = token[7:] if token.startswith('Bearer ') else None
        return authenticate(item.value if item else None, self.server.session,
                            bearer, os.environ.get('SAGAZ_API_TOKEN'))

    def do_GET(self):
        if not self.valid_host():return self.send(421,{'error':'Host não permitido'})
        path=urlparse(self.path).path
        if path=='/':return self.send(200,(ROOT/'sagaz/index.html').read_bytes(),'text/html; charset=utf-8',cookie=True)
        if path in ('/assets/app.css', '/assets/app.js'):
            name=path.rsplit('/',1)[-1]
            kind='text/css; charset=utf-8' if name.endswith('.css') else 'text/javascript; charset=utf-8'
            return self.send(200,(ROOT/'sagaz/static'/name).read_bytes(),kind)
        if path=='/api/skills':return self.send(200,skills())
        if path in ('/api/cti/search', '/api/cti/summary'):
            if self.scope().connector == 'public':
                return self.send(403, {'error': 'Autenticação necessária'})
            try:
                if path == '/api/cti/summary':
                    return self.send(200, cti_summary())
                params = parse_qs(urlparse(self.path).query, keep_blank_values=True)
                if set(params) - {'q', 'limit'} or len(params.get('q', [])) != 1 or len(params.get('limit', [])) > 1:
                    raise ValueError('Invalid CTI query parameters')
                limit = int(params.get('limit', ['10'])[0])
                return self.send(200, cti_search(params['q'][0], limit))
            except (ValueError, TypeError, KeyError) as exc:
                return self.send(400, {'error': str(exc)})
        if path=='/api/attribution':return self.send(200,credits())
        if path=='/healthz':return self.send(200,{'status':'ok','service':'SagaZ ZeRo','version':credits()['version']})
        if path=='/gateway/connectors':return self.send(200,{'entries':[{'name':'local','available':True,'kind':'preparation'},{'name':'openai_compatible','available':connection()['configured'],'kind':'optional_provider'}],'shell_enabled':False})
        if path=='/api/connection' and self.scope().connector!='local-ui':return self.send(403,{'error':'Sessão necessária'})
        if path=='/api/connection':return self.send(200,connection())
        if path in ('/v1/models','/gateway/capabilities','/gateway/audit/verify','/gateway/cost'):
            scope=self.scope()
            if scope.connector=='public':return self.send(403,{'error':'Sessão ou token de API necessário'})
            if path=='/v1/models':return self.send(200,self.server.gateway.models())
            if path=='/gateway/capabilities':return self.send(200,self.server.gateway.capability(scope))
            if path=='/gateway/audit/verify':return self.send(200,self.server.gateway.audit.verify())
            if path=='/gateway/cost':return self.send(200,self.server.gateway.cost.report())
        if path.startswith('/api/conversation/'):
            if self.scope().connector!='local-ui':return self.send(403,{'error':'Sessão necessária'})
            try:
                file=self.project(path.rsplit('/',1)[-1])/'conversation.json'
                if not file.is_file():return self.send(404,{'error':'Conversa não encontrada'})
                return self.send(200,json.loads(file.read_text(encoding='utf-8')))
            except ValueError:return self.send(400,{'error':'Projeto inválido'})
        if path=='/api/status':
            return self.send(200,{'name':'SagaZ ZeRo','persona':'HooLeeSheet','organization':'Systemia Solutions','version':(ROOT/'VERSION').read_text().strip(),'model_configured':bool(os.environ.get('DSANT_BASE_URL') and os.environ.get('DSANT_MODEL')),'default_mode':'local_preparation','shell':False,'sources':len(CORE.registry()['entries'])})
        if path=='/api/integrations' and self.scope().connector!='local-ui':return self.send(403,{'error':'Sessão necessária'})
        if path=='/api/integrations':return self.send(200,json.loads((ROOT/'knowledge/integrations.json').read_text(encoding='utf-8')))
        if path=='/api/sources' and self.scope().connector!='local-ui':return self.send(403,{'error':'Sessão necessária'})
        if path=='/api/sources':return self.send(200,CORE.registry())
        if path=='/api/projects':
            if self.scope().connector!='local-ui':return self.send(403,{'error':'Sessão necessária'})
            rows=[]
            for folder in sorted(self.server.state_root.glob('*'),key=lambda p:p.name):
                if folder.is_symlink():continue
                if (folder/'campaign.json').is_file():
                    try:
                        cfg=CORE.read(folder/'campaign.json');rows.append(dict(id=folder.name,brief=cfg['brief'],niche=cfg['niche'],task=cfg['task'],created_at=cfg['created_at'],conversation=(folder/'conversation.json').is_file()))
                    except (ValueError,OSError,KeyError):continue
            return self.send(200,rows)
        if path.startswith('/api/context/'):
            if self.scope().connector!='local-ui':return self.send(403,{'error':'Sessão necessária'})
            try:
                file=self.project(path.split('/')[-1])/'context.md'
                if not file.is_file():return self.send(404,{'error':'Contexto não encontrado'})
                return self.send(200,file.read_bytes(),'text/markdown; charset=utf-8')
            except ValueError:return self.send(400,{'error':'Projeto inválido'})
        return self.send(404,{'error':'Rota não encontrada'})
    def do_POST(self):
        if not self.valid_host():return self.send(421,{'error':'Host não permitido'})
        origin=self.headers.get('Origin')
        if origin and origin!='http://'+self.headers.get('Host',''):return self.send(403,{'error':'Origem não permitida'})
        scope=self.scope()
        if scope.connector=='public':return self.send(403,{'error':'Abra a interface local ou use um token de API configurado'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send(415,{'error':'JSON obrigatório'})
        try:length=int(self.headers.get('Content-Length','0'))
        except ValueError:return self.send(400,{'error':'Tamanho inválido'})
        if not 1<=length<=32768:return self.send(413,{'error':'Pedido excede o limite'})
        if not self.server.busy.acquire(blocking=False):return self.send(429,{'error':'Duas tarefas em andamento; tente novamente após terminar'})
        try:
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise ValueError('Corpo JSON inválido')
            if self.path in ('/api/chat','/api/research') and scope.connector!='local-ui':
                raise Denied('Somente sessão local pode preparar tarefas ou pesquisar')
            if self.path=='/api/chat':
                result=prepare_task(data.get('brief'),data.get('niche','general'),data.get('method','cinematic-3d'),data.get('use_model',False),self.server.state_root,parent_id=data.get('parent_id'))
            elif self.path=='/api/research':result=research(data.get('url',''),self.server.state_root)
            elif self.path=='/v1/chat/completions':result=self.server.gateway.chat(scope,data)
            elif self.path=='/mcp':result=self.server.gateway.mcp(scope,data)
            elif self.path=='/gateway/skills/select':result=self.server.gateway.select(scope,data)
            else:return self.send(404,{'error':'Rota não encontrada'})
            return self.send(200,result if result is not None else {})
        except Denied as exc:return self.send(402,{'error':{'message':str(exc)}})
        except ProviderUnavailable as exc:return self.send(503,{'error':str(exc)})
        except (ValueError,TypeError,KeyError,ProtocolError) as exc:return self.send(400,{'error':str(exc)})
        except Exception as exc:return self.send(500,{'error':'Falha em '+type(exc).__name__+'; confira configuração e arquivos locais'})
        finally:self.server.busy.release()


def serve(port=8080,state_root=None,host=None):
    host = host or ('0.0.0.0' if os.environ.get('SAGAZ_BIND_ALL') == '1' else '127.0.0.1')
    if host not in ('127.0.0.1','0.0.0.0'):
        raise ValueError('Host não permitido')
    if host == '0.0.0.0' and os.environ.get('SAGAZ_BIND_ALL') != '1':
        raise ValueError('Defina SAGAZ_BIND_ALL=1 explicitamente para expor todas as interfaces')
    with Server((host,port),state_root) as server:
        print(f'SagaZ ZeRo · http://127.0.0.1:{server.server_port} · modo local por padrão',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass


def cli(use_model=False):
    blue='\033[38;5;39m' if sys.stdout.isatty() else ''
    reset='\033[0m' if blue else ''
    print(blue+'SagaZ · Console azul · digite sair para encerrar'+reset)
    while True:
        try:brief=input(blue+'SagaZ > '+reset).strip()
        except (EOFError,KeyboardInterrupt):break
        if brief.casefold() in ('sair','exit','quit'):break
        if not brief:continue
        try:print(prepare_task(brief,use_model=use_model)['answer'])
        except (ValueError,OSError) as exc:print('Erro:',exc)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--web',action='store_true');parser.add_argument('--port',type=int,default=8080);parser.add_argument('--use-model',action='store_true');a=parser.parse_args()
    serve(a.port) if a.web else cli(a.use_model)
