"""Local HLS transport fixtures only. Never connects to YouTube or upstream hosts.

Logs header presence/fixture matches, never header values, queries or client IPs.
Real playback requires an independently generated owned media directory.
"""
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse, json, re, ssl, threading, time
from urllib.parse import parse_qs, urlsplit

CASES = {'P00','P01','P02','P03','P04','P05','P06','P07','P08','P09','P10',
         'R01','R02','R03','R04','R05','R06','R07','R08','R09'}
AUTH_FIXTURE = 'Bearer HLS-FIXTURE-ONLY'
COOKIE_FIXTURE = 'hls_fixture=fixture-only'

@dataclass
class Config:
    media: Path
    log: Path
    a: str = 'a.hls.test'
    b: str = 'b.hls-other.test'
    http_port: int = 8080
    https_port: int = 8443
    events: list = field(default_factory=list)
    lock: object = field(default_factory=threading.Lock)

    def origin(self, scheme='https', host=None):
        port = self.https_port if scheme == 'https' else self.http_port
        suffix = '' if port == (443 if scheme=='https' else 80) else ':'+str(port)
        return scheme+'://'+(host or self.a)+suffix

def make_servers(config, cert, key, bind='127.0.0.1'):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass

        def do_GET(self): self.respond(False)
        def do_HEAD(self): self.respond(True)

        def respond(self, head):
            parsed=urlsplit(self.path)
            match=re.fullmatch(r'/case/([PR]\d{2})/(master\.m3u8|final-master\.m3u8|child\.m3u8|final-child\.m3u8|seg\d{3}\.ts|final-seg\d{3}\.ts)',parsed.path)
            if not match or match[1] not in CASES:
                self.send_error(404); return
            case,name=match.groups()
            host=self.headers.get('Host','').split(':')[0].lower()
            host=host if host in (config.a, config.b) else 'other-host'
            raw_auth=self.headers.get('Authorization','')
            raw_cookie=self.headers.get('Cookie','')
            event={'relativeSeconds':round(time.monotonic()-started,3),'case':case,'resource':name,
                'host':host,'transport':'https' if isinstance(self.connection,ssl.SSLSocket) else 'http',
                'method':self.command,'authorizationPresent':bool(raw_auth),'cookiePresent':bool(raw_cookie),
                'authorizationFixtureSeen':raw_auth==AUTH_FIXTURE,
                'cookieFixtureSeen':COOKIE_FIXTURE in raw_cookie}
            with config.lock:
                config.events.append(event)
                with config.log.open('a',encoding='utf-8') as f:f.write(json.dumps(event)+'\n')
            try: code=int(parse_qs(parsed.query).get('code',['302'])[0])
            except ValueError: code=302
            if code not in (301,302,303,307,308): code=302
            origin=lambda scheme='https',h=None:config.origin(scheme,h)
            route=lambda n:'/case/'+case+'/'+n
            location=None
            if name=='master.m3u8':
                if case=='R01':location=origin()+route('final-master.m3u8')
                if case=='R02':location=origin('http')+route('final-master.m3u8')
                if case=='R03':location=origin(h=config.b)+route('final-master.m3u8')
                if case=='R08':location=origin('http',config.b)+route('final-master.m3u8')
                if case=='R09':location=origin()+route('master.m3u8')+'?code='+str(code)
            if name=='child.m3u8':
                if case=='R04':location=origin('http')+route('final-child.m3u8')
                if case=='R06':location=origin(h=config.b)+route('final-child.m3u8')
            if re.fullmatch(r'seg\d{3}\.ts',name):
                if case=='R05':location=origin('http')+route('final-'+name)
                if case=='R07':location=origin(h=config.b)+route('final-'+name)
            if location:
                self.send_response(code);self.send_header('Location',location)
                if host==config.a and isinstance(self.connection,ssl.SSLSocket):
                    self.send_header('Set-Cookie',COOKIE_FIXTURE+'; Path=/; Secure; HttpOnly; SameSite=Lax')
                self.send_header('Cache-Control','no-store');self.send_header('Content-Length','0')
                self.end_headers();return
            if name.endswith('master.m3u8'):
                child='child.m3u8?code='+str(code)
                if case=='P01':child=origin('http')+route('child.m3u8')
                if case=='P03':child=origin(h=config.b)+route('child.m3u8')
                if case=='P05':child=origin().replace('://','://fixture:dummy@')+route('child.m3u8')
                if case=='P07':child='https://'+config.a+':444'+route('child.m3u8')
                if case=='P09':child='https://bad_host.invalid'+route('child.m3u8')
                body=('#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=400000,RESOLUTION=320x180\n'+child+'\n').encode()
                content_type='application/vnd.apple.mpegurl'
            elif name.endswith('child.m3u8'):
                playlist=config.media/'owned.m3u8'
                if not playlist.is_file():self.send_error(503,'Generate owned media before playback tests');return
                lines=[]
                for line in playlist.read_text(encoding='utf-8').splitlines():
                    if line and not line.startswith('#'):
                        if not re.fullmatch(r'seg\d{3}\.ts',line):self.send_error(500,'Unexpected owned media filename');return
                        segment=line+'?code='+str(code)
                        if case=='P02':segment=origin('http')+route(line)
                        if case=='P04':segment=origin(h=config.b)+route(line)
                        if case=='P06':segment=origin().replace('://','://fixture:dummy@')+route(line)
                        if case=='P08':segment='https://'+config.a+':444'+route(line)
                        if case=='P10':segment='https://bad_host.invalid'+route(line)
                        line=segment
                    lines.append(line)
                body=('\n'.join(lines)+'\n').encode();content_type='application/vnd.apple.mpegurl'
            else:
                filename=name.removeprefix('final-')
                file=config.media/filename
                if not file.is_file():self.send_error(503,'Generate owned media before playback tests');return
                body=file.read_bytes();content_type='video/mp2t'
            self.send_response(200);self.send_header('Content-Type',content_type)
            self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)))
            if host==config.a and isinstance(self.connection,ssl.SSLSocket):
                self.send_header('Set-Cookie',COOKIE_FIXTURE+'; Path=/; Secure; HttpOnly; SameSite=Lax')
            self.end_headers()
            if not head:self.wfile.write(body)

    started=time.monotonic()
    http=ThreadingHTTPServer((bind,config.http_port),Handler)
    try:
        https=ThreadingHTTPServer((bind,config.https_port),Handler)
        ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.minimum_version=ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(str(cert),str(key));https.socket=ctx.wrap_socket(https.socket,server_side=True)
    except Exception:
        http.server_close();raise
    config.http_port=http.server_port;config.https_port=https.server_port
    return http,https

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cert',type=Path,required=True);p.add_argument('--key',type=Path,required=True)
    p.add_argument('--media-dir',type=Path,required=True);p.add_argument('--log',type=Path,required=True)
    p.add_argument('--bind',default='127.0.0.1');p.add_argument('--http-port',type=int,default=8080)
    p.add_argument('--https-port',type=int,default=8443)
    args=p.parse_args()
    if args.log.exists():p.error('Use a fresh log filename; existing logs are never overwritten')
    cfg=Config(args.media_dir,args.log,http_port=args.http_port,https_port=args.https_port)
    servers=make_servers(cfg,args.cert,args.key,args.bind)
    for s in servers:threading.Thread(target=s.serve_forever,daemon=True).start()
    print('Fixture server ready. Application U-01 accepts HTTPS 443 only; 8443 is harness-only.')
    print('No real credentials. No upstream fetch. Stop with Ctrl-C.')
    try:
        while True:time.sleep(1)
    except KeyboardInterrupt:pass
    finally:
        for s in servers:s.shutdown();s.server_close()

if __name__=='__main__':main()
