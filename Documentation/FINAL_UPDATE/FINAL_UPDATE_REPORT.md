# MarufYT — coordinated application and repository update

Date: 2026-11-03 (Asia/Kuala_Lumpur). Version: **1.1.4+marufyt.8**.
Developer: arifular1f. Package: `com.arifular1f.marufyt`.
Host bundle: `com.google.ios.youtube`. Branch: `final-update-security`.
Baseline: Phase 4.1 `657aed16a3bc51f5bb41aa4d33d89fe4d343d4ff`.
Tested/compiled revision: **`c5f3dc3f8aa2205053b27029f2e73552d80fae28`**.

Implementation, source/documentation publication, CI and independent structural
verification of both unsigned IPAs are complete. Actual signed iPhone runtime
acceptance remains **NOT TESTED**. This is one coordinated update, not a new
project phase, UI redesign, or certification that the application is 100% secure.

## 1. Security fixes and evidence

| Finding | Implemented change | Evidence / limits |
| --- | --- | --- |
| F-01 — request-data storage | Removed authenticated seed serialization/restoration and the raw outgoing protobuf dump. Capture stays in memory. Exact old seed files are queued for deletion from Documents/Application Support/Caches YTKACE roots; media/settings are not deleted. Lazy 15-minute inactivity expiry covers captured-state getters; active download requests refresh liveness. Recognized account boundaries clear captured player/SABR/playlist authorization state, standalone client metadata and cancel active SABR sessions | `Runtime/SecurityLifecycle.h/.mm`, `NetworkRules.h`, `Entry.mm`, `DownloadHooks.mm`, `SABRDownloader.mm`, `PlaylistDownloader.mm`. Foundation fixtures execute exact legacy-file cleanup while preserving settings/media, expiry predicates and boundary wrappers. File protection/deletion failures, already copied files/backups, native host token storage and real logout coverage require device verification |
| F-02 — URL and credential routing | Initial SABR and custom/HTTP redirect URLs require trusted HTTPS Google video origins. Native media-header replay is allowlisted, excluding Authorization/Cookie and unknown headers. Generic cross-origin redirects remove service/identity headers and refuse body/stream replay; same-origin requests retain legitimate authentication | `Runtime/URLPolicy.h/.mm`, `NetworkRules.h`, SABR/custom task delegates. Foundation checks cover hostile suffixes, encoded host ambiguity, userinfo/ports, body replay, sensitive headers and allowed CDN redirects. No live traffic/redirect or Google token test was performed |
| F-03 — remote HTTPS | Guarded client rejects invalid/non-HTTPS/schemeless initial URLs asynchronously; completion-based callers receive an error rather than hanging. All formerly shared MarufYT sessions use the client; fixed API sessions and custom task delegates have redirect policy. StreamResolver/download-task entry points reject HTTP. Local filesystem/media import APIs remain separate | No host-wide NSURLSession hook or certificate-trust bypass. Foundation tests cover unsafe and valid URL forms plus asynchronous rejection. Original YouTube sessions, ATS carrier exceptions, AVFoundation-internal traffic and third-party code are not globally controlled |
| F-04 — diagnostics | Normal and debug logs now require the existing opt-in Debug Logs preference. Opaque formatted objects/C strings/pointers are not interpolated; event templates/numeric diagnostics remain. Known credential/raw JSON/response formats are omitted; URL/email/video-ID-shaped strings are filtered; identifiers constrained and line breaks normalized. Old log removed once during log-format migration | `DownloadLog.h/.mm`, `SecurityLifecycle.mm`; native Foundation redaction fixtures and source contracts. No log uploader added. Filtering does not certify arbitrary unlabeled text or historical copies are secret-free |

Account boundary selection is deliberately small, not a scan/hook of every host
class. Read-only Objective-C metadata inspection of **both** original host binaries
found `YTIdentityControllerImpl signOut` (`v16@0:8`) and
`SSODefaultAccountListViewController setSelectedIdentity:` (`v24@0:8@16`). Runtime
installation still verifies method ownership, void return and object argument ABI;
optional removal variants are skipped if unavailable/incompatible. Opening a picker
or reassigning its same identity does not purge state; a changed identity does.
Original native account methods/callbacks still run. Fixture tests exercise these
wrapper rules, not Google's implementation. Presence of a method is not proof of
every device account-transition path executing it.

## 2. Application changes and preservation

The `.8` package preserves the original host identity, ROOTLESS layout and loader
dependencies. No Google-password form, new activation/account service, entitlement
forgery, unrelated feature or appearance change was introduced. SponsorBlock normal/
Private Lookup, DeArrow, AiSList, downloads, playback and customization source paths
remain; their network tasks now use the security policy. No new external service,
vendored binary, certificate, token or private configuration was added.

