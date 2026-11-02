#!/usr/bin/env python3
"""Scan every blob reachable from any ref (full Git history, all branches and
tags) for credentials and sensitive files. Read-only; standard library only.

usage: marufyt_secret_scan.py [REPORT.json]   (exit 1 on any finding)
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import json
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
                             r'\.ipa|id_rsa|id_ed25519|\.env(\..*)?|credentials\.json|\.netrc|\.npmrc)$')
# Known-safe matches (reviewed): placeholders and documentation examples.
ALLOW = [
    re.compile(rb'(?i)password["\']\s*:\s*["\']\s*["\']'),
]


def git(*args, **kw):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True, **kw).stdout


def entropy(token):
    counts = Counter(token)
    return -sum(c / len(token) * math.log2(c / len(token)) for c in counts.values())


def main():
    refs = [r for r in git('for-each-ref', '--format=%(refname)').decode().split() if r]
    objects = git('rev-list', '--objects', '--all').decode().splitlines()
    commits = int(git('rev-list', '--all', '--count').decode().strip())
    blobs = {}
    for line in objects:
        parts = line.split(' ', 1)
        if len(parts) == 2:
            blobs.setdefault(parts[0], set()).add(parts[1])
    types = git('cat-file', '--batch-check', input='\n'.join(blobs).encode()).decode().splitlines()
    blob_ids = [t.split()[0] for t in types if t.split()[1] == 'blob']
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
        if b'\0' in data[:8000]:
            continue  # binary (static libraries, images)
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(data):
                text = match.group(0)
                if any(a.search(text) for a in ALLOW):
                    continue
                if label == 'Generic secret assignment':
                    value = re.findall(rb'["\']([^"\']+)["\']', text)[-1]
                    if entropy(value) < 3.5 or re.match(rb'^[A-Za-z .]+$', value):
                        continue
                findings.append({'type': label, 'blob': blob, 'paths': sorted(blobs[blob]),
                                 'match': text[:60].decode('utf-8', 'replace') + ('…' if len(text) > 60 else '')})
    proc.stdin.close()
    proc.wait()
    report = {'refs': refs, 'commits': commits, 'blobsScanned': scanned, 'bytesScanned': sizes,
              'patterns': list(PATTERNS) + ['sensitive file names'], 'findings': findings}
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(report, indent=1), encoding='utf-8')
    print(f"refs={len(refs)} commits={commits} blobs={scanned} bytes={sizes:,} findings={len(findings)}")
    for f in findings:
        print(' ', f)
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
