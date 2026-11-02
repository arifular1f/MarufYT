#!/usr/bin/env python3
"""Assemble a MarufYT IPA from a user-supplied decrypted YouTube IPA and the
ROOTLESS MarufYT .deb. Standard library only; inputs are never modified.

Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import argparse
import hashlib
import io
import json
import plistlib
import struct
import sys
import tarfile
import zipfile
from pathlib import Path

LC_SEGMENT_64 = 0x19
LC_LOAD_DYLIB = 0xC
LC_LOAD_WEAK_DYLIB = 0x80000018
LC_CODE_SIGNATURE = 0x1D
MH_MAGIC_64 = 0xFEEDFACF
FAT_MAGIC = 0xCAFEBABE

DYLIB = 'MarufYT.dylib'
LOAD = '@rpath/MarufYT.dylib'
DEB_PREFIX = 'var/jb/Library/MobileSubstrate/DynamicLibraries/'
# Tweaks bundled by the YouTube Plus IPA builder; removed when present.
DEFAULT_REMOVE = ['YTLite', 'YouQuality', 'YouTubeDislikesReturn', 'DontEatMyContent',
                  'YTABConfig', 'YTVideoOverlay', 'YouGroupSettings', 'YTKACE']
TWEAK_BUNDLES = {'YTLite': 'YTLite', 'YouQuality': 'YouQuality', 'YouTubeDislikesReturn': 'RYD',
                 'DontEatMyContent': 'DontEatMyContent', 'YTABConfig': 'YTABC',
                 'YTVideoOverlay': 'YTVideoOverlay', 'YouGroupSettings': 'YouGroupSettings'}


# ---------------------------------------------------------------- Mach-O ----
def slice_offsets(data):
    if struct.unpack_from('>I', data, 0)[0] == FAT_MAGIC:
        return [struct.unpack_from('>IIIII', data, 8 + 20 * i)[2]
                for i in range(struct.unpack_from('>I', data, 4)[0])]
    return [0]


def commands(data, base):
    magic, _, _, _, ncmds, sizeofcmds, _, _ = struct.unpack_from('<IiiIIIII', data, base)
    if magic != MH_MAGIC_64:
        raise ValueError('not a 64-bit Mach-O')
    out, cursor = [], base + 32
    for _ in range(ncmds):
        cmd, size = struct.unpack_from('<II', data, cursor)
        out.append((cmd, cursor, size))
        cursor += size
    return out, sizeofcmds


def dylib_name(data, cmd, offset, size):
    if cmd not in (LC_LOAD_DYLIB, LC_LOAD_WEAK_DYLIB):
        return None
    start = offset + struct.unpack_from('<I', data, offset + 8)[0]
    return data[start:offset + size].split(b'\0', 1)[0].decode()


def first_section_offset(data, base, cmds):
    offsets = []
    for cmd, offset, _ in cmds:
        if cmd != LC_SEGMENT_64:
            continue
        for i in range(struct.unpack_from('<I', data, offset + 64)[0]):
            file_offset = struct.unpack_from('<I', data, offset + 72 + 80 * i + 48)[0]
            if file_offset:
                offsets.append(file_offset)
    return min(offsets)


def rewrite_loads(data, remove, add):
    out = bytearray(data)
    for base in slice_offsets(data):
        cmds, sizeofcmds = commands(data, base)
        kept, signature = [], []
        for cmd, offset, size in cmds:
            name = dylib_name(data, cmd, offset, size)
            if name is not None and name in remove:
                continue
            raw = bytes(data[offset:offset + size])
            (signature if cmd == LC_CODE_SIGNATURE else kept).append(raw)
        names = {dylib_name(k, struct.unpack_from('<I', k)[0], 0, len(k)) for k in kept}
        if add not in names:
            encoded = add.encode() + b'\0'
            size = (24 + len(encoded) + 7) & ~7
            kept.append(struct.pack('<IIIIII', LC_LOAD_DYLIB, size, 24, 0, 0, 0) + encoded.ljust(size - 24, b'\0'))
        kept += signature  # signers expect LC_CODE_SIGNATURE last
        blob = b''.join(kept)
        start = base + 32
        limit = base + first_section_offset(data, base, cmds)
        old_end = start + sizeofcmds
        if start + len(blob) > limit:
            raise ValueError('not enough header padding')
        if any(data[old_end:limit]):
            raise ValueError('non-zero header padding; refusing to edit')
        end = max(old_end, start + len(blob))
        out[start:end] = blob + b'\0' * (end - start - len(blob))
        struct.pack_into('<II', out, base + 16, len(kept), len(blob))
    return bytes(out)


def loads(data):
    cmds, _ = commands(data, slice_offsets(data)[0])
    return [dylib_name(data, c, o, s) for c, o, s in cmds if dylib_name(data, c, o, s)]


# ------------------------------------------------------------------- deb ----
def deb_files(path):
    data = Path(path).read_bytes()
    if data[:8] != b'!<arch>\n':
        raise ValueError('not a .deb')
    cursor, members = 8, {}
    while cursor < len(data):
        header = data[cursor:cursor + 60]
        name = header[:16].decode().strip().rstrip('/')
        size = int(header[48:58].decode().strip())
        members[name] = data[cursor + 60:cursor + 60 + size]
        cursor += 60 + size + (size & 1)
    name = next(n for n in members if n.startswith('data.tar'))
    raw = members[name]
    if name.endswith('.zst'):
        from compression import zstd  # Python 3.14+
        raw = zstd.decompress(raw)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:' if name.endswith('.zst') else 'r:*') as tar:
        for member in tar.getmembers():
            if member.isfile():
                files[member.name.lstrip('./')] = tar.extractfile(member).read()
    return files


# ------------------------------------------------------------------ main ----
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--youtube', required=True, type=Path)
    parser.add_argument('--deb', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--remove', nargs='*', default=DEFAULT_REMOVE,
                        help='tweak names whose @rpath/<name>.dylib loads and files are removed')
    args = parser.parse_args(argv)
    if args.output.resolve() in (args.youtube.resolve(), args.deb.resolve()):
        parser.error('output must differ from inputs')

    files = deb_files(args.deb)
    dylib = files[DEB_PREFIX + DYLIB]
    bundle = {k[len(DEB_PREFIX):]: v for k, v in files.items() if k.startswith(DEB_PREFIX + 'YTKACE.bundle/')}
    if not bundle:
        raise SystemExit('deb has no YTKACE.bundle')

    with zipfile.ZipFile(args.youtube) as src:
        app = next(n.split('/')[1] for n in src.namelist() if n.startswith('Payload/') and n.endswith('.app/Info.plist')
                   and n.count('/') == 2)
        prefix = f'Payload/{app}/'
        info = plistlib.loads(src.read(prefix + 'Info.plist'))
        executable = prefix + info['CFBundleExecutable']
        host_loads = loads(src.read(executable))
        remove_loads = {f'@rpath/{n}.dylib' for n in args.remove} & set(host_loads)
        removed_names = {l.split('/')[-1][:-6] for l in remove_loads}
        drop = [prefix + f'Frameworks/{n}.dylib' for n in removed_names]
        drop += [prefix + f'{TWEAK_BUNDLES[n]}.bundle/' for n in removed_names if n in TWEAK_BUNDLES]
        drop += [prefix + '_CodeSignature/', prefix + 'cyan.entitlements', prefix + 'YTKACE.bundle/']
        if removed_names and not any('CydiaSubstrate' in l for l in set(host_loads) - remove_loads):
            drop.append(prefix + 'Frameworks/CydiaSubstrate.framework/')
        if 'YTLite' in removed_names:
            drop.append(prefix + 'PlugIns/OpenYoutubeSafariExtension.appex/')

        def dropped(name):
            return any(name == d.rstrip('/') or name.startswith(d) for d in drop)

        args.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.output.with_suffix('.tmp')
        removed_files = 0
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
            for item in src.infolist():
                if dropped(item.filename):
                    removed_files += not item.is_dir()
                    continue
                data = src.read(item)
                if item.filename == executable:
                    data = rewrite_loads(data, remove_loads, LOAD)
                elif item.filename == prefix + 'Info.plist':
                    plist = plistlib.loads(data)
                    if 'YTLite' in removed_names:  # undo YTLite's Info.plist edits
                        plist.pop('NSFaceIDUsageDescription', None)
                        plist['UIDesignRequiresCompatibility'] = True
                    plist['UIFileSharingEnabled'] = True
                    plist['LSSupportsOpeningDocumentsInPlace'] = True
                    modes = plist.setdefault('UIBackgroundModes', [])
                    if 'audio' not in modes:
                        modes.append('audio')
                    data = plistlib.dumps(plist, fmt=plistlib.FMT_BINARY, sort_keys=False)
                out = zipfile.ZipInfo(item.filename, item.date_time)
                out.external_attr, out.create_system = item.external_attr, item.create_system
                out.compress_type = zipfile.ZIP_STORED if item.is_dir() else zipfile.ZIP_DEFLATED
                dst.writestr(out, data)
            for rel, data in sorted(bundle.items()):
                out = zipfile.ZipInfo(prefix + rel, (2026, 11, 2, 0, 0, 0))
                out.external_attr, out.create_system = 0o100644 << 16, 3
                dst.writestr(out, data, zipfile.ZIP_DEFLATED)
            out = zipfile.ZipInfo(prefix + 'Frameworks/' + DYLIB, (2026, 11, 2, 0, 0, 0))
            out.external_attr, out.create_system = 0o100755 << 16, 3
            dst.writestr(out, dylib, zipfile.ZIP_DEFLATED)
        tmp.replace(args.output)

    # Verify the written archive.
    with zipfile.ZipFile(args.output) as z:
        result = {
            'zipCRC': z.testzip() is None,
            'hostNonSystemLoads': [l for l in loads(z.read(executable)) if not l.startswith(('/System', '/usr/lib'))],
            'dylibMatchesDeb': z.read(prefix + 'Frameworks/' + DYLIB) == dylib,
            'bundleFiles': sum(1 for n in z.namelist() if n.startswith(prefix + 'YTKACE.bundle/') and not n.endswith('/')),
            'bundleIdentifier': plistlib.loads(z.read(prefix + 'Info.plist'))['CFBundleIdentifier'],
            'version': plistlib.loads(z.read(prefix + 'Info.plist'))['CFBundleShortVersionString'],
            'removedTweaks': sorted(removed_names),
            'removedFiles': removed_files,
        }
    h = hashlib.sha256()
    with open(args.output, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    result['sha256'] = h.hexdigest()
    ok = (result['zipCRC'] and result['dylibMatchesDeb'] and result['bundleFiles'] == len(bundle)
          and LOAD in result['hostNonSystemLoads'])
    result['ok'] = ok
    print(json.dumps(result, indent=1))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
