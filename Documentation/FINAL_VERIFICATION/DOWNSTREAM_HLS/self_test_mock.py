"""Execute fixture-server plumbing on loopback. This does NOT execute MarufYT."""
from pathlib import Path
import argparse, http.client, json, shutil, ssl, subprocess, tempfile, threading
from urllib.parse import urlsplit
from mock_hls_server import Config, make_servers, AUTH_FIXTURE, COOKIE_FIXTURE

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--openssl',default=shutil.which('openssl') or r'C:\Program Files\Git\usr\bin\openssl.exe')
    p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args();args.output_dir.mkdir(exist_ok=False)
    checks=0
    def check(condition):
        nonlocal checks
        checks+=1
        assert condition,'Fixture check '+str(checks)+' failed'
    with tempfile.TemporaryDirectory(prefix='marufyt-hls-fixture-') as temp:
        root=Path(temp)
        def openssl(*cmd):subprocess.run([args.openssl,*cmd],cwd=root,check=True,capture_output=True)
        openssl('req','-x509','-newkey','rsa:2048','-sha256','-nodes','-keyout','ca.key','-out','ca.crt','-days','2',
                '-subj','/CN=MarufYT HLS fixture CA','-addext','basicConstraints=critical,CA:TRUE',
                '-addext','keyUsage=critical,keyCertSign,cRLSign')
        openssl('req','-newkey','rsa:2048','-nodes','-keyout','server.key','-out','server.csr','-subj','/CN=a.hls.test')
        (root/'leaf.ext').write_text('subjectAltName=DNS:a.hls.test,DNS:b.hls-other.test,IP:127.0.0.1\nbasicConstraints=CA:FALSE\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n')
        openssl('x509','-req','-in','server.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial',
                '-out','server.crt','-days','2','-sha256','-extfile','leaf.ext')
        # Deliberately not playable video: these tests verify routing/TLS only.
        (root/'owned.m3u8').write_text('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:2\n#EXT-X-MEDIA-SEQUENCE:0\n#EXTINF:2.0,\nseg000.ts\n#EXT-X-ENDLIST\n')
        (root/'seg000.ts').write_bytes(b'NONPLAYABLE SYNTHETIC TRANSPORT FIXTURE')
        cfg=Config(root,args.output_dir/'MOCK_REQUESTS.jsonl',http_port=0,https_port=0)
        servers=make_servers(cfg,root/'server.crt',root/'server.key')
        for s in servers:threading.Thread(target=s.serve_forever,daemon=True).start()
        context=ssl.create_default_context(cafile=str(root/'ca.crt'))
        def get(path,secure=True,host=None,credentials=False):
            cls=http.client.HTTPSConnection if secure else http.client.HTTPConnection
            kwargs={'context':context} if secure else {}
            c=cls('127.0.0.1',cfg.https_port if secure else cfg.http_port,timeout=5,**kwargs)
            headers={'Host':host or cfg.a}
            if credentials:headers.update(Authorization=AUTH_FIXTURE,Cookie=COOKIE_FIXTURE)
            c.request('GET',path,headers=headers);r=c.getresponse();body=r.read()
            result=r.status,dict(r.getheaders()),body;c.close();return result
        try:
            for secure in (False,True):
                check(get('/case/P00/master.m3u8',secure)[0]==200)
            check(get('/case/P00/child.m3u8')[0]==200)
            check(get('/case/P00/seg000.ts')[2].startswith(b'NONPLAYABLE'))
            variants={'P01':('master.m3u8','http://'),'P02':('child.m3u8','http://'),
                'P03':('master.m3u8',cfg.b),'P04':('child.m3u8',cfg.b),
                'P05':('master.m3u8','fixture:dummy@'),'P06':('child.m3u8','fixture:dummy@'),
                'P07':('master.m3u8',':444/'),'P08':('child.m3u8',':444/'),
                'P09':('master.m3u8','bad_host.invalid'),'P10':('child.m3u8','bad_host.invalid')}
            for case,(name,literal) in variants.items():
                status,headers,body=get('/case/'+case+'/'+name)
                check(status==200 and literal.encode() in body)
            redirects={'R01':('master.m3u8','https',cfg.a),'R02':('master.m3u8','http',cfg.a),
                'R03':('master.m3u8','https',cfg.b),'R04':('child.m3u8','http',cfg.a),
                'R05':('seg000.ts','http',cfg.a),'R06':('child.m3u8','https',cfg.b),
                'R07':('seg000.ts','https',cfg.b),'R08':('master.m3u8','http',cfg.b),
                'R09':('master.m3u8','https',cfg.a)}
            for case,(resource,scheme,host) in redirects.items():
                for code in (301,302,303,307,308):
                    status,headers,body=get('/case/'+case+'/'+resource+'?code='+str(code))
                    target=urlsplit(headers['Location'])
                    check(status==code and target.scheme==scheme and target.hostname==host)
            status,headers,body=get('/case/R03/master.m3u8',credentials=True)
            check(headers.get('Set-Cookie','').startswith(COOKIE_FIXTURE))
            target=urlsplit(headers['Location'])
            # Explicit safe/unsafe controls calibrate the logger, not client policy.
            get(target.path,host=cfg.b,credentials=False)
            get(target.path,host=cfg.b,credentials=True)
            check(cfg.events[-3]['authorizationFixtureSeen'] and cfg.events[-3]['cookieFixtureSeen'])
            check(not cfg.events[-2]['authorizationPresent'] and not cfg.events[-2]['cookiePresent'])
            check(cfg.events[-1]['authorizationFixtureSeen'] and cfg.events[-1]['cookieFixtureSeen'])
            check(get('/case/P00/master.m3u8?ignored_token=synthetic-do-not-log')[0]==200)
            log=cfg.log.read_text()
            check(AUTH_FIXTURE not in log and COOKIE_FIXTURE not in log and 'synthetic-do-not-log' not in log)
            check(get('/../private.key')[0]==404)
        finally:
            for s in servers:s.shutdown();s.server_close()
        result={'status':'PASS','checks':checks,'requests':len(cfg.events),'networkScope':'127.0.0.1 only',
            'certificateValidation':'enabled; temporary CA trusted only by this client',
            'credentials':'synthetic markers only','mockRedirectFollowing':'manual safe/unsafe logger calibration',
            'media':'intentionally nonplayable transport bytes; not a playback test',
            'applicationExecuted':False,'MarufYTPolicyExecuted':False,'iPhoneTested':False,
            'keysAndCertificates':'temporary directory removed after run'}
    (args.output_dir/'SELF_TEST_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
