#!/usr/bin/env python3
"""Isolated arm64 LGPL static-library replacement/link demonstration.
Never changes vendored libraries or builds/repackages a release application.
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theos', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    opts = parser.parse_args()
    opts.output.mkdir(parents=True, exist_ok=False)
    out = opts.output.resolve()
    bin_dir = opts.theos.resolve() / 'toolchain/linux/iphone/bin'
    compiler = bin_dir / 'clang'
    archiver = bin_dir / 'llvm-ar'
    sdk = opts.theos.resolve() / 'sdks/iPhoneOS16.5.sdk'
    source = ROOT / 'Vendor/FFmpeg/lib/libavutil.a'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    commands = []

    def run(*args):
        commands.append([str(a) for a in args])
        try:
            return subprocess.check_output([str(a) for a in args], text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print(error.output, flush=True)
            raise

    names = run(archiver, 't', source).splitlines()
    if names.count('version.o') != 1:
        raise ValueError('Expected exactly one version.o; no arbitrary archive-member replacement')
    probe = out / 'probe.c'
    probe.write_text('#include <libavutil/avutil.h>\nconst char *MarufYTFFmpegProbe(void) { return av_version_info(); }\n')
    marker = 'MarufYT LGPL relink evidence only'
    changed = out / 'version.c'
    changed.write_text('const char *av_version_info(void) { return "' + marker + '"; }\n')
    flags = ['-target', 'arm64-apple-ios15.0', '-isysroot', str(sdk), '-fPIC']
    run(compiler, *flags, '-I' + str(ROOT / 'Vendor/FFmpeg/include'), '-c', probe, '-o', out / 'probe.o')
    run(compiler, *flags, '-c', changed, '-o', out / 'version.o')
    modified = out / 'libavutil-modified-for-audit.a'
    shutil.copyfile(source, modified)
    run(archiver, 'd', modified, 'version.o')
    run(archiver, 'r', modified, out / 'version.o')
    run(archiver, 's', modified)
    for name, library in [('original', source), ('modified', modified)]:
        run(compiler, *flags, '-dynamiclib', '-Wl,-install_name,@rpath/RelinkProbe.dylib',
            out / 'probe.o', library, '-o', out / (name + '.dylib'))
    original = (out / 'original.dylib').read_bytes()
    replacement = (out / 'modified.dylib').read_bytes()
    assert b'8.1.2' in original and marker.encode() in replacement and original != replacement
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    report = {'originalVendoredSHA256': before, 'vendoredLibraryUnchanged': True,
              'originalProbeSHA256': hashlib.sha256(original).hexdigest(),
              'modifiedProbeSHA256': hashlib.sha256(replacement).hexdigest(),
              'modifiedMarkerLinked': True, 'target': 'arm64-apple-ios15.0',
              'deviceExecutionPerformed': False, 'fullApplicationRelinkPerformed': False,
              'scope': 'Actual replacement of one FFmpeg object and link of a separate source-available consumer',
              'commands': commands}
    (out / 'relink-evidence.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
