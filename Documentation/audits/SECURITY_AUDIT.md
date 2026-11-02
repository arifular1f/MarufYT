# Security audit: MarufYT (branch `phase2`)

Date: 2026-11-02. Auditor: Claude for arifular1f.

**Scope:**
- the whole repository, all branches and tags, and the full Git history;
- GitHub configuration;
- GitHub Actions;
- Objective-C/C++ sources, scripts and tools;
- ROOTLESS packaging and IPA assembly;
- iOS runtime behaviour (static review).

**Method:** static review, plus the automated checks listed at the end. **No iPhone runtime testing**, so runtime behaviour is reviewed from source only.

## Summary

| Severity | Found | Fixed | Unresolved |
| --- | --- | --- | --- |
| Critical | 0 | — | — |
| High | 0 | — | — |
| Medium | 3 | 3 | 0 |
| Low | 6 | 3 | 3 (documented) |
| Informational | 7 | — | — |

There are no exposed secrets: 0 findings across 174 commits, 23 refs and 1,528 file versions (109 MB), with a positive-control test of the scanner. GitHub secret scanning reports 0 alerts.

## Findings

| ID | Severity | Area | Finding | Status |
| --- | --- | --- | --- | --- |
| M1 | Medium | Privacy / storage | The diagnostics log was written to `Documents/YTKACE/Logs`. `UIFileSharingEnabled` exposes Documents in the Files app and over USB, and device backups include it. Lines contain video IDs, file names and, with debug logging on, server response excerpts | **Fixed** `f48ad18`: moved to Application Support, excluded from backup, `NSFileProtectionCompleteUntilFirstUserAuthentication`, old copy removed once |
| M2 | Medium | Privacy / logging | No central redaction. A future or debug log line containing a URL, token or `Authorization` value would be persisted verbatim | **Fixed** `f48ad18`: every line redacts bearer tokens, URL query strings and token, key, signature, pot, password and cookie parameters |
| M3 | Medium | CI supply chain | Actions were referenced by moving tags (`@v6`, `@v4`, `@v7`). The Theos installer ran directly from `roothide/theos@master` (`curl … \| bash`). Checkout persisted the workflow token | **Fixed** `bec9bf4`: SHA-pinned actions, pinned and hash-verified installer, Theos checked out at a pinned commit, `persist-credentials: false`, per-job read-only permissions, timeouts and concurrency. Repository settings: only GitHub-owned actions allowed, SHA pinning required |
| L1 | Low | Repository settings | Dependabot alerts and updates, private vulnerability reporting and branch protection were all off | **Fixed** (GitHub settings): enabled; ruleset *Protect release branches* blocks deletion and force-push on `main`, `phase2` and `stable-*` |
| L2 | Low | Build tooling | `Scripts/build-ffmpeg.sh` downloaded the FFmpeg source without integrity verification | **Fixed**: the script now requires `FFMPEG_SHA256` and refuses a mismatch; documented signature-verification steps. The vendored `.a` hashes are recorded |
| L3 | Low | Accessibility | Player overlay buttons exposed raw internal identifiers to VoiceOver | **Fixed** `7acd384` |
| L4 | Low | Supply chain | The Theos SDK and toolchain are installed by the pinned installer from their publishers' *latest* releases, not by hash | **Unresolved (residual)**: versions are recorded in each build's `provenance.txt`. Mitigated by using the official roothide installer at a pinned commit |
| L5 | Low | Privacy | SponsorBlock segment and DeArrow lookups send the plain video ID. SponsorBlock offers a k-anonymity hash-prefix endpoint | **Unresolved (recommendation)**: changing the request and response parsing of a working feature without device testing was judged riskier than the benefit. Documented in PRIVACY.md |
| L6 | Low | Storage | The random SponsorBlock submission user ID is stored in `NSUserDefaults`, not the Keychain | **Unresolved (accepted)**: it is a SponsorBlock-only pseudonymous ID. It stays in the app sandbox and is excluded from settings backups (they export only `YTKACE.Preference.*`) |

## Informational (reviewed, no change needed)

| ID | Area | Observation |
| --- | --- | --- |
| I1 | TLS | No `ServerTrust` / `SecTrust` handling, no `NSAllowsArbitraryLoads`, no `http://` endpoints. iOS default TLS validation applies everywhere. This is now enforced by a CI check |
| I2 | Accounts | Playlist downloads reuse YouTube's live authorization. It is sent only to the hard-coded `https://youtubei.googleapis.com/youtubei/v1/browse`, over an ephemeral `NSURLSession` with cookies disabled; it is never stored, and only booleans are logged. Google sign-in itself is unchanged host code |
| I3 | Keychain | `SideloadCompatibility.mm` adds or reads one generic-password marker item (account "YTKACEDummyItem") holding no secret, only to learn the app's access group so sideloaded Google sign-in works |
| I4 | Code execution | `ChallengeSolver.mm` evaluates the bundled yt-dlp EJS solver and YouTube's player script in a bare `JSContext`. No Objective-C objects or native functions are bridged in, and the bundled solver hashes are recorded |
| I5 | Third-party data | AiSList lists are fetched only when an AI-channel option is on, over HTTPS, capped at 8 MB, and parsed into channel identifiers only. Content integrity rests on the AiSList GitHub repository; worst case is hidden or unhidden channels |
| I6 | ROOTLESS packaging | The deb installs only under `/var/jb/Library/{MobileSubstrate/DynamicLibraries, Application Support}`, has no maintainer scripts, and its filter targets `com.google.ios.youtube` only. `MarufYT.dylib` links only system libraries and frameworks. The IPA host keeps its original sections byte-for-byte; only one `LC_LOAD_DYLIB` is added, before `LC_CODE_SIGNATURE` |
| I7 | Permissions | Photos add-only access is requested only when saving. No location, contacts, camera, microphone or tracking APIs are used |

## GitHub configuration (after hardening)

**Secrets and access:**

- **Visibility:** public.
- **Secret scanning and push protection:** enabled. The non-provider-pattern and validity-check features stayed disabled after the request; they appear to need GitHub Advanced Security on this account.
- **Actions secrets and variables:** none.
- **Deploy keys and webhooks:** none.
- **Collaborators:** `arifular1f` (admin) only.

**Actions:**

- Allowed actions: GitHub-owned only.
- SHA pinning: required.
- Default token: read-only; it cannot approve pull requests.

**Code-security features:**

- Dependabot alerts: on, 0 alerts.
- Dependabot security updates: on.
- Version updates: `.github/dependabot.yml`, for GitHub Actions.
- Private vulnerability reporting: on.

**Branch protection:** ruleset *Protect release branches* blocks deletion and non-fast-forward pushes on `main`, `phase2` and `stable-*`.

## Automated checks (all passing)

| Tool | What it checks |
| --- | --- |
| `Tools/marufyt_secret_scan.py` | 11 credential patterns plus sensitive file names, over all history. Runs locally and in CI |
| `Tools/marufyt_checks.py` | 101 checks. Covers TLS overrides, cleartext endpoints, log redaction and location, workflow pinning, permissions, credential persistence, event-data injection, licences, branding and localization |
| Upstream unit tests | 5/5 |
| Release verification | Per-build verification of both IPAs (see the release's audit folder) |

## Not done

- **Dynamic testing:** no Frida, no network capture, no device. TLS behaviour, Keychain behaviour and log redaction are verified by source review and the static checks only.
- **Fuzzing:** none of the protobuf, UMP or SABR parsers or the FFmpeg inputs were fuzzed. These come from upstream and FFmpeg 8.1.2.
