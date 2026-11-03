"""Package only a successful U-01 CI dylib, replacing exactly one IPA member."""
from pathlib import Path
import copy, hashlib, json, plistlib, struct, sys, zipfile
sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[3]
WORK = REPO.parent
sys.path.insert(0, str(REPO/'Tools'))
import marufyt_package as pkg
OUT = WORK/'release/MarufYT-U01-HLS-743f307'
EXPECTED = '743f307'  # Full SHA comes from successful CI, not an artifact filename.
OLD = WORK/'release/MarufYT-FinalUpdate-1.1.4+marufyt.8'

def sha(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

ci = json.loads((OUT/'CI_RESULT.json').read_text())
assert ci['conclusion']=='success' and ci['headSha'].startswith(EXPECTED)
assert all(j['conclusion']=='success' for j in ci['jobs'])
artifact = OUT/'CI-Artifact'
for line in (artifact/'SHA256SUMS.txt').read_text().splitlines():
    expected,name = line.split(None,1)
    assert sha(artifact/name.strip().lstrip('*')) == expected
deb = next(artifact.glob('*.deb'))
files = pkg.deb_files(deb)
oldfiles = pkg.deb_files(next((OLD/'CI-Artifact').glob('*.deb')))
dykey = pkg.DEB_PREFIX+pkg.DYLIB
assert {k:v for k,v in files.items() if k!=dykey} == {k:v for k,v in oldfiles.items() if k!=dykey}
dylib = files[dykey]
assert dylib == (artifact/'MarufYT.dylib').read_bytes()
assert struct.unpack_from('<I',dylib)[0] == 0xfeedfacf
assert struct.unpack_from('<I',dylib,4)[0] == 0x0100000c  # arm64
inputs = json.loads((REPO/'Documentation/FINAL_UPDATE/URL_NETWORK_EVIDENCE/INPUTS.json').read_text())
results = {'compiledCommit':ci['headSha'],'CI':ci['url'],'version':'1.1.4+marufyt.8',
           'buildLabel':'U01-HLS; separate rebuild, not an overwritten .8 release',
           'nonDylibDEBPayloadUnchanged':True,'deviceTests':'NOT TESTED','builds':{}}
for build,entry in inputs.items():
    src = WORK/entry['path']
    assert sha(src)==entry['sha256']
    version = '21.43.5' if build=='Latest' else '21.39.4'
    folder = OUT/(build+'-YouTube-'+version)
    folder.mkdir(exist_ok=False)
    target = folder/f'MarufYT-1.1.4+marufyt.8-U01-HLS-YouTube-{version}-ROOTLESS-signing-required.ipa'
    assert not target.exists()
    member = 'Payload/YouTube.app/Frameworks/MarufYT.dylib'
    with zipfile.ZipFile(src) as original:
        assert original.testzip() is None
        names=original.namelist(); assert len(names)==len(set(names)) and member in names
        assert pkg.loads(original.read(member))==pkg.loads(dylib)
        with zipfile.ZipFile(target,'x') as updated:
            for item in original.infolist():
                updated.writestr(copy.copy(item),dylib if item.filename==member else original.read(item))
        with zipfile.ZipFile(target) as updated:
            assert updated.testzip() is None and updated.namelist()==names
            changed=[n for n in names if original.read(n)!=updated.read(n)]
            assert changed==[member]
            info=plistlib.loads(updated.read('Payload/YouTube.app/Info.plist'))
            assert info['CFBundleIdentifier']=='com.google.ios.youtube'
            assert info['CFBundleShortVersionString']==version
            loads=pkg.loads(updated.read('Payload/YouTube.app/'+info['CFBundleExecutable']))
            assert loads.count(pkg.LOAD)==1
    assert sha(src)==entry['sha256']
    results['builds'][build]={'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size,
        'changedMembers':changed,'bundleID':info['CFBundleIdentifier'],'hostVersion':version,
        'ZIPCRC':'PASS','inputIPAUnchanged':True,'MarufYTDylibSHA256':hashlib.sha256(dylib).hexdigest(),
        'dependencyLoadsUnchanged':True,'runtime':'NOT TESTED'}
preserved=[]
for line in (OLD/'SHA256SUMS.txt').read_text().splitlines():
    expected,name=line.split(None,1)
    path=OLD/name.strip().lstrip('*')
    assert path.resolve().is_relative_to(OLD.resolve()) and sha(path)==expected
    preserved.append(name)
results['previousReleaseManifestFilesVerified']=len(preserved)
(OUT/'PACKAGE_VERIFICATION.json').write_text(json.dumps(results,indent=2)+'\n')
(OUT/'SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+str(p.relative_to(OUT)).replace('\\','/')
    for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt')+'\n')
print(json.dumps(results,indent=2))
