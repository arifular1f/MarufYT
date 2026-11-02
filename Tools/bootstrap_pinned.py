#!/usr/bin/env python3
"""Verified, non-install-script Theos bootstrap for fresh Linux CI workspaces.
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import argparse
import hashlib
import json
import platform
import re
import subprocess
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def validate_lock(lock):
    if lock['schema'] != 1 or not re.fullmatch(r'[a-f0-9]{40}', lock['theos']['commit']):
        raise ValueError('Invalid source pin')
    for item in [lock['theos']] + lock['theos']['submodules']:
        if not item['url'].startswith('https://github.com/') or not re.fullmatch(r'[a-f0-9]{40}', item['commit']):
            raise ValueError('Unpinned or non-HTTPS source')
    for item in lock['archives']:
        if not item['url'].startswith('https://github.com/') or '/releases/download/' not in item['url'] or '/latest/' in item['url']:
            raise ValueError('Archive requires a versioned publisher URL')
        if not re.fullmatch(r'[a-f0-9]{64}', item['sha256']) or item['bytes'] <= 0:
            raise ValueError('Invalid archive integrity pin')
        if PurePosixPath(item['prefix']).is_absolute() or '..' in PurePosixPath(item['prefix']).parts:
            raise ValueError('Unsafe archive prefix')


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def verified_download(item, cache):
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (item['sha256'] + '.tar.xz')
    if not path.exists():
        pending = path.with_suffix('.pending')
        request = urllib.request.Request(item['url'], headers={'User-Agent': 'MarufYT-pinned-bootstrap'})
        with urllib.request.urlopen(request, timeout=60) as source, pending.open('wb') as dest:
            while chunk := source.read(1024 * 1024):
                dest.write(chunk)
        if pending.stat().st_size != item['bytes'] or sha(pending) != item['sha256']:
            pending.unlink()
            raise ValueError('Downloaded archive integrity mismatch')
        pending.rename(path)
    if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
        raise ValueError('Cached archive integrity mismatch; refusing extraction')
    return path


def safe_extract(path, destination, prefix):
    with tarfile.open(path) as archive:
        entries = archive.getmembers()
        if len(entries) > 100000 or sum(m.size for m in entries) > 2 * 1024 ** 3:
            raise ValueError('Archive exceeds extraction bounds')
        for member in entries:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or '\\' in member.name:
                raise ValueError('Unsafe archive member')
            if not (member.name == prefix or member.name.startswith(prefix + '/')):
                # Compiler archive has directory ancestors such as linux/.
                if not member.isdir() or not prefix.startswith(member.name.rstrip('/') + '/'):
                    raise ValueError('Unexpected archive tree')
        archive.extractall(destination, filter='data')


def command(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True, encoding='utf-8').strip()


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--theos', type=Path, default=ROOT / '.theos')
    args.add_argument('--cache', type=Path, default=ROOT / '.toolchain-downloads')
    args.add_argument('--report', type=Path, default=ROOT / 'toolchain-provenance.json')
    opts = args.parse_args()
    lock = json.loads((ROOT / 'Tools/toolchain.lock.json').read_text())
    validate_lock(lock)
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise RuntimeError('This lock targets Linux x86_64; no platform substitution is allowed')
    target = opts.theos.resolve()
    if target.exists() and any(target.iterdir()):
        raise RuntimeError('Requires a fresh Theos destination; cached executable trees are not reused')
    target.mkdir(parents=True, exist_ok=True)
    command('git', 'init', '-q', str(target))
    command('git', 'remote', 'add', 'origin', lock['theos']['url'], cwd=target)
    command('git', 'fetch', '--depth', '1', 'origin', lock['theos']['commit'], cwd=target)
    command('git', 'checkout', '--detach', 'FETCH_HEAD', cwd=target)
    for item in lock['theos']['submodules']:
        tree = command('git', 'ls-tree', 'HEAD', item['path'], cwd=target)
        if tree.split()[2] != item['commit']:
            raise ValueError('Submodule gitlink differs from reviewed lock')
    command('git', '-c', 'protocol.file.allow=never', '-c', 'protocol.ssh.allow=never',
            'submodule', 'update', '--init', '--recursive', '--depth', '1', cwd=target)
    status = command('git', 'submodule', 'status', '--recursive', cwd=target)
    if any(line.startswith(('+', '-', 'U')) for line in status.splitlines()):
        raise ValueError('Submodule checkout does not match pinned gitlinks')
    installed = []
    for item in lock['archives']:
        archive = verified_download(item, opts.cache)
        destination = target / ('toolchain' if item['role'] == 'compiler' else 'sdks')
        destination.mkdir(exist_ok=True)
        safe_extract(archive, destination, item['prefix'])
        installed.append({'role': item['role'], 'url': item['url'], 'sha256': sha(archive), 'bytes': archive.stat().st_size})
    compiler = target / 'toolchain/linux/iphone/bin/clang'
    report = {'theosCommit': command('git', 'rev-parse', 'HEAD', cwd=target),
              'submodules': status.splitlines(), 'archives': installed,
              'clangVersion': command(str(compiler), '--version'),
              'hostPackages': command('dpkg-query', '-W', '-f=${Package}=${Version}\n',
                                      'git', 'make', 'libxml2', 'libtinfo6', 'fakeroot', 'xz-utils'),
              'unavoidableHostComponents': lock['host']['residuals'],
              'installerOrLatestResolverExecuted': False}
    opts.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
