# Security policy

MarufYT is maintained by [arifular1f](https://github.com/arifular1f).

## Report privately

Use [GitHub private vulnerability reporting](https://github.com/arifular1f/MarufYT/security/advisories/new). Include the exact tweak/YouTube versions, signing/install method, reproduction and redacted evidence. Never post live tokens, passwords, signing keys or account/session dumps. Upstream YTKACE issues should also be reported privately to the upstream maintainer.

## Current revision and older builds

The coordinated update is **1.1.4+marufyt.8** on `final-update-security`, based on Phase 4.1 `657aed1`. `main`, `phase2` and preserved release branches are not promoted or rewritten. Older builds remain available for reproducibility/rollback and retain their historical findings; no backport or runtime-safety guarantee is implied. See the [pre-fix .7 audit](Documentation/FINAL_SECURITY_AUDIT/FINAL_SECURITY_REPORT.md) and [current evidence](Documentation/FINAL_UPDATE/FINAL_UPDATE_REPORT.md).

## Current controls

- **F-01:** no authenticated request seed or raw outgoing protobuf dump is intentionally persisted by the patched paths. Exact legacy files are purged on initialization/account boundaries; in-memory state has inactivity expiry and boundary cleanup. This does not erase copies already made or revoke Google credentials.
- **F-02:** SABR destinations and both HTTP/protobuf redirects are restricted to HTTPS Google video media origins. Native header replay is allowlisted and excludes Authorization/Cookie. Generic cross-origin redirects discard sensitive/unrecognized headers and reject request-body replay.
- **F-03:** MarufYT remote task construction rejects non-HTTPS URLs, URL userinfo and nonstandard ports; local filesystem/media imports remain separate. This policy does not globally override YouTube's own sessions. The original host still has ATS local-network/carrier exceptions.
- **F-04:** diagnostics are opt-in; opaque object values/raw server payloads are not interpolated. Known credentials, URL/email/video-ID formats are omitted, log identifiers are constrained, and line breaks are normalized. No generic filter guarantees arbitrary text is free of personal data.
- **Accounts:** Google authentication remains the host's implementation with existing sideload compatibility hooks. New cleanup wrappers call original native methods and clear only MarufYT state. Real login/logout/account switching and the coverage of private methods require iPhone testing.
- **Storage:** media/settings remain in the app sandbox/Files-visible download tree. Diagnostics separately request protected Application Support storage and backup exclusion. OS protection, fallback paths, signing entitlements and existing backups require runtime verification.
- **Code:** Objective-C runtime hooks and JavaScriptCore player-script processing exist. Neither name guards nor a clean import list proves safe execution of all proprietary/third-party code.

## Build and repository integrity

Actions use full SHA pins, a read-only token and non-persisted checkout credentials. No repository secrets are required. The Theos/compiler/SDK integrity lock remains in `Tools/toolchain.lock.json`; fresh tooling is used with hash-verified archive caching. Hosted images/apt packages are moving residuals. CI runs existing tests, focused source contracts, actual macOS Foundation security fixtures, full reachable-history secret scanning and the ROOTLESS build. Native policy tests do not run YouTube or an iPhone.

No original YouTube IPA/DEB, signer credential or live token is committed. Generated host IPAs remain local. Verify artifact SHA256 manifests against the exact source/run; do not rely on an unrelated latest/default-branch build. Dependabot schedule/default-branch limitations remain documented in the historical audits; no default-branch change is implied.

## Limits

Device traffic/TLS capture, signing/provisioning validation, Google session behavior, permission prompts, backup/file-protection checks, malformed-response/media fuzzing and memory-safety profiling remain open unless separately evidenced. New policy guards may reject an unsupported CDN or require a download retry rather than forwarding session material unsafely. The project does not claim 100% security or zero host tracking. [PRIVACY.md](PRIVACY.md) details data flows; [installation](Documentation/INSTALLATION.md) covers migration.
