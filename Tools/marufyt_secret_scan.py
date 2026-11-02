#!/usr/bin/env python3
"""Scan every blob reachable from any ref (full Git history, all branches and
tags) for credentials and sensitive files. Read-only; standard library only.

usage: marufyt_secret_scan.py [REPORT.json]   (exit 1 on any finding)
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import json
import hashlib
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = {
    'GitHub token': re.compile(rb'\b(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b'),
    'AWS access key': re.compile(rb'\b(AKIA|ASIA)[0-9A-Z]{16}\b'),
    'Google API key': re.compile(rb'\bAIza[0-9A-Za-z_\-]{35}\b'),
    'Google OAuth client secret': re.compile(rb'\bGOCSPX-[0-9A-Za-z_\-]{28}\b'),
    'Slack token': re.compile(rb'\bxox[abposr]-[0-9A-Za-z-]{10,}\b'),
    'Stripe key': re.compile(rb'\b(sk|rk)_live_[0-9A-Za-z]{20,}\b'),
    'Private key block': re.compile(rb'-----BEGIN (RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY'),
    'JWT': re.compile(rb'\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b'),
    'Discord webhook': re.compile(rb'discord(app)?\.com/api/webhooks/\d+/[\w-]+'),
    'Generic secret assignment': re.compile(
        rb'(?i)\b(api[_-]?key|secret|passwd|password|access[_-]?token|auth[_-]?token|client[_-]?secret)\b'
        rb'\s*[:=]\s*["\'][^"\'\s]{12,}["\']'),
    'URL with credentials': re.compile(rb'https?://[^/\s:@"\']{3,}:[^/\s:@"\']{6,}@'),
}
SENSITIVE_FILES = re.compile(r'(?i)(\.p12|\.pfx|\.mobileprovision|\.cer|\.der|\.pem|\.key|\.keystore|\.jks|'
                             r'\.ipa|\.p8|id_rsa|id_ed25519|\.env(\..*)?|credentials\.json|\.netrc|\.npmrc)$')
# Known-safe matches (reviewed): placeholders and documentation examples.
ALLOW = [
    re.compile(rb'(?i)password["\']\s*:\s*["\']\s*["\']'),
]


def git(*args, **kw):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True, **kw).stdout


def entropy(token):
    counts = Counter(token)
    return -sum(c / len(token) * math.log2(c / len(token)) for c in counts.values())


def scan_bytes(data, paths, **metadata):
    """Return locations/fingerprints only: never include matched credential bytes."""
    findings = []
    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(data):
            text = match.group(0)
            if any(a.search(text) for a in ALLOW):
                continue
            if label == 'Generic secret assignment':
                value = re.findall(rb'["\']([^"\']+)["\']', text)[-1]
                if entropy(value) < 3.5 or re.match(rb'^[A-Za-z .]+$', value):
                    continue
            findings.append({'type': label, 'paths': sorted(paths), **metadata,
                             'byteOffset': match.start(),
                             'matchSHA256': hashlib.sha256(text).hexdigest()})
    return findings


def collect_blob_paths():
    # rev-list --objects supplies only one representative name for a shared
    # object. Inspect every unique committed tree so benign content committed
    # again as .env or a certificate cannot evade the filename check.
    trees = set(git('log', '--all', '--format=%T').decode().split())
    blobs = {}
    for tree in trees:
        for entry in git('ls-tree', '-r', '-z', tree).split(b'\0'):
            if not entry:
                continue
            metadata, name = entry.split(b'\t', 1)
            _, kind, oid = metadata.split()
            if kind == b'blob':
                blobs.setdefault(oid.decode(), set()).add(name.decode('utf-8', 'surrogateescape'))
    # Include staged versions, even when they differ from the working file.
    for entry in git('ls-files', '--stage', '-z').split(b'\0'):
        if not entry:
            continue
        metadata, name = entry.split(b'\t', 1)
        _, oid, _ = metadata.split()
        if set(oid) != {48}:  # intent-to-add has no object yet
            blobs.setdefault(oid.decode(), set()).add(name.decode('utf-8', 'surrogateescape'))
    return blobs


def main():
    if git('rev-parse', '--is-shallow-repository').strip() != b'false':
        print('ERROR: full-history scan requires a non-shallow checkout (fetch-depth: 0).')
        return 2
    refs = [r for r in git('for-each-ref', '--format=%(refname)').decode().split() if r]
    commits = int(git('rev-list', '--all', '--count').decode().strip())
    blobs = collect_blob_paths()
    blob_ids = sorted(blobs)
    findings, scanned, sizes = [], 0, 0
    for name_set in (blobs[b] for b in blob_ids):
        for name in name_set:
            if SENSITIVE_FILES.search(name):
                findings.append({'type': 'sensitive file name', 'path': name})
    proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for blob in blob_ids:
        proc.stdin.write(blob.encode() + b'\n')
        proc.stdin.flush()
        header = proc.stdout.readline().split()
        size = int(header[2])
        data = proc.stdout.read(size)
        proc.stdout.read(1)
        scanned += 1
        sizes += size
        findings.extend(scan_bytes(data, blobs[blob], blob=blob, scope='history-or-index'))
    proc.stdin.close()
    proc.wait()
    proc.stdout.close()
    if proc.returncode:
        raise RuntimeError('Git blob reader failed; scan coverage is incomplete')
    # Scan visible working files as well as committed/staged versions. Never
    # follow symlinks to private files outside the checkout.
    visible = set(git('ls-files', '-z').split(b'\0')) | set(git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0'))
    working_count = 0
    for raw in sorted(visible):
        if not raw:
            continue
        name = raw.decode('utf-8', 'surrogateescape')
        path = ROOT / name
        if path.is_symlink():
            findings.append({'type': 'unscanned symlink', 'path': name, 'scope': 'working-tree'})
            continue
        if not path.is_file():
            continue
        if SENSITIVE_FILES.search(name):
            findings.append({'type': 'sensitive file name', 'path': name, 'scope': 'working-tree'})
        findings.extend(scan_bytes(path.read_bytes(), [name], scope='working-tree'))
        working_count += 1
    report = {'refs': refs, 'commits': commits, 'blobsScanned': scanned, 'bytesScanned': sizes,
              'workingFilesScanned': working_count, 'binaryContentScanned': True,
              'reportsContainSecretValues': False,
              # DEBs are not credentials. Track artifact-policy evidence
              # separately; upstream gh-pages refs can legitimately contain them.
              'packageArtifactPaths': sorted({p for paths in blobs.values() for p in paths if p.lower().endswith('.deb')}),
              'patterns': list(PATTERNS) + ['sensitive file names'], 'findings': findings}
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(report, indent=1), encoding='utf-8')
    print(f"refs={len(refs)} commits={commits} blobs={scanned} bytes={sizes:,} findings={len(findings)}")
    for f in findings:
        print(' ', f)
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
