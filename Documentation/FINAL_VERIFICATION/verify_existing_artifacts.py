"""Verification only: reads releases/source; writes this report's Evidence only."""
from pathlib import Path
import hashlib, json, plistlib, struct, subprocess, sys, zipfile
sys.dont_write_bytecode = True
OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]
WORK=REPO.parent
sys.path.insert(0,str(REPO/'Tools'))
import marufyt_package as pkg
GIT=r'C:\Program Files\Git\cmd\git.exe'
def git(*args):return subprocess.check_output([GIT,*args],cwd=REPO,text=True).strip()
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
release=WORK/'release/MarufYT-U01-HLS-743f307'
original=WORK/'release/MarufYT-FinalUpdate-1.1.4+marufyt.8'
before=json.loads((OUT/'Evidence/STATE_BEFORE.json').read_text())
ci=json.loads((release/'CI_RESULT.json').read_text())
assert ci['headSha']==before['HEAD']=='743f307b816d275fef88d34a36ba546415015753'
assert ci['conclusion']=='success' and all(j['conclusion']=='success' for j in ci['jobs'])
checks={'sourceCommit':before['HEAD'],'branch':before['branch'],'existingCI':{'url':ci['url'],'conclusion':ci['conclusion'],'headSha':ci['headSha'],'reusedNotRerun':True},'manifests':{},'packages':{}}
for root in (original,release):
    rows=[]
    for line in (root/'SHA256SUMS.txt').read_text().splitlines():
        expected,name=line.split(None,1); name=name.strip().lstrip('*'); path=root/name
        assert path.resolve().is_relative_to(root.resolve())
        assert sha(path)==expected,(root,name)
        rows.append({'file':name,'sha256':expected})
    checks['manifests'][root.name]={'verifiedFiles':len(rows),'allMatch':True,'manifestSHA256':sha(root/'SHA256SUMS.txt')}
    (OUT/'Evidence'/f'{root.name}_HASHES.json').write_text(json.dumps(rows,indent=2)+'\n')
baseline=json.loads((REPO/'Documentation/FINAL_UPDATE/URL_NETWORK_EVIDENCE/INPUTS.json').read_text())
packages=json.loads((release/'PACKAGE_VERIFICATION.json').read_text())
expected_dylib=hashlib.sha256((release/'CI-Artifact/MarufYT.dylib').read_bytes()).hexdigest()
for build,item in packages['builds'].items():
    path=Path(item['path']); old=WORK/baseline[build]['path']; assert sha(path)==item['sha256']
    assert sha(old)==baseline[build]['sha256']
    with zipfile.ZipFile(path) as z,zipfile.ZipFile(old) as o:
        assert z.testzip() is None and o.testzip() is None
        assert z.namelist()==o.namelist() and len(z.namelist())==len(set(z.namelist()))
        changed=[n for n in z.namelist() if z.read(n)!=o.read(n)]
        member='Payload/YouTube.app/Frameworks/MarufYT.dylib'
        assert changed==[member]
        dylib=z.read(member); assert hashlib.sha256(dylib).hexdigest()==expected_dylib
        assert struct.unpack_from('<II',dylib)==(0xfeedfacf,0x0100000c)
        info=plistlib.loads(z.read('Payload/YouTube.app/Info.plist'))
        assert info['CFBundleIdentifier']=='com.google.ios.youtube'
        assert info['CFBundleShortVersionString']==item['hostVersion']
        assert pkg.loads(z.read('Payload/YouTube.app/'+info['CFBundleExecutable'])).count(pkg.LOAD)==1
        assert pkg.loads(dylib)==pkg.loads(o.read(member))
        usage={k:v for k,v in info.items() if k.endswith('UsageDescription')}
        checks['packages'][build]={'path':str(path),'sha256':item['sha256'],'ZIPCRC':'PASS','hostVersion':item['hostVersion'],
            'bundleID':info['CFBundleIdentifier'],'dylibSHA256':expected_dylib,'dylibArchitecture':'arm64',
            'onlyChangedMemberFromOriginal8':changed,'dependencyLoadsUnchanged':True,'usageDescriptions':usage,
            'ATS':info.get('NSAppTransportSecurity'),'backgroundModes':info.get('UIBackgroundModes'),
            'runtime':'NOT TESTED','signing':'Signing required; no signed installation tested'}
olddeb=pkg.deb_files(next((original/'CI-Artifact').glob('*.deb')))
newdeb=pkg.deb_files(next((release/'CI-Artifact').glob('*.deb')))
key=pkg.DEB_PREFIX+pkg.DYLIB
assert {k:v for k,v in olddeb.items() if k!=key}=={k:v for k,v in newdeb.items() if k!=key}
assert hashlib.sha256(newdeb[key]).hexdigest()==expected_dylib
checks['nonDylibDEBPayloadUnchanged']=True
assert git('rev-parse','HEAD')==before['HEAD']
assert git('branch','--show-current')==before['branch']
assert git('for-each-ref','--format=%(refname) %(objectname)','refs/heads','refs/remotes')==before['refs']
changed=[p for p,h in before['trackedHashes'].items() if hashlib.sha256((REPO/p).read_bytes()).hexdigest()!=h]
assert not changed
assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
checks['preservation']={'HEADUnchanged':True,'branchAndAllLocalRemoteRefsUnchanged':True,'trackedFilesChanged':changed,'rebuildPerformed':False,'newWorkflowTriggered':False,'networkCapturePerformed':False}
(OUT/'Evidence/ARTIFACT_AND_STATE_VERIFICATION.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({k:v for k,v in checks.items() if k!='packages'},indent=2))
