"""Read-only static evidence collector; never executes or extracts IPA payloads.
Secret pattern results contain categories/offsets/fingerprints, never values.
Uses the existing local Mach-O parser and repository secret scanner.
"""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import plistlib
import re
import struct
import sys
import zipfile

REPO = Path(__file__).resolve().parents[2]
WORK = REPO.parent
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK / 'release/MarufYT-Phase2.1/Source'))
sys.path.insert(0, str(REPO / 'Tools'))
import macho
import marufyt_secret_scan as scanner


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def section_strings(data, info, section):
    result = set()
    for item in info['sections']:
        if item['name'] == section:
            start = info['base'] + item['offset']
            result.update(x.decode('utf-8', 'replace') for x in data[start:start + item['size']].split(b'\0') if x)
    return result


def binary(data):
    infos = []
    for base in macho.slice_offsets(data):
        info = macho.parse(data, base)
        imports, entitlements = set(), []
        for command in info['commands']:
            offset = command['offset']
            if command['cmd'] == 2:  # LC_SYMTAB, nlist_64
                symoff, count, stroff, strsize = struct.unpack_from('<IIII', data, offset + 8)
                for index in range(count):
                    string_index, kind = struct.unpack_from('<IB', data, base + symoff + index * 16)
                    if kind & 0x0e == 0 and string_index < strsize:
                        name = data[base + stroff + string_index:base + stroff + strsize].split(b'\0', 1)[0].decode('utf-8', 'replace')
                        imports.add(name)
            if command['cmd'] == macho.LC_CODE_SIGNATURE:
                off, size = struct.unpack_from('<II', data, offset + 8)
                blob = data[base + off:base + off + size]
                if len(blob) >= 12 and struct.unpack_from('>I', blob)[0] == 0xfade0cc0:
                    count = struct.unpack_from('>I', blob, 8)[0]
                    for index in range(count):
                        slot, start = struct.unpack_from('>II', blob, 12 + index * 8)
                        magic, length = struct.unpack_from('>II', blob, start)
                        if magic == 0xfade7171:
                            obj = plistlib.loads(blob[start + 8:start + length].rstrip(b'\0'))
                            entitlements.append({'format': 'XML', 'values': obj})
                        elif magic == 0xfade7172:
                            entitlements.append({'format': 'DER', 'length': length, 'decoded': False})
        # Convert bytes/dates only in serialisation, not content matching.
        infos.append({'cputype': info['cputype'], 'filetype': info['filetype'],
                      'loads': [c['name'] for c in info['commands'] if c['cmd'] in macho.DYLIB_CMDS],
                      'rpaths': [c['name'] for c in info['commands'] if c['cmd'] == macho.LC_RPATH],
                      'cryptids': [c['cryptid'] for c in info['commands'] if 'cryptid' in c],
                      'imports': sorted(imports), 'entitlements': entitlements})
    return infos


def inventory(path):
    result = {'path': path.relative_to(WORK).as_posix(), 'sha256': file_sha(path)}
    with zipfile.ZipFile(path) as archive:
        result['zipCRCValid'] = archive.testzip() is None
        result['entries'] = len(archive.infolist())
        result['nativeBinaries'], result['privacyManifests'], result['secretPatternMatches'] = {}, {}, []
        info = plistlib.loads(archive.read('Payload/YouTube.app/Info.plist'))
        result['hostInfo'] = {k: v for k, v in info.items() if k.startswith(('NS', 'UIBackground', 'UIFileSharing', 'LSSupports', 'CFBundle'))}
        result['permissionDescriptions'] = {k: v for k, v in info.items() if 'UsageDescription' in k}
        result['provisioningFiles'] = [n for n in archive.namelist() if n.endswith('.mobileprovision')]
        result['scriptOrCertificatePaths'] = [n for n in archive.namelist() if n.lower().endswith(('.sh', '.py', '.js', '.p12', '.pfx', '.pem', '.cer', '.der', '.key'))]
        host_urls = set()
        for item in archive.infolist():
            if item.is_dir():
                continue
            data = archive.read(item)
            if item.filename.endswith('PrivacyInfo.xcprivacy'):
                result['privacyManifests'][item.filename] = plistlib.loads(data)
            if data[:4] in (b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe'):
                result['nativeBinaries'][item.filename] = {'sha256': sha(data), 'slices': binary(data)}
                for url in re.findall(rb'https?://([a-zA-Z0-9.-]+)(?:[:/][^\x00\x20\x22\x27<>]*)?', data):
                    host_urls.add(url.decode('ascii').lower())
            # Scan credential patterns, including resources, without emitting matches.
            result['secretPatternMatches'].extend(scanner.scan_bytes(data, {item.filename}))
        result['literalURLHostsFromNativeBinaries'] = sorted(host_urls)
    return result


release = WORK / 'release'
snapshots = {}
for phase in ['MarufYT-Phase4', 'MarufYT-Phase4.1']:
    for file in (release / phase).rglob('*'):
        if file.is_file():
            snapshots[file.relative_to(WORK).as_posix()] = file_sha(file)
(OUT / 'PRESERVATION_BEFORE.json').write_text(json.dumps(snapshots, indent=2) + '\n')

inventories = {}
for phase in ['MarufYT-Phase4', 'MarufYT-Phase4.1']:
    for path in sorted((release / phase).rglob('*.ipa')):
        inventory_result = inventory(path)
        inventories[path.name] = inventory_result
        print(path.name, 'CRC', inventory_result['zipCRCValid'], 'native', len(inventory_result['nativeBinaries']),
              'manifests', len(inventory_result['privacyManifests']), 'pattern candidates', len(inventory_result['secretPatternMatches']), flush=True)
        (OUT / (path.stem + '.json')).write_text(json.dumps(inventory_result, indent=2, default=str) + '\n')

comparison = {}
for host in ['21.43.5', '21.39.4']:
    previous = next(v for k, v in inventories.items() if 'marufyt.6-' in k and host in k)
    current = next(v for k, v in inventories.items() if 'marufyt.7-' in k and host in k)
    with zipfile.ZipFile(WORK / previous['path']) as p, zipfile.ZipFile(WORK / current['path']) as c:
        pn, cn = set(p.namelist()), set(c.namelist())
        different = [n for n in sorted(pn & cn) if p.read(n) != c.read(n)]
    comparison[host] = {'addedPaths': sorted(cn-pn), 'removedPaths': sorted(pn-cn), 'changedPaths': different,
                        'infoPlistIdentical': previous['hostInfo'] == current['hostInfo'],
                        'privacyManifestsIdentical': previous['privacyManifests'] == current['privacyManifests']}
(OUT / 'PHASE4_BINARY_COMPARISON.json').write_text(json.dumps(comparison, indent=2) + '\n')
print('Phase4 comparison:', {k: len(v['changedPaths']) for k, v in comparison.items()}, flush=True)
