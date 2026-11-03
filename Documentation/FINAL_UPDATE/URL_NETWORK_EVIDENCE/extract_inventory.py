"""Read-only IPA string/structured-data endpoint inventory, no payload execution.
Raw secret-shaped URL values are redacted; hashes and byte offsets are retained.
This is lexical extraction, not proof of DNS ownership or code reachability.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import base64
import bisect
import collections
import csv
import gzip
import hashlib
import html
import io
import ipaddress
import json
import plistlib
import re
import urllib.parse
import zipfile

REPO = Path(__file__).resolve().parents[3]
WORK = REPO.parent
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK / 'release/MarufYT-Phase2.1/Source'))
import macho

ASCII = re.compile(rb'[\x20-\x7e]{5,}')
UTF16_LE = re.compile(rb'(?:[\x20-\x7e]\x00){5,}')
UTF16_BE = re.compile(rb'(?:\x00[\x20-\x7e]){5,}')
URI = re.compile(r'(?i)\b([a-z][a-z0-9+.-]{0,100})://[^\s<>"\x27`{}\\\x00]+')
RAW_URI = re.compile(rb'(?i)\b[a-z][a-z0-9+.-]{0,100}://[^\x00-\x20\x7f<>"\x27`{}\\]+')
DOMAIN = re.compile(r'(?i)(?<![a-z0-9_@-])(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}(?![a-z0-9_-])')
IPV4 = re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])')
IPV6 = re.compile(r'(?<![\w:])(?:[a-fA-F0-9]{0,4}:){2,}[a-fA-F0-9:.%a-zA-Z_-]*(?![\w:])')
SENSITIVE = re.compile(r'(?i)([?&;](?:[^=&;]*(?:token|secret|password|passwd|cookie|authorization|signature|credential|api.?key|session|visitorData)[^=&;]*|key|sig|code|auth|pot)=)[^&#;\s]*')
KEYLIKE = re.compile(r'(?i)(?:AIza[0-9a-z_-]{35}|GOCSPX-[0-9a-z_-]{28}|gh[pousr]_[0-9a-z]{36,}|eyJ[\w-]+\.eyJ[\w-]+\.[\w-]+)')
MAX_INNER = 128 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def sanitize(text):
    text = re.sub(r'(?i)([a-z][a-z0-9+.-]*://)[^/\s@]+@', r'\1[userinfo-redacted]@', text)
    text = SENSITIVE.sub(r'\1[redacted]', text)
    return KEYLIKE.sub('[credential-pattern-redacted]', text)


def owner(name):
    if name.endswith('/MarufYT.dylib') or '/YTKACE.bundle/' in name:
        return 'MarufYT (includes bundled dependencies)'
    return 'Original host / bundled component'


def classify_domain(host):
    h = host.lower().rstrip('.')
    families = ['google.com', 'googleapis.com', 'googlevideo.com', 'googleusercontent.com',
                'gstatic.com', 'ggpht.com', 'ytimg.com', 'youtube.com', 'youtu.be',
                'doubleclick.net', 'googleadservices.com', 'firebase.com', 'firebaseio.com',
                'app-analytics-services.com', 'app-analytics-services-att.com']
    if any(h == f or h.endswith('.' + f) for f in families):
        return 'Google/YouTube-associated naming; ownership/activity not independently verified'
    if h in ['sponsor.ajay.app', 'dearrow-thumb.ajay.app']:
        return 'Documented SponsorBlock/DeArrow integration'
    if h == 'api.aisloplist.com':
        return 'Documented AiSList report integration'
    if h == 'raw.githubusercontent.com':
        return 'GitHub raw content; AiSList list source when referenced by tweak'
    if h == 'github.com':
        return 'Repository/project links; per-row context required'
    if h.endswith(('.example', '.invalid', '.test', '.localhost')) or h in ['example.com', 'example.org', 'example.net']:
        return 'Reserved/example/testing candidate'
    if h in ['www.w3.org', 'schemas.android.com', 'aomedia.org', 'streams.videolan.org']:
        return 'Standards/documentation/sample candidate; not evidence of a request'
    return 'Unclassified lexical candidate; may be code/property/file/version text, not a DNS destination'


def scope_ip(value):
    try:
        ip = ipaddress.ip_address(value.split('%')[0])
    except ValueError:
        return None
    if ip.is_loopback: kind = 'loopback'
    elif ip.is_unspecified: kind = 'unspecified/bind placeholder'
    elif ip.is_link_local: kind = 'link-local'
    elif ip.is_multicast: kind = 'multicast'
    elif ip.is_private: kind = 'private/documentation/non-global'
    else: kind = 'global-syntax candidate; no ownership/reachability verification'
    return str(ip), kind


cache = {}
coverage = []
per_build = {}
records = collections.defaultdict(dict)
all_files = collections.defaultdict(dict)


def extract_blob(data, name):
    # Cache identical files across the IPAs; paths and owner are applied later.
    digest = sha(data)
    if digest in cache:
        return cache[digest]
    found = {}
    sections = []
    if data[:4] in (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe'):
        try:
            for base in macho.slice_offsets(data):
                info = macho.parse(data, base)
                for section in info['sections']:
                    if not section['zerofill']:
                        sections.append((base + section['offset'], base + section['offset'] + section['size'],
                                         section['segment'] + ',' + section['name']))
        except (ValueError, KeyError, IndexError):
            pass

    def collect(text, offset, encoding, location=''):
        # Never save whole surrounding strings, which might include unrelated secrets.
        def emit(kind, raw, confidence='lexical'):
            raw = raw.strip()
            if not raw: return
            value = sanitize(raw)
            key = kind, sha(raw.encode('utf-8', 'replace'))
            if key not in found:
                section = location or next((s for a, b, s in sections if a <= offset < b), '')
                found[key] = {'kind': kind, 'value': value, 'rawSHA256': key[1],
                              'byteOffsetOrContainerOffset': offset, 'encoding': encoding,
                              'sectionOrStructuredPath': section, 'literalCountInFile': 0,
                              'redacted': value != raw, 'confidence': confidence}
            found[key]['literalCountInFile'] += 1

        for m in URI.finditer(text):
            value = m.group(0)
            scheme = m.group(1).lower()
            kind = 'URL' if scheme in ['http', 'https', 'ws', 'wss'] else 'custom-URI'
            emit(kind, value)
        for m in re.finditer(r'(?i)\b(?:mailto|tel|sms):[^\s<>"\x27`]+',text):
            emit('custom-URI',m.group(0))
        for m in DOMAIN.finditer(text): emit('domain-candidate', m.group(0).lower(), 'DNS-like syntax only')
        for m in IPV4.finditer(text):
            ip = scope_ip(m.group(0))
            if ip: emit('IPv4-candidate', ip[0], ip[1] + '; can also be version/code data')
        if ':' in text:
            for m in IPV6.finditer(text):
                ip = scope_ip(m.group(0))
                if ip: emit('IPv6-candidate', ip[0], ip[1] + '; syntax only')

    # UTF8 URLs can contain non-ASCII paths/hosts; don't truncate them to ASCII.
    for m in RAW_URI.finditer(data):
        collect(m.group().decode('utf-8','replace'),m.start(),'raw UTF8 URI candidate')
    # Decode complete UTF16 Mach-O Unicode sections using the thin slice's byte order.
    for start,end,section_name in sections:
        if section_name.endswith(',__ustring'):
            collect(data[start:end].decode('utf-16-le','replace'),start,'Mach-O UTF16-LE section',section_name)
    # PEM certificate URI/SAN text lives inside base64 DER. No private key is decoded.
    for pem in re.finditer(rb'-----BEGIN CERTIFICATE-----\s*([A-Za-z0-9+/=\s]+?)-----END CERTIFICATE-----',data):
        try: der=base64.b64decode(pem.group(1),validate=False)
        except ValueError: continue
        for m in ASCII.finditer(der): collect(m.group().decode('ascii'),pem.start(),'PEM certificate base64 DER ASCII')
    # Full uncompressed member bytes, not just selected Mach-O string sections.
    for pattern, enc in [(ASCII, 'ASCII/UTF8-compatible'), (UTF16_LE, 'UTF16-LE ASCII-range'), (UTF16_BE, 'UTF16-BE ASCII-range')]:
        for match in pattern.finditer(data):
            text = match.group().decode('ascii' if enc == 'ASCII/UTF8-compatible' else ('utf-16-le' if enc.startswith('UTF16-LE') else 'utf-16-be'))
            collect(text, match.start(), enc)
            # Common textual encodings; preserve provenance, do not evaluate scripts.
            if '\\/' in text or '&#' in text or '&amp;' in text or re.search(r'%[0-9a-fA-F]{2}', text):
                decoded = urllib.parse.unquote(html.unescape(text.replace('\\/', '/')))
                if decoded != text and ('://' in decoded or 'http' in decoded.lower()):
                    collect(decoded, match.start(), enc + '+percent/HTML/escaped-slash decoded')
            if 'aHR0' in text or 'd3M6' in text or 'd3Nz' in text or text.startswith('eyJ'):
                for token in re.findall(r'[A-Za-z0-9+/_-]{16,}={0,2}', text):
                    if not token.startswith(('aHR0', 'd3M6', 'd3Nz', 'eyJ')) or len(token) > 65536: continue
                    try:
                        decoded = base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).decode('utf-8')
                    except (ValueError, UnicodeDecodeError): continue
                    if '://' in decoded: collect(decoded, match.start(), enc + '+base64 decoded')

    def walk(obj, path):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(key, str): collect(key, -1, 'structured-key', path)
                walk(value, path + '/' + str(key))
        elif isinstance(obj, list):
            for i, value in enumerate(obj): walk(value, path + '/' + str(i))
        elif isinstance(obj, str):
            collect(obj, -1, 'structured-value', path)
            if '/CFBundleURLSchemes/' in path or '/LSApplicationQueriesSchemes/' in path:
                key = 'declared-custom-scheme', sha(obj.encode())
                found[key] = {'kind': key[0], 'value': sanitize(obj), 'rawSHA256': key[1],
                              'byteOffsetOrContainerOffset': -1, 'encoding': 'structured-value',
                              'sectionOrStructuredPath': path, 'literalCountInFile': 1,
                              'redacted': sanitize(obj) != obj, 'confidence': 'Declared scheme; inbound/query capability, not a contacted server'}
            if '/NSExceptionDomains/' in path:
                collect(path.split('/NSExceptionDomains/',1)[1].split('/')[0], -1, 'ATS configuration', path)
        elif isinstance(obj, bytes) and len(obj) <= MAX_INNER:
            # plist data values may embed printable text or further structures.
            for m in ASCII.finditer(obj): collect(m.group().decode('ascii'), -1, 'plist-data ASCII', path)

    structured = False
    try:
        if data.startswith((b'bplist00', b'<?xml', b'<!DOCTYPE plist')) or name.endswith(('.plist', '.xcprivacy')):
            walk(plistlib.loads(data), '$'); structured = True
        elif name.endswith('.json'):
            walk(json.loads(data), '$'); structured = True
    except (ValueError, TypeError, plistlib.InvalidFileException): pass
    if name.lower().endswith(('.js','.html','.htm','.xml','.json','.txt','.strings','.stringsdict','.config','.cfg','.svg','.css')):
        try:
            text=data.decode('utf-8')
            if '\x00' not in text:
                collect(text,0,'complete UTF8 text resource')
                decoded=urllib.parse.unquote(html.unescape(text.replace('\\/','/')))
                if decoded!=text: collect(decoded,0,'complete text+percent/HTML/escaped-slash decoded')
        except UnicodeDecodeError: pass
    cache[digest] = list(found.values()), structured
    return cache[digest]


def process_member(build, name, data, container=''):
    found, structured = extract_blob(data, name)
    label = name if not container else container + '!' + name
    coverage.append({'build': build, 'file': label, 'bytes': len(data), 'sha256': sha(data),
                     'structuredParsed': structured, 'findings': len(found), 'scan': 'raw member + ASCII-range UTF16 + supported textual decodes'})
    for row in found:
        key = row['kind'], row['rawSHA256']
        item = records[key]
        if not item:
            item.update({'kind': row['kind'], 'value': row['value'], 'rawSHA256': row['rawSHA256'], 'redacted': row['redacted'], 'builds': set(), 'files': set(), 'occurrences': []})
        item['builds'].add(build); item['files'].add(label)
        item['occurrences'].append({'build': build, 'file': label, 'owner': owner(label), **row})
    # Bounded nested ZIP/gzip handling. Opaque assets/encryption cannot be decoded generically.
    if data.startswith(b'PK\x03\x04'):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as inner:
                if sum(i.file_size for i in inner.infolist()) <= MAX_INNER:
                    for member in inner.infolist():
                        if not member.is_dir():
                            found_inner, _ = extract_blob(inner.read(member), member.filename)
                            for row in found_inner:
                                key = row['kind'], row['rawSHA256']; item = records[key]
                                if not item: item.update({'kind': row['kind'], 'value': row['value'], 'rawSHA256': row['rawSHA256'], 'redacted': row['redacted'], 'builds': set(), 'files': set(), 'occurrences': []})
                                file = label + '!' + member.filename
                                item['builds'].add(build); item['files'].add(file)
                                item['occurrences'].append({'build': build, 'file': file, 'owner': owner(label), **row})
        except (ValueError, zipfile.BadZipFile): pass
    elif data.startswith(b'\x1f\x8b'):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream: inner = stream.read(MAX_INNER + 1)
            if len(inner) <= MAX_INNER:
                found_inner, _ = extract_blob(inner, name + '!gzip')
                for row in found_inner:
                    key = row['kind'], row['rawSHA256']; item = records[key]
                    if not item: item.update({'kind': row['kind'], 'value': row['value'], 'rawSHA256': row['rawSHA256'], 'redacted': row['redacted'], 'builds': set(), 'files': set(), 'occurrences': []})
                    file = label + '!gzip'; item['builds'].add(build); item['files'].add(file)
                    item['occurrences'].append({'build': build, 'file': file, 'owner': owner(label), **row})
        except (OSError, ValueError): pass


release = WORK / 'release/MarufYT-FinalUpdate-1.1.4+marufyt.8'
inputs = {}
for host, build in [('21.43.5','Latest'),('21.39.4','Stable')]:
    candidates = list(release.glob('*' + host + '/*.ipa'))
    if len(candidates) != 1: raise RuntimeError('Ambiguous IPA input')
    p = candidates[0]
    inputs[build] = {'path': p.relative_to(WORK).as_posix(), 'sha256': file_sha(p), 'bytes': p.stat().st_size}
    print('Scanning', build, p.name, flush=True)
    with zipfile.ZipFile(p) as archive:
        inputs[build]['zipCRCValid'] = archive.testzip() is None
        entries = [i for i in archive.infolist() if not i.is_dir()]
        inputs[build]['fileCount'] = len(entries)
        for i, member in enumerate(entries):
            data = archive.read(member)
            all_files[build][member.filename] = sha(data)
            process_member(build, member.filename, data)
            if i % 250 == 0: print(build, i, '/', len(entries), member.filename, flush=True)
    print('Finished', build, 'unique lexical records so far', len(records), flush=True)

(OUT/'INPUTS.json').write_text(json.dumps(inputs,indent=2)+'\n')
for index, key in enumerate(sorted(records, key=lambda k:(k[0],records[k]['value'],k[1])),1):
    records[key]['id'] = f'N{index:06d}'

def write_csv(name, columns, rows):
    with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)

inventory=[]; occurrences=[]; groups=collections.Counter(); comparisons=collections.defaultdict(list)
for key,item in records.items():
    builds=sorted(item['builds']); comparison='Common' if len(builds)==2 else builds[0]+'-only'
    groups[(item['kind'],comparison)]+=1
    owners=sorted({r['owner'] for r in item['occurrences']})
    classification=classify_domain(item['value']) if item['kind']=='domain-candidate' else 'See feature map / lexical evidence; not a runtime observation'
    inventory.append({'id':item['id'],'kind':item['kind'],'value':item['value'],'rawSHA256':item['rawSHA256'],
                      'comparison':comparison,'owners':'; '.join(owners),'classification':classification,
                      'files':'; '.join(sorted(item['files'])),'occurrences':len(item['occurrences']),
                      'redacted':item['redacted'],'function':'Unknown for opaque compiled/resource strings; see source map',
                      'reachability':'Not established from a string','dataTransmitted':'Unknown for host literals; see source map for verified tweak paths',
                      'authentication':'Not established by string evidence'})
    comparisons[item['kind']+' / '+comparison].append({'id':item['id'],'value':item['value'],'rawSHA256':item['rawSHA256']})
    for row in item['occurrences']: occurrences.append({'id':item['id'],**row})

write_csv('COMPLETE_INVENTORY.csv',list(inventory[0]),sorted(inventory,key=lambda r:r['id']))
write_csv('OCCURRENCES.csv',['id','build','file','owner','kind','value','rawSHA256','byteOffsetOrContainerOffset','encoding','sectionOrStructuredPath','literalCountInFile','redacted','confidence'],occurrences)
write_csv('FILE_COVERAGE.csv',['build','file','bytes','sha256','structuredParsed','findings','scan'],coverage)
(OUT/'LATEST_STABLE_COMPARISON.json').write_text(json.dumps(comparisons,indent=2)+'\n')
unchanged=[]
for build,info in inputs.items():
    current=file_sha(WORK/info['path']);unchanged.append(current==info['sha256'])
    info['afterSHA256']=current
summary={'inputs':inputs,'allInputsUnchanged':all(unchanged),'uniqueFilesScanned':len(cache),
         'fileCoverageRows':len(coverage),'records':len(inventory),'occurrenceRows':len(occurrences),
         'counts':[{'kind':k,'comparison':c,'count':v} for (k,c),v in sorted(groups.items())],
         'encodedRows':sum('decoded' in r['encoding'] for r in occurrences),
         'redactedRecords':sum(r['redacted'] for r in inventory),
         'networkRequestsSent':0,'payloadsExecuted':0,
         'limits':['Lexical candidates are not DNS ownership/connection/reachability proof.',
                   'First byte offset is the enclosing printable string/container, not necessarily the exact token byte.',
                   'UTF16 raw scanning covers ASCII-range text (both alignments can create noisy/truncated candidates); complete Mach-O Unicode sections and decoded plist/JSON values are traversed as Unicode.',
                   'One bounded nested ZIP/gzip layer; no script execution, arbitrary deobfuscation, proprietary asset decompression or encrypted-string recovery.',
                   'Any member/encoding that cannot be decoded remains covered by raw string scanning only.']}
(OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['limits','inputs']},indent=2),flush=True)
