#!/usr/bin/env python3
"""Static YouTube host compatibility audit for MarufYT.

Compares two decrypted YouTube IPAs (current and candidate) against the hook
targets in this source tree: Objective-C class and selector names, Info.plist,
URL schemes, load commands, extensions and minimum iOS. Name presence is a
necessary condition only; the tweak also checks method type encodings at
runtime (YTKACEMethodTypesMatch) and skips missing targets.

usage: marufyt_host_audit.py CURRENT.ipa CANDIDATE.ipa REPORT.md [REPORT.json]
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import collections
import json
import plistlib
import re
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LC_LOAD = {0xC, 0x80000018}
SYSTEM_CLASSES = re.compile(r'^(UI|NS|AV|CA|MP|PH|WK|CL|UN|SK|CK|AS|LA|MK|_UI|_NS|CI|CG|QL|PK|GK|SF|SL|SC)[A-Z_]')

AREAS = {
    'Player hooks': ['Playback', 'Streaming', 'Gestures', 'Queue'],
    'Navigation hooks': ['Navigation'],
    'Feed hooks': ['Interface', 'Ads'],
    'Shorts hooks': ['Shorts'],
    'SponsorBlock': ['SponsorBlock'],
    'Download system': ['Downloads'],
    'Google sign-in / account switching': ['Compatibility'],
    'Liquid Glass': ['Navigation/TabBarHooks.mm', 'Navigation/GlassChrome.mm',
                     'Navigation/GlassSheets.mm', 'Playback/PlayerGlass.mm'],
    'Appearance / onboarding': ['Appearance', 'Onboarding'],
}


def read_host(path):
    with zipfile.ZipFile(path) as z:
        app = next(n.split('/')[1] for n in z.namelist() if n.count('/') == 2 and n.endswith('.app/Info.plist'))
        info = plistlib.loads(z.read(f'Payload/{app}/Info.plist'))
        data = z.read(f'Payload/{app}/{info["CFBundleExecutable"]}')
        names = z.namelist()
    magic, cputype, _, _, ncmds, _, _, _ = struct.unpack_from('<IiiIIIII', data, 0)
    assert magic == 0xFEEDFACF, 'expected thin arm64 host'
    cursor, loads, sections, crypt = 32, [], {}, None
    for _ in range(ncmds):
        cmd, size = struct.unpack_from('<II', data, cursor)
        if cmd in LC_LOAD:
            off = struct.unpack_from('<I', data, cursor + 8)[0]
            loads.append(data[cursor + off:cursor + size].split(b'\0', 1)[0].decode())
        elif cmd == 0x2C:
            crypt = struct.unpack_from('<I', data, cursor + 16)[0]
        elif cmd == 0x19:
            for i in range(struct.unpack_from('<I', data, cursor + 64)[0]):
                s = cursor + 72 + 80 * i
                name = data[s:s + 16].split(b'\0', 1)[0].decode()
                size_, offset = struct.unpack_from('<QI', data, s + 40)
                sections[name] = (offset, size_)
        cursor += size
    strings = {}
    for section in ('__objc_classname', '__objc_methname'):
        offset, size_ = sections.get(section, (0, 0))
        strings[section] = {x.decode('utf-8', 'replace') for x in data[offset:offset + size_].split(b'\0') if x}
    return {
        'version': info.get('CFBundleShortVersionString'), 'bundleId': info.get('CFBundleIdentifier'),
        'minimumOS': info.get('MinimumOSVersion'), 'cputype': hex(cputype), 'cryptid': crypt,
        'classes': strings['__objc_classname'], 'selectors': strings['__objc_methname'],
        'loads': loads, 'info': info,
        'schemes': sorted(s for t in info.get('CFBundleURLTypes', []) for s in t.get('CFBundleURLSchemes', [])),
        'extensions': sorted({n.split('/')[3] for n in names if '.appex/' in n and n.count('/') >= 4}),
        'groups': sorted(info.get('com.apple.security.application-groups', []) or []),
    }


def hook_targets():
    pattern = re.compile(r'YTKACEInstall\w*?(?:Hook|Method)\w*\(\s*@"([A-Za-z_][\w.]*)"\s*,\s*@"([^"]+)"', re.S)
    targets = []
    base = ROOT / 'Tweak/Features'
    for path in sorted(base.rglob('*.mm')):
        rel = path.relative_to(base).as_posix()
        for cls, sel in pattern.findall(path.read_text(encoding='utf-8')):
            targets.append((rel, cls, sel))
    return targets


def area_of(rel):
    hits = [area for area, keys in AREAS.items() if any(rel == k or rel.startswith(k + '/') for k in keys)]
    return hits or ['Other']


def main():
    current, candidate = read_host(sys.argv[1]), read_host(sys.argv[2])
    out_md, out_json = Path(sys.argv[3]), Path(sys.argv[4]) if len(sys.argv) > 4 else None
    rows = []
    per_area = collections.defaultdict(lambda: collections.Counter())
    for rel, cls, sel in hook_targets():
        system = bool(SYSTEM_CLASSES.match(cls))
        state = {}
        for label, host in (('current', current), ('candidate', candidate)):
            state[label] = 'system' if system else (
                'present' if cls in host['classes'] and sel in host['selectors'] else
                'class missing' if cls not in host['classes'] else 'selector missing')
        rows.append({'file': rel, 'class': cls, 'selector': sel, **state})
        if system:
            continue
        for area in area_of(rel):
            c = per_area[area]
            c['targets'] += 1
            c['current'] += state['current'] == 'present'
            c['candidate'] += state['candidate'] == 'present'
            c['lost'] += state['current'] == 'present' and state['candidate'] != 'present'
            c['gained'] += state['current'] != 'present' and state['candidate'] == 'present'

    def status(c):
        if c['targets'] == 0:
            return 'NOT FOUND'
        if c['lost'] == 0 and c['candidate'] >= c['current']:
            return 'COMPATIBLE (static)'
        return 'NEEDS UPDATE' if c['candidate'] > 0 else 'INCOMPATIBLE'

    info_keys = sorted(k for k in set(current['info']) | set(candidate['info'])
                       if current['info'].get(k) != candidate['info'].get(k)
                       and k not in ('CFBundleShortVersionString', 'CFBundleVersion', 'BuildMachineOSBuild',
                                     'DTPlatformBuild', 'DTSDKBuild', 'DTXcode', 'DTXcodeBuild', 'DTPlatformVersion',
                                     'DTSDKName', 'DTCompiler'))
    sso = ['SSOConfiguration', 'SSOKeychainHelper', 'SSOKeychainCore', 'SSOAuthorizationFactory',
           'YTPivotBarView', 'YTPivotBarItemView', 'YTIPlayerResponse', 'YTPlayerViewController',
           'YTReelPlayerViewController', 'YTIElementRenderer', 'YTSettingsSectionItemManager']
    lines = [f"# Host compatibility audit: YouTube {current['version']} → {candidate['version']}", '',
             '**Method:** static name analysis. Status means the hook target class and selector names exist; '
             'it is **not** runtime proof. The tweak also checks method type encodings at runtime and skips '
             'missing targets.', '',
             '| Property | Current | Candidate |', '| --- | --- | --- |']
    for key in ['version', 'bundleId', 'minimumOS', 'cputype', 'cryptid']:
        lines.append(f'| {key} | {current[key]} | {candidate[key]} |')
    lines += [f"| Objective-C class names | {len(current['classes'])} | {len(candidate['classes'])} |",
              f"| Selector names | {len(current['selectors'])} | {len(candidate['selectors'])} |",
              f"| Load commands | {len(current['loads'])} | {len(candidate['loads'])} |",
              f"| URL schemes identical | {'yes' if current['schemes'] == candidate['schemes'] else 'no'} | |",
              f"| Extensions | {', '.join(current['extensions']) or '—'} | {', '.join(candidate['extensions']) or '—'} |",
              '', '## Load commands added / removed', '']
    added = sorted(set(candidate['loads']) - set(current['loads']))
    removed = sorted(set(current['loads']) - set(candidate['loads']))
    lines += [f'- added: `{x}`' for x in added] + [f'- removed: `{x}`' for x in removed] or ['- none']
    lines += ['', '## Info.plist keys that differ (excluding build stamps)', '']
    lines += [f'- `{k}`: {str(current["info"].get(k))[:80]} → {str(candidate["info"].get(k))[:80]}' for k in info_keys] or ['- none']
    lines += ['', '## Key classes', '', '| Class | Current | Candidate |', '| --- | --- | --- |']
    for cls in sso:
        lines.append(f"| {cls} | {'yes' if cls in current['classes'] else 'no'} | {'yes' if cls in candidate['classes'] else 'no'} |")
    lines += ['', '## Hook targets by component', '',
              '| Component | Targets | Present in current | Present in candidate | Lost | Gained | Status |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    for area in list(AREAS) + ['Other']:
        c = per_area.get(area)
        if c is None:
            continue
        lines.append(f"| {area} | {c['targets']} | {c['current']} | {c['candidate']} | {c['lost']} | {c['gained']} | {status(c)} |")
    lost = [r for r in rows if r['current'] == 'present' and r['candidate'] not in ('present', 'system')]
    gained = [r for r in rows if r['candidate'] == 'present' and r['current'] not in ('present', 'system')]
    missing_both = [r for r in rows if r['current'] not in ('present', 'system') and r['candidate'] not in ('present', 'system')]
    lines += ['', f'## Targets lost in the candidate ({len(lost)})', '']
    lines += [f"- `{r['class']} {r['selector']}` ({r['file']}): {r['candidate']}" for r in lost] or ['- none']
    lines += ['', f'## Targets that appear only in the candidate ({len(gained)})', '']
    lines += [f"- `{r['class']} {r['selector']}` ({r['file']})" for r in gained] or ['- none']
    lines += ['', f'## Targets missing in both hosts ({len(missing_both)}): version fallbacks, skipped at runtime', '']
    lines += [f"- `{r['class']} {r['selector']}` ({r['file']}): {r['candidate']}" for r in missing_both] or ['- none']
    out_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if out_json:
        out_json.write_text(json.dumps({'current': current['version'], 'candidate': candidate['version'],
                                        'rows': rows, 'areas': {k: dict(v) for k, v in per_area.items()}},
                                       indent=1), encoding='utf-8')
    print('\n'.join(lines[:40]))
    print(f'... lost={len(lost)} gained={len(gained)} missingBoth={len(missing_both)}')


if __name__ == '__main__':
    main()
