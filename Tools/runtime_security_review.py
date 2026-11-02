#!/usr/bin/env python3
"""Static review evidence and a Python model of selected native regex patterns.
Does not run Foundation, Keychain, YouTube, networking or an iPhone.
Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    names = ['Downloads/DownloadLog.mm', 'Downloads/PlaylistDownloader.mm',
             'Downloads/YTKACEBackupManager.mm', 'Playback/ChallengeSolver.mm',
             'Compatibility/SideloadCompatibility.mm', 'SponsorBlock/SponsorClient.mm']
    files = {}
    for name in names:
        path = ROOT / 'Tweak/Features' / name
        files[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    log = (ROOT / 'Tweak/Features/Downloads/DownloadLog.mm').read_text()
    literals = re.findall(r'regularExpressionWithPattern:\s*@"((?:\\.|[^"\\])*)"', log)
    patterns = [re.compile(json.loads('"' + s + '"'), re.I) for s in literals]
    if len(patterns) != 3:
        raise ValueError('Native regex set changed; review the model before using its evidence')
    replacements = ['[URL omitted]', '[email omitted]', '[identifier omitted]']
    # Synthetic fixtures only. No real tokens or requests are used.
    fixtures = [('bearer', 'Bearer fixture-value', True),
                ('url-query', 'https://example.invalid/path?token=fixture-value', True),
                ('key-value', 'access_token=fixture-value', True),
                ('json-field', '{"access_token":"fixture-value"}', True),
                ('cookie-header', 'Cookie: session=fixture-value', True)]
    cases = []
    for label, text, expected in fixtures:
        markers = ['authorization', 'bearer', 'cookie', 'token', 'password', 'secret', 'api_key', 'api-key', 'apikey', 'signature', 'session=', 'key=', 'pot=', '{', '}', 'response=', 'body=', '/var/', '/private/', '/users/']
        redacted = '[sensitive diagnostic omitted]' if any(m in text.lower() for m in markers) else text
        for pattern, replacement in zip(patterns, replacements):
            redacted = pattern.sub(replacement, redacted)
        cases.append({'case': label, 'syntheticValueRemoved': 'fixture-value' not in redacted,
                      'reviewedExpectedCoverage': expected})
    result = {'method': 'Static source review with Python regex approximation; not ICU/Foundation execution',
              'sourceFiles': files, 'logPatternCoverageModel': cases,
              'knownUncoveredFormatsRemain': 'No guarantee for arbitrary unlabeled secrets; native policy tests run separately in macOS CI', 'identifierRedactionProven': False,
              'redirectCredentialPolicyRuntimeVerified': False,
              'backupAndKeychainRuntimeVerified': False,
              'parserFuzzingPerformed': False, 'iPhoneRuntimeTestingPerformed': False}
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
