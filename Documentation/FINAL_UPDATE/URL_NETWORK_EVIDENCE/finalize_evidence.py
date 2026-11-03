"""Read-only package verification and lossless audit-evidence packaging."""
from pathlib import Path
import csv, gzip, hashlib, json, plistlib, subprocess, sys, zipfile
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[2]
WORK = REPO.parent
sys.path.insert(0, str(WORK / 'release/MarufYT-Phase2.1/Source'))
import macho

def digest(path):
    with path.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

inputs = json.loads((OUT/'INPUTS.json').read_text())
result = {'packages': {}, 'auditOnly': True, 'executedPayloads': 0}
for build, entry in inputs.items():
    path = WORK / entry['path']
    assert digest(path) == entry['sha256']
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        info = plistlib.loads(z.read('Payload/YouTube.app/Info.plist'))
        binaries = []
        for n in z.namelist():
            if n.endswith('/'): continue
            data = z.read(n)
            if data[:4] not in (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe'): continue
            item = {'file': n, 'sha256': hashlib.sha256(data).hexdigest()}
            try:
                slices = [macho.parse(data, off) for off in macho.slice_offsets(data)]
                item['sliceCount'] = len(slices)
                item['CPUType'] = [s.get('cputype', 'see parser') for s in slices]
                item['sectionNames'] = sorted({s['segment']+','+s['name'] for p in slices for s in p['sections']})
            except Exception as e: item['parseError'] = type(e).__name__
            if n.endswith('/MarufYT.dylib'):
                item['HLSLiteralEvidence'] = {s: data.find(s.encode()) for s in ('hlsManifestUrl', 'setHlsManifestURL:', 'vision video=%@ playability=%@ no manifest', 'swap video=%@ source=%@')}
                item['offsetMeaning'] = 'Exact literal byte offsets, not function addresses or runtime proof'
            binaries.append(item)
        result['packages'][build] = {'path': str(path), 'sha256': entry['sha256'], 'zipCRCValid': True,
            'bundleID': info.get('CFBundleIdentifier'), 'hostVersion': info.get('CFBundleShortVersionString'),
            'ATS': info.get('NSAppTransportSecurity'), 'binaries': binaries}
    assert digest(path) == entry['sha256']

test = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'Tests.test_security_fixes', '-v'], cwd=REPO, capture_output=True, text=True)
(OUT/'SOURCE_CONTRACT_TESTS.txt').write_text(test.stdout+test.stderr+'\nProcess exit code: '+str(test.returncode)+'\n', encoding='utf-8')
result['sourceContractTestExitCode'] = test.returncode
assert test.returncode == 0
git = r'C:\Program Files\Git\cmd\git.exe'
for key,args in [('branch',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('trackedDiff',['diff','--stat']),('trackedStagedDiff',['diff','--cached','--stat'])]:
    result[key] = subprocess.check_output([git,*args],cwd=REPO,text=True).strip()
assert result['branch']=='final-update-security'
assert result['HEAD']=='81c31676d91c94e47c905ebe31b1cf6fcb1b62ba'
assert not result['trackedDiff'] and not result['trackedStagedDiff']
(OUT/'FINAL_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')

# Only this audit's newly generated CSVs are compressed/replaced. Never releases.
compressed = []
for path in sorted(OUT.glob('*.csv')):
    assert path.resolve().parent == OUT.resolve()
    before = digest(path)
    target = path.with_suffix('.csv.gz')
    with path.open('rb') as src, target.open('wb') as dst:
        with gzip.GzipFile(filename='',mode='wb',fileobj=dst,mtime=0) as gz:
            while chunk := src.read(1024*1024): gz.write(chunk)
    with gzip.open(target,'rb') as f: after = hashlib.file_digest(f,'sha256').hexdigest()
    assert before == after
    compressed.append({'file': target.name,'uncompressedSHA256':before,'gzipSHA256':digest(target)})
    path.unlink()
(OUT/'COMPRESSION_VERIFICATION.json').write_text(json.dumps(compressed,indent=2)+'\n')
print('Verified both IPA hashes/CRCs, unchanged branch/HEAD/source; four source contracts passed; compressed',len(compressed),'CSV files losslessly.')