All **239 compiled .7 preference keys** remain. Every non-dylib DEB payload resource
is byte-identical to `.7`. For **each** host IPA, the only archive member whose bytes
change from `.7` is `Payload/YouTube.app/Frameworks/MarufYT.dylib`; no member is added
or removed. Host executable, Info.plist/permissions, signing metadata, frameworks,
extensions and resource files remain byte-identical. Original input host Mach-O
section hashes also match. This is preservation evidence, not a feature runtime pass.

Authenticated stream templates are intentionally not restored after process restart.
Playback must refresh native state; a download may require retry after expiry or
account change. Clearing MarufYT memory does not revoke Google's server-side tokens,
delete native Google accounts or recall existing shared files/backups. No continuous
cleanup timer, new telemetry or extra background polling was introduced.

## 3. GitHub repository changes

README now identifies `.8`, the working branch and matching CI rather than an
unrelated/default-branch run. Updated: installation/migration/rollback instructions,
build instructions, compatibility limits, Security/Privacy, changelog, provenance
and documentation index. The pre-fix audit and useful prior phase history remain
available and explicitly historical. Release notes accompany this report.

No genuine current screenshots were supplied; no new screenshot gallery or test
image was fabricated. Existing upstream assets/credits and MIT/LGPL notices remain.
No original IPA/DEB or signer material was pushed. CI uploads only the compiled
tweak package/dylib and provenance. Repository/source changes are on
`final-update-security`; the default `main` landing page remains unchanged because
no promotion/merge was authorized.

## 4. Latest and Stable build results

Output directory, relative to the existing workspace:
`release/MarufYT-FinalUpdate-1.1.4+marufyt.8/`.

The pinned existing Theos workflow compiled **93 arm64 source files**, zero compiler
`warning:` or `error:` diagnostics, and produced the ROOTLESS `.8` DEB/dylib.
Theos reports that optional XML-plist optimization tools are absent; the package
is still valid. Two independent IPA assembly/verification runs used each original
host input and the same compatible host-adaptive tweak. A second identical native
compilation per host was unnecessary and is not claimed.

Both IPAs pass **40/40 structural checks**, including identity/version, CRC, original
host sections/length, Google SSO scheme, load commands/injection, system-only dylib
dependencies, ROOTLESS resources and packaged dylib matching the DEB. The separate
14-check review also confirms `.7` preferences/resources/host-file preservation,
new compiled policy markers/classes, original-package preservation and CI provenance.

The old verifier initially reported 39/40 because three SDK selectors disappeared
after the intended fixes: authenticated-seed serialization/restoration methods and
the delegate-less session factory. They are now explicit documented removals;
the new omission marker replaces its obsolete redaction-regex string sentinel.
No identity, feature-preference, host-section, architecture or injection check was
removed. Initial receipts and verifier notes are retained in the new output tree.

## 5. Test results

| Check | Actual result |
| --- | --- |
| Existing + focused Python suite | CI: **30/30 PASS**, including native C wrapper tests; local Windows: 28 passed / 2 skipped because no C compiler |
| Existing static source checks | **136/136 PASS** |
| Actual macOS Foundation policy/lifecycle fixtures | **55 checks, 0 failures**; shipped policy/log/lifecycle code, controlled files/requests and hook/clear stubs; no YouTube/iPhone execution |
| Focused source contracts | Assert no seed writes/raw dump, expiry/boundary cleanup, initial/custom/HTTP redirect guards, no unguarded shared sessions and opt-in/object-safe diagnostics |
| Repository secret scan in final source CI | 9 refs / 198 reachable commits / 1759 blobs: **0 findings**; scoped to refs in that checkout |
| Downloaded CI artifact manifest | **5/5 hashes match** |
| Latest IPA verification | **40/40 PASS** |
| Stable IPA verification | **40/40 PASS** |
| Additional package/security regression review | **14/14 PASS** |
| Preserved existing/original IPA and DEB files | **35/35 unchanged** from the pre-update hash snapshot |

Full raw logs and verification JSON are local release evidence. Static contracts
and synthetic fixtures do not replace native application integration, traffic
capture, backup/protection tests or memory-safety tooling.

## 6. GitHub Actions status

