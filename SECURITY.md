# Security policy

MarufYT is maintained by [arifular1f](https://github.com/arifular1f).

## Reporting a vulnerability

Report security problems **privately** through GitHub's private vulnerability reporting:
**[Open a private security report](https://github.com/arifular1f/MarufYT/security/advisories/new)**

Please do not open a public issue for a vulnerability. Include:

- the affected version (MarufYT settings → About → Version);
- the YouTube version;
- the install method;
- reproduction steps.

You will get an acknowledgement as soon as possible.

**Upstream issues:** a problem that also affects upstream YTKACE should also be reported to [the upstream project](https://github.com/itzzace/ytkace).

## Supported versions

| Version | Branch | Supported |
| --- | --- | --- |
| 1.1.4+marufyt.x | `phase2` | Yes (current development) |
| 1.1.1+marufyt.1 | `main`, `stable-21.39.4` | Security fixes only, until `phase2` is promoted |

## What this repository never contains

- No YouTube or other Google application binaries (decrypted or not). IPAs are assembled locally from a copy you supply.
- No signing certificates, provisioning profiles, private keys, API keys or tokens.
  - The `phase2` workflow checks its checkout with `Tools/marufyt_secret_scan.py` (full reachable history, index and visible working files, including binary content). Findings contain locations and hashes, never matched credential text.
  - GitHub secret scanning and push protection are enabled.

## Build integrity

- **GitHub Actions (`phase2` workflow):**
  - every action is pinned to a full commit SHA;
  - the workflow token is read-only, and credentials are not persisted on the runner;
  - no repository secrets are used;
  - untrusted event data is never interpolated into shell commands.
- **Theos (`phase2`):** a fresh detached checkout and reviewed submodule gitlinks are installed directly. Versioned compiler/SDK archives are size/hash checked before extraction or execution. The moving installer is not run. See `Tools/toolchain.lock.json` and the toolchain audit; hosted image and apt packages remain explicitly recorded residuals.
- **Dependabot:** repository alerts/security updates are enabled. Weekly action-update configuration is prepared on `phase2`, but is not active while it is absent from the default branch. `main` is intentionally unchanged; no default-branch change or promotion is implied.
- **Artifact checksums:** every CI artifact ships with `SHA256SUMS.txt`. Verify downloaded files against it.

## Runtime security design

| Area | Behaviour |
| --- | --- |
| Network | HTTPS only. No custom certificate or trust handling and no App Transport Security exceptions; iOS validates TLS normally |
| Accounts | Google sign-in is YouTube's own; MarufYT has no Google-password form. Playlist code uses the host's authorization in memory for HTTPS requests to `youtubei.googleapis.com`, over an ephemeral session without cookies. No credential persistence was found in that path; redirect and session behaviour still require device testing |
| Keychain | One non-secret marker item, used only to read the app's Keychain access group so sideloaded sign-in works |
| Code execution | Player script evaluation uses a JavaScriptCore context; no native bridge was found in the reviewed code. This is in the app process, not a separately verified sandbox or resource-limit boundary |
| Storage | Settings in the app sandbox. Downloads in `Documents/YTKACE` (visible in Files by design). Diagnostics log in Application Support: excluded from backup, file-protected, with tokens and URL query strings redacted |
| Hooks | Objective-C runtime hooks are installed by name; a missing class or selector is skipped instead of crashing |

## Known limitations

See `Documentation/audits/COMPLETION_AUDIT.md` for the follow-up findings and `Documentation/audits/SECURITY_AUDIT.md` for the earlier audit. Neither static checks nor a clean credential scan certify that all runtime logging formats are redacted. JSON token fields, cookie headers, log identifiers and redirects need separate runtime coverage. The frozen `main` workflow retains its older configuration; its action tags may conflict with the repository's SHA-pinning policy. No branch was promoted to address this.

Current disposition: `Documentation/audits/FINDING_DISPOSITION.md`. Audit-only branch dispatch validates tooling and isolated relinking without a release rebuild. Exact signed FFmpeg source and corresponding-source/relink documentation are recorded separately; a source signature is not a claim of vulnerability-free code or historical bit reproducibility.
