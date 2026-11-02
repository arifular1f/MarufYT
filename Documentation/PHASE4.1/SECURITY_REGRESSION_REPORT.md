# Security Regression Report (Phase 4.1)

Compared build `1.1.4+marufyt.7` (CI run `41434077642`) with `.6` (Phase 4, run `41432137516`).

| Check | Method | Result |
| --- | --- | --- |
| New secrets | Full-history scan: 31 refs, 192 commits, 1,701 blobs | **0 findings** |
| New tracking / identifiers | String scan of both dylibs for `advertisingIdentifier`, `identifierForVendor`, `CLLocationManager`, `CNContactStore`, `NSLog`, and Firebase, Crashlytics, Sentry, Mixpanel, Amplitude, AppsFlyer | None in either build |
| Unexpected network endpoints | Host set extracted from both dylibs | **Identical**; no host added or removed. The only new URL string in the diff is the SponsorBlock route extended with a path component on the same host |
| Permissions | Info.plist produced by the packager is unchanged by this phase (no packager change); no new usage description | No change |
| Insecure image / caption requests | `MarufYTIsSecureURL` still guards avatar, post-image and caption fetches; static check in `marufyt_checks.py` | Pass |
| Unsafe file handling | New code writes nothing to disk; artwork cache is in memory only; diagnostics-log path unchanged | No new file operations |
| Command execution / dynamic loading | Symbol scan of both dylibs for `system`, `popen`, `posix_spawn`, `execve`, `fork`, `dlopen`, `ptrace` | None imported. (A raw `_system` byte match is the embedded text label `sound_system`, not an import) |
| SHA-256 implementation | Own header-only code (no CommonCrypto) with native known-answer tests in CI | Pass; used only to derive an opt-in 4-character prefix, not for security decisions |
| Google sign-in, account switching | Not touched: no change to `SideloadCompatibility.mm`, keychain use or URL schemes; `verify_release.py` confirms the SSO scheme is present in both IPAs | Static pass; **Not tested** on a device |
| Auth tokens in logs | `YTKACERedactLogMessage` unchanged and still in the log path; new code logs nothing | Pass (static) |
| Licences and attribution | `LICENSE`, `THIRD_PARTY_NOTICES.md`, `UPSTREAM_README.md` untouched | Pass |
| Release integrity | `verify_release.py` 40/40 on each IPA; the four `ipa file/` inputs match their recorded checksums | Pass |

## Newly introduced behaviour to be aware of

- **Private Lookup** adds a second request shape to `sponsor.ajay.app` when the user enables it. It transmits less than the default form. See `SPONSORBLOCK_PRIVACY_REPORT.md`.
- The artwork cache holds decoded album art in memory (bounded).

## Still open from Phase 4

Dynamic network capture; Authorization-header handling on redirects (S-03); memory-safety tooling (S-11); the muxer wait without a timeout (low). No new vulnerability was found in this phase, but this is a static review: it does not prove the absence of vulnerabilities.
