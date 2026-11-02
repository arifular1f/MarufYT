# Security policy

MarufYT is maintained by [arifular1f](https://github.com/arifular1f).

## Reporting a vulnerability

Report security problems **privately** through GitHub's private vulnerability reporting:
**https://github.com/arifular1f/MarufYT/security/advisories/new**

Please do not open a public issue for a vulnerability. Include:

- the affected version (MarufYT settings → About → Version);
- the YouTube version;
- the install method;
- reproduction steps.

You will get an acknowledgement as soon as possible.

**Upstream issues:** a problem that also affects upstream YTKACE should also be reported to https://github.com/itzzace/ytkace.

## Supported versions

| Version | Branch | Supported |
| --- | --- | --- |
| 1.1.4+marufyt.x | `phase2` | Yes (current development) |
| 1.1.1+marufyt.1 | `main`, `stable-21.39.4` | Security fixes only, until `phase2` is promoted |

## What this repository never contains

- No YouTube or other Google application binaries (decrypted or not). IPAs are assembled locally from a copy you supply.
- No signing certificates, provisioning profiles, private keys, API keys or tokens.
  - CI checks every change with `Tools/marufyt_secret_scan.py` (full history).
  - GitHub secret scanning and push protection are enabled.

## Build integrity

- **GitHub Actions:**
  - every action is pinned to a full commit SHA;
  - the workflow token is read-only, and credentials are not persisted on the runner;
  - no repository secrets are used;
  - untrusted event data is never interpolated into shell commands.
- **Theos:** the installer is downloaded from a pinned commit and verified by SHA-256 before it runs, and Theos is checked out at that commit. The SDK and toolchain versions used are recorded in each build's `provenance.txt`.
- **Dependabot:** proposes action updates as pull requests; nothing is merged automatically.
- **Artifact checksums:** every CI artifact ships with `SHA256SUMS.txt`. Verify downloaded files against it.

## Runtime security design

| Area | Behaviour |
| --- | --- |
| Network | HTTPS only. No custom certificate or trust handling and no App Transport Security exceptions; iOS validates TLS normally |
| Accounts | Google sign-in is YouTube's own. MarufYT never asks for, stores or transmits credentials. Playlist downloads reuse YouTube's current authorization only for requests to `youtubei.googleapis.com`, over an ephemeral session without cookies; it is never logged or stored |
| Keychain | One non-secret marker item, used only to read the app's Keychain access group so sideloaded sign-in works |
| Code execution | YouTube's own player script is evaluated in an isolated JavaScriptCore context with no native objects exposed (stream challenge solving) |
| Storage | Settings in the app sandbox. Downloads in `Documents/YTKACE` (visible in Files by design). Diagnostics log in Application Support: excluded from backup, file-protected, with tokens and URL query strings redacted |
| Hooks | Objective-C runtime hooks are installed by name; a missing class or selector is skipped instead of crashing |

## Known limitations

See `Documentation/audits/SECURITY_AUDIT.md`.
