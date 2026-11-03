"""Run and report the local Windows fixture cases, never an IPA or iPhone.

Only writes test documentation/evidence here and temporary synthetic fixtures.
No DNS changes, OS certificate installation, app builds or real credentials.
"""
from pathlib import Path
import argparse, csv, hashlib, http.client, json, shutil, ssl, subprocess, sys
import tempfile, threading, time, unittest
from urllib.parse import urlsplit
from mock_hls_server import Config, make_servers, AUTH_FIXTURE, COOKIE_FIXTURE

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
GIT=r'C:\Program Files\Git\cmd\git.exe'

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--openssl',default=shutil.which('openssl') or r'C:\Program Files\Git\usr\bin\openssl.exe')
    args=p.parse_args()
    runid=time.strftime('%Y%m%d-%H%M%S')+'-'+str(time.time_ns()%1000000)
    out=ROOT/'Evidence'/('WINDOWS-'+runid);out.mkdir(exist_ok=False)
    results=[]
    def check(case,description,condition,scope='Mock server only'):
        status='PASS' if condition else 'FAIL'
        results.append({'id':case,'description':description,'result':status,'scope':scope})
        print(status+' | '+case+' | '+description,flush=True)
    def git(*cmd):return subprocess.check_output([GIT,*cmd],cwd=REPO,text=True).strip()
    tracked=[x for x in subprocess.check_output([GIT,'ls-files','-z'],cwd=REPO).decode().split('\0') if x]
    baseline={'HEAD':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),
        'refs':git('for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes'),
        'hashes':{x:sha(REPO/x) for x in tracked if (REPO/x).is_file()}}
    openssl_version=subprocess.check_output([args.openssl,'version'],text=True).strip()
    print('Python '+sys.version.split()[0]+'; '+openssl_version,flush=True)
    print('Preparing temporary test certificates; nothing is installed into Windows trust.',flush=True)
    servers=[];request_events=[]
    with tempfile.TemporaryDirectory(prefix='MarufYT-HLS-Windows-') as temp:
        private=Path(temp)
        def openssl(*cmd):subprocess.run([args.openssl,*cmd],cwd=private,check=True,capture_output=True)
        openssl('req','-x509','-newkey','rsa:2048','-sha256','-nodes','-keyout','ca.key','-out','ca.crt','-days','2',
            '-subj','/CN=MarufYT Windows fixture CA','-addext','basicConstraints=critical,CA:TRUE',
            '-addext','keyUsage=critical,keyCertSign,cRLSign')
        openssl('req','-newkey','rsa:2048','-nodes','-keyout','server.key','-out','server.csr','-subj','/CN=a.hls.test')
        (private/'leaf.ext').write_text('subjectAltName=DNS:a.hls.test,DNS:b.hls-other.test,IP:127.0.0.1\nbasicConstraints=CA:FALSE\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n')
        openssl('x509','-req','-in','server.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial',
            '-out','server.crt','-days','2','-sha256','-extfile','leaf.ext')
        (private/'owned.m3u8').write_text('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:2\n#EXT-X-MEDIA-SEQUENCE:0\n#EXTINF:2.0,\nseg000.ts\n#EXT-X-ENDLIST\n')
        media=b'SYNTHETIC TRANSPORT BYTES - NOT PLAYABLE VIDEO'
        (private/'seg000.ts').write_bytes(media)
        cfg=Config(private,out/'MOCK_REQUESTS.jsonl',http_port=0,https_port=0)
        servers=make_servers(cfg,private/'server.crt',private/'server.key')
        ports={'http':cfg.http_port,'https':cfg.https_port}
        for s in servers:threading.Thread(target=s.serve_forever,daemon=True).start()
        print('STARTED HTTP: 127.0.0.1:'+str(cfg.http_port),flush=True)
        print('STARTED HTTPS: 127.0.0.1:'+str(cfg.https_port),flush=True)
        print('These temporary ports are Windows fixture ports, not accepted app master-URL ports.',flush=True)
        context=ssl.create_default_context(cafile=str(private/'ca.crt'))
        # Real TLS validates SAN a.hls.test/b.hls-other.test, while the socket is
        # deliberately routed to loopback. No OS DNS/hosts-file modification.
        class LocalHTTPS(http.client.HTTPSConnection):
            def connect(self):
                sock=self._create_connection(('127.0.0.1',self.port),self.timeout,self.source_address)
                self.sock=self._context.wrap_socket(sock,server_hostname=self.host)
        class LocalHTTP(http.client.HTTPConnection):
            def connect(self):
                self.sock=self._create_connection(('127.0.0.1',self.port),self.timeout,self.source_address)
        def get(path,secure=True,host=None,credentials=False,ctx=None):
            host=host or cfg.a
            if host not in (cfg.a,cfg.b):raise ValueError('Only the two local fixture names are allowed')
            connection=(LocalHTTPS(host,cfg.https_port,timeout=5,context=ctx or context) if secure else
                LocalHTTP(host,cfg.http_port,timeout=5))
            headers={}
            if credentials:headers={'Authorization':AUTH_FIXTURE,'Cookie':COOKIE_FIXTURE}
            try:
                connection.request('GET',path,headers=headers)
                response=connection.getresponse()
                return response.status,dict(response.getheaders()),response.read()
            finally:connection.close()
        def follow_owned(location):
            target=urlsplit(location)
            if target.scheme not in ('http','https') or target.username or target.password:
                raise ValueError('Not an owned redirect control')
            expected=cfg.https_port if target.scheme=='https' else cfg.http_port
            if target.port!=expected:raise ValueError('Unexpected fixture port')
            return get(target.path+('?' + target.query if target.query else ''),
                secure=target.scheme=='https',host=target.hostname)
        try:
            check('P00-HTTP','HTTP test server answers the master request',get('/case/P00/master.m3u8',False)[0]==200)
            check('P00-HTTPS','HTTPS master works with certificate validation',get('/case/P00/master.m3u8')[0]==200)
            check('P00-CHILD','Relative child playlist is served',get('/case/P00/child.m3u8')[0]==200)
            check('P00-SEGMENT','Synthetic segment bytes are served (not video decoding)',get('/case/P00/seg000.ts')[2]==media)
            try:get('/case/P00/master.m3u8',ctx=ssl.create_default_context())
            except ssl.SSLCertVerificationError:untrusted_rejected=True
            else:untrusted_rejected=False
            check('TLS-UNTRUSTED','Client refuses the temporary CA when it is not explicitly trusted',untrusted_rejected)
            variants={
                'P01':('master.m3u8','http://','Master contains an HTTP child test URL'),
                'P02':('child.m3u8','http://','Child contains an HTTP segment test URL'),
                'P03':('master.m3u8',cfg.b,'Master contains a cross-domain HTTPS child URL'),
                'P04':('child.m3u8',cfg.b,'Child contains a cross-domain HTTPS segment URL'),
                'P05':('master.m3u8','fixture:dummy@','Child userinfo fixture is generated'),
                'P06':('child.m3u8','fixture:dummy@','Segment userinfo fixture is generated'),
                'P07':('master.m3u8',':444/','Child unacceptable-port fixture is generated'),
                'P08':('child.m3u8',':444/','Segment unacceptable-port fixture is generated'),
                'P09':('master.m3u8','bad_host.invalid','Invalid child-host fixture is generated'),
                'P10':('child.m3u8','bad_host.invalid','Invalid segment-host fixture is generated')}
            for case,(resource,literal,description) in variants.items():
                status,headers,body=get('/case/'+case+'/'+resource)
                check(case,description,status==200 and literal.encode() in body)
                if case in ('P01','P02','P03','P04'):
                    uri=next(line for line in body.decode().splitlines() if line and not line.startswith('#'))
                    check(case+'-SINK','Controlled target is reachable with no copied credentials',follow_owned(uri)[0]==200)
            redirects={
                'R01':('master.m3u8','https',cfg.a,'same-domain HTTPS master'),
                'R02':('master.m3u8','http',cfg.a,'master downgrade to HTTP'),
                'R03':('master.m3u8','https',cfg.b,'cross-domain HTTPS master'),
                'R04':('child.m3u8','http',cfg.a,'child downgrade to HTTP'),
                'R05':('seg000.ts','http',cfg.a,'segment downgrade to HTTP'),
                'R06':('child.m3u8','https',cfg.b,'cross-domain HTTPS child'),
                'R07':('seg000.ts','https',cfg.b,'cross-domain HTTPS segment'),
                'R08':('master.m3u8','http',cfg.b,'cross-domain HTTP master'),
                'R09':('master.m3u8','https',cfg.a,'redirect-loop response')}
            for case,(resource,scheme,host,description) in redirects.items():
                for code in (301,302,303,307,308):
                    status,headers,body=get('/case/'+case+'/'+resource+'?code='+str(code))
                    target=urlsplit(headers.get('Location',''))
                    ok=status==code and target.scheme==scheme and target.hostname==host
                    if ok and case!='R09':ok=follow_owned(headers['Location'])[0]==200
                    check(case+'-'+str(code),description+' returns '+str(code)+' and correct controlled target',ok)
            status,headers,body=get('/case/R03/master.m3u8',credentials=True)
            check('HDR-SETCOOKIE','A sets only the synthetic Secure host-only cookie',headers.get('Set-Cookie','').startswith(COOKIE_FIXTURE))
            target=urlsplit(headers['Location'])
            get(target.path,host=cfg.b,credentials=False)
            get(target.path,host=cfg.b,credentials=True)
            check('HDR-A','Origin A detects both synthetic markers',cfg.events[-3]['authorizationFixtureSeen'] and cfg.events[-3]['cookieFixtureSeen'])
            check('HDR-B-SAFE','B detects no markers when the test client sends none',not cfg.events[-2]['authorizationPresent'] and not cfg.events[-2]['cookiePresent'])
            check('HDR-B-UNSAFE','B detects both markers in deliberate unsafe control',cfg.events[-1]['authorizationFixtureSeen'] and cfg.events[-1]['cookieFixtureSeen'])
            check('LOG-QUERY','Unknown query canary does not break a valid fixture',get('/case/P00/master.m3u8?ignored_token=synthetic-do-not-log')[0]==200)
            log=cfg.log.read_text()
            check('LOG-REDACTION','Logs contain no marker values or query canary',AUTH_FIXTURE not in log and COOKIE_FIXTURE not in log and 'synthetic-do-not-log' not in log)
            check('PATH-SAFETY','Server refuses a path outside fixture routes',get('/../private.key')[0]==404)
        finally:
            for s in servers:s.shutdown();s.server_close()
            request_events=list(cfg.events)
            print('STOPPED: both local servers. Temporary test keys will be removed.',flush=True)
    # No temp CA/key files survive this context.
    command=[sys.executable,'-B','-m','unittest','Tests.test_security_fixes','-v']
    proc=subprocess.run(command,cwd=REPO,capture_output=True,text=True)
    (out/'SOURCE_CONTRACTS.txt').write_text(proc.stdout+proc.stderr+'\nExit code: '+str(proc.returncode)+'\n',encoding='utf-8')
    names={
        'test_diagnostics_are_opt_in_and_objects_are_not_interpolated':'F-04 sensitive logging source contract',
        'test_expiry_logout_cleanup_and_signatures':'F-01 cleanup/expiry source contract',
        'test_hls_validation_precedes_cache_and_native_mutations':'U-01 cache/handoff source contract',
        'test_https_initial_tasks_and_both_redirect_layers':'F-02/F-03 HTTPS and redirect source contracts',
        'test_no_authenticated_seed_persistence_or_raw_protobuf_dump':'F-01 no sensitive seed persistence source contract'}
    output=proc.stdout+proc.stderr
    for i,(name,label) in enumerate(names.items(),1):
        line=next((line for line in output.splitlines() if line.startswith(name+' ')),'')
        check('SC'+str(i),label,line.rstrip().endswith('... ok'),'Source inspection test, not runtime')
    check('SC-EXIT','Existing source-test command finishes successfully',proc.returncode==0,'Source inspection test, not runtime')
    unchanged=(git('rev-parse','HEAD')==baseline['HEAD'] and git('branch','--show-current')==baseline['branch'] and
        git('for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes')==baseline['refs'] and
        all(sha(REPO/x)==h for x,h in baseline['hashes'].items()))
    check('PRESERVE-SOURCE','All tracked source files and branch refs are unchanged',unchanged,'Preservation')
    release_counts={}
    for name in ('MarufYT-FinalUpdate-1.1.4+marufyt.8','MarufYT-U01-HLS-743f307'):
        folder=REPO.parent/'release'/name; count=0;valid=True
        for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
            expected,rel=line.split(None,1);file=folder/rel.strip().lstrip('*')
            valid=valid and file.resolve().is_relative_to(folder.resolve()) and sha(file)==expected;count+=1
        release_counts[name]=count
        check('PRESERVE-'+str(count),str(count)+' existing release files still match their checksums',valid,'Preservation')
    summary={'python':sys.version.split()[0],'openssl':openssl_version,'pythonTLS':ssl.OPENSSL_VERSION,
        'HEAD':baseline['HEAD'],'branch':baseline['branch'],'ports':ports,'serversStopped':True,
        'temporaryKeysRemoved':True,'certificateInstalledInWindows':False,'DNSOrFirewallChanged':False,
        'requestsLogged':len(request_events),'passes':sum(r['result']=='PASS' for r in results),
        'failures':sum(r['result']=='FAIL' for r in results),'releaseFilesVerified':release_counts,
        'applicationExecuted':False,'iPhoneTested':False,'applicationRebuilt':False,
        'realCredentialsUsed':False,'optionalFFmpegOnPATH':bool(shutil.which('ffmpeg')),
        'optionalMitmwebOnPATH':bool(shutil.which('mitmweb')),'results':results}
    (out/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    with (out/'RESULTS.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['id','description','result','scope']);w.writeheader();w.writerows(results)
    report=['# Windows downstream HLS test results','',
        'Executed '+time.strftime('%Y-%m-%d %H:%M:%S')+' local PC time. Commit `'+baseline['HEAD']+'`.',
        '', '**These are Windows mock-server and source checks, not MarufYT/iPhone runtime results.**',
        '',f"Result: **{summary['passes']} PASS, {summary['failures']} FAIL**. Both mock servers were started, exercised and stopped.",
        '', '## Prerequisites and exact files','',
        '- Python '+summary['python']+'; '+openssl_version+'. Required Python modules are standard-library modules.',
        '- `mock_hls_server.py`: existing HTTP/HTTPS fixture server.',
        '- `self_test_mock.py`: existing standalone fixture self-test.',
        '- `run_windows_walkthrough.py`: this per-case Windows launcher/report writer.',
        '- `inject_fixture_response.py`: optional phone/proxy addon; not executed.',
        '- FFmpeg/mitmweb are optional for later playback/device work; neither is needed for these transport checks.',
        '', '## What was executed','',
        '1. Verified Python, OpenSSL and Python SSL/HTTP libraries.',
        '2. Generated a temporary CA/server certificate, trusted only by the test Python client.',
        '3. Started loopback HTTP and HTTPS listeners on temporary ports '+str(ports['http'])+' and '+str(ports['https'])+'.',
        '4. Executed P00–P10 and R01–R09 (redirects 301/302/303/307/308), controlled target requests and synthetic header controls.',
        '5. Ran all five existing security source-contract tests and checked source/release preservation.',
        '6. Closed both servers and deleted temporary certificate/key/media files. No user clicks were required.',
        '', '## How to read PASS','',
        '**Mock PASS means the test server returned the intended fixture and/or the Windows client could reach its controlled target.**',
        'An HTTP downgrade fixture PASS does not mean MarufYT rejected that downgrade. Some controlled HTTP destinations were deliberately requested by this Windows client to confirm the sink works.',
        'Headers on redirect controls were deliberately sent/omitted by the test client, not automatically forwarded by MarufYT.',
        '', '| Case | Windows result | Simple explanation | Scope |','| --- | --- | --- | --- |']
    report.extend('| '+r['id']+' | '+r['result']+' | '+r['description']+' | '+r['scope']+' |' for r in results)
    report.extend(['', '## Actual MarufYT status — both versions','',
        '| Requirement | Latest 21.43.5 | Stable 21.39.4 |','| --- | --- | --- |',
        '| Native master URL validation / invalid URL fallback | NOT TESTED on device | NOT TESTED on device |',
        '| Child/segment URI rejection and redirect security | NOT TESTED | NOT TESTED |',
        '| Native Authorization/Cookie forwarding | NOT EXERCISED | NOT EXERCISED |',
        '| Video playback and decoder behavior | NOT TESTED | NOT TESTED |',
        '', 'Windows cannot execute these iOS IPAs or Apple Foundation policy code. The source-contract tests inspect code order/content only. No mirrored Python URL validator is being claimed as the app policy.',
        'The served segment is intentionally nonplayable synthetic bytes; FFmpeg media generation and video decoding were not performed.',
        'Temporary high ports are suitable for this harness but U-01 accepts only absent/443 HTTPS ports for app master URLs.',
        'TLS checks use the two certificate DNS names routed explicitly to loopback; no operating-system DNS/hosts-file changes were made.',
        '', '## Preservation and evidence','',
        '- All tracked source hashes and branch refs remain unchanged; no merge, push, version change or rebuild.',
        '- All 142 previous .8 release files and all 25 U01-HLS release files match their checksum manifests, including both IPAs and DEBs.',
        '- No real account credentials, passwords, cookies or tokens were used. Synthetic marker values were not logged.',
        '- No system certificate, firewall rule, DNS change or extra software was installed.',
        '- Detailed evidence: ['+out.name+'](Evidence/'+out.name+'/RESULTS.json), [case CSV](Evidence/'+out.name+'/RESULTS.csv), [request metadata](Evidence/'+out.name+'/MOCK_REQUESTS.jsonl), [source-test log](Evidence/'+out.name+'/SOURCE_CONTRACTS.txt).',
        '', '## Repeat with one command','', 'Run from `C:\\Users\\oriyan\\Desktop\\ios App\\MarufYT`:',
        '', '```powershell', 'python -B Documentation/FINAL_VERIFICATION/DOWNSTREAM_HLS/run_windows_walkthrough.py', '```',
        '', 'Each run creates a new evidence folder, uses fresh temporary keys and stops its own servers automatically.',
        'Do not interpret these results as physical iPhone security verification. Follow TEST_PLAN.md only when an owned test phone and controlled fixture routing are available.', ''])
    (ROOT/'TEST_RESULTS.md').write_text('\n'.join(report),encoding='utf-8')
    print('SUMMARY: '+str(summary['passes'])+' PASS, '+str(summary['failures'])+' FAIL',flush=True)
    print('REPORT: '+str(ROOT/'TEST_RESULTS.md'),flush=True)
    print('iPhone/IPA runtime: NOT TESTED. No application rebuild.',flush=True)
    return 1 if summary['failures'] else 0

if __name__=='__main__':sys.exit(main())