**SUCCESS:** [Build run 41541646237](https://github.com/arifular1f/MarufYT/actions/runs/41541646237),
source `c5f3dc3f8aa2205053b27029f2e73552d80fae28`. All three jobs succeeded:
Linux tests/scan, macOS Foundation security and ROOTLESS build/artifact upload.
Action SHA pins, read-only permissions, non-persisted credentials and compiler/SDK/
Theos lock remain. The build now waits for the Foundation tests as well as Linux.

An earlier full-build attempt failed to link the playlist-clear export because
its implementation lacked the shared C-linkage header. That was fixed in `06025cc`;
the final full build above verifies resolution. Superseded/cancelled runs are not
release evidence. Subsequent report-only publication does not change compiled
source, tests, build tooling or workflow; that equality is checked before handoff.

## 7. Exact IPA paths and SHA256

Paths are relative to the workspace root (`ios App`), not public download URLs:

| Artifact | Exact path | SHA256 |
| --- | --- | --- |
| Latest unsigned IPA | `release/MarufYT-FinalUpdate-1.1.4+marufyt.8/Latest-YouTube-21.43.5/MarufYT-1.1.4+marufyt.8-YouTube-21.43.5-ROOTLESS-signing-required.ipa` | `576ca959641e5ba1c285c422d19b1e545d5f838b36a8be7109564b22b2cb46e8` |
| Stable unsigned IPA | `release/MarufYT-FinalUpdate-1.1.4+marufyt.8/Stable-YouTube-21.39.4/MarufYT-1.1.4+marufyt.8-YouTube-21.39.4-ROOTLESS-signing-required.ipa` | `05a13cb11f555a64889a19a702028b235a363e50dc489e1dd7728942f7ddeaf7` |
| DEB, same compiled package copied into each host folder | `<each host folder>/com.arifular1f.marufyt_1.1.4+marufyt.8_rootless.deb` | `3ab9f0550f53c6363a49b075fc2845285b5753bf6802bdefc64c12b813f84102` |

Each folder includes its own DEB/dylib, assembly/verification records, toolchain
provenance and manifest. The root holds combined receipts, preservation snapshot,
source/license material, installation/release documentation and SHA256 manifest.
Signing changes the IPA hash; verify these exact unsigned artifacts first.
Use the existing local GBox signing workflow with your own credentials.

## 8. Remaining device-only tests

**NOT TESTED on a physical iPhone**, for each separately signed host:

- Launch/install under the actual profile and entitlements; Google login, logout,
  account switching and restored host sessions; confirm boundary execution and
  that simply opening the account picker does not interrupt downloads.
- Verify old seed/dump/log migration and deletion success, locked-device protection,
  Files visibility, backup/restore, old shared copies and failure paths. Ordinary
  deletion is not forensic secure erase.
- Exercise downloads after cold launch, inactivity expiry/account transition,
  retries, cancel/completion, foreground/background and long-running sessions.
- Capture actual HTTP/protobuf redirects and credential/cookie behavior with a
  controlled test account; verify supported CDN coverage, rejected unsafe URLs and
  native host traffic separately. Do not use live credentials in adversarial tests.
- Regress SponsorBlock/Private Lookup, DeArrow, AiSList, video/audio/playlist/subtitle
  downloads, background audio/PiP, player/feed/Shorts/tab settings and preference
  persistence. Test parser/malformed response and permissions separately.
- Verify native logging behavior and inspect redacted output before sharing;
  investigate lifecycle races, memory safety and performance with device tools.

No claim of complete endpoint discovery, negotiated TLS properties, absence of all
tracking, zero memory retention, secure erasure, device performance improvement,
universal private-API coverage or 100% security is made.

## 9. Commits, branch and review

| Revision | Purpose |
| --- | --- |
| `657aed16a3bc51f5bb41aa4d33d89fe4d343d4ff` | Latest verified Phase 4.1 baseline |
| `0901ef3` | Four security fixes, policy/lifecycle helpers, focused tests and CI gate |
| `e1fcdba` | Cross-origin identity-header restriction; current repository docs and retained audit |
| `1b0f661` | Verified account-boundary owners; no purge on initial picker assignment |
| `06025cc` | Correct C-linkage declaration for playlist cleanup |
| `faada48` | Captured-state expiry coverage and active-download liveness |
| `c5f3dc3f8aa2205053b27029f2e73552d80fae28` | Final tested application source; reject schemeless/ambiguous-host inputs |

Report/release publication is a later documentation-only commit on the same branch;
its exact hash is supplied in the completion handoff and local
`FINAL_REPOSITORY_STATE.json`. Native-source equality to the successful build is
verified there. The complete diff was reviewed for scope, whitespace, accidental
secrets, original-package handling, license preservation and unrelated UI changes.

Protected/default pointers remain: `main` and `stable-21.39.4` at `aac6947…`,
`phase2` at `6d079b1…`, and `phase4.1-performance-ui` at `657aed1…`. No force-push,
existing release overwrite, merge, default-branch change or promotion was performed.
