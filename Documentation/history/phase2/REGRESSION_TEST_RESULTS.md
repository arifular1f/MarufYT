# Optimization regression results

Compiled source: `2d5318a8a92879c51cf31b6b0094b0b492f15315`.
Package: 1.1.4+marufyt.4; work branch `optimization/phase2-performance`.

[Successful CI build 41415092947](https://github.com/arifular1f/MarufYT/actions/runs/41415092947)
compiled 90 arm64 source files with zero compiler `warning:` / `error:` diagnostics.
Theos emits a non-fatal notice that XML plists were not optimized because optional
plist tools are absent. This does not mean installation or launch was tested.
The previous run 41414915918 was cancelled when the final memory/layout changes
superseded it; it is not release evidence.

| Check | Actual result |
| --- | --- |
| Packaging/parser, pinned-tooling and scanner unit tests | 13/13 PASS locally and CI |
| Static source contracts | 115/115 PASS locally and CI; 14 added checks are source assertions |
| CI secret scan | 181 reachable commits, 1559 blobs, zero findings; checkout ref scope 5 |
| Downloaded CI artifact manifest | 5/5 SHA256 matches |
| YouTube 21.43.5 package review | 40/40 structural checks PASS |
| YouTube 21.39.4 package review | 40/40 structural checks PASS |
| Additional optimization artifact review | 10/10 PASS |
| Previous compiled preferences | All 237 retained; zero missing |
| Previous DEB resources and injection filter | Every non-dylib payload file byte-identical to .3 |
| Original/release IPA and DEB preservation | 18/18 protected files unchanged |
| Previous release file preservation | 240/240 files unchanged |
| Main / phase2 / stable branch pointers | Unchanged from baseline |

The 40 checks include ZIP CRC, bundle identity/version, Google SSO URL scheme,
original host section hashes and length, dylib identity/architecture/system
dependencies, ROOTLESS layout, packaged dylib matching DEB, all common remaining
host resources matching the input and existing upstream feature/preference
inventory. They do not execute a hook or log in to Google. The hosts are assembled
separately around the same host-adaptive tweak build; no second identical native
compilation is claimed or needed.

| Feature | Static evidence / implementation disposition | After-change device result |
| --- | --- | --- |
| Google sign-in | Authentication sources untouched, original host sections and URL scheme retained | NOT TESTED |
| YouTube account switching | Same host/session code and static targets retained | NOT TESTED |
| Ad filtering | Hook sources/preferences retained | NOT TESTED |
| SponsorBlock | Service/categories/skipping sources retained, cache/timeouts reviewed | NOT TESTED |
| DeArrow | Same service/replacement logic; image cost budget added | NOT TESTED |
| AiSList | Existing refresh/cache/parse sources retained | NOT TESTED |
| Background audio | Playback sources and audio background mode retained | NOT TESTED |
| Picture-in-Picture | Existing implementation retained | NOT TESTED |
| Video downloads | Download pipeline retained; presentation timer/cache optimized | NOT TESTED |
| Audio downloads | Pipeline retained | NOT TESTED |
| Playlist downloads | Pipeline retained | NOT TESTED |
| Subtitles | Existing implementation retained | NOT TESTED |
| Playback speed | Existing implementation retained | NOT TESTED |
| Loop | Existing implementation retained | NOT TESTED |
| Sleep timer | Existing implementation retained | NOT TESTED |
| Shorts customization | Existing implementation retained | NOT TESTED |
| Feed customization | Existing implementation retained | NOT TESTED |
| Tab customization | Original settings retained; selection/layout code changed | NOT TESTED |
| Top bar customization | Retained, Reduce Transparency guard added | NOT TESTED |
| Liquid Glass | Original default retained; optional lighter appearance/accessibility paths added | NOT TESTED |
| Settings persistence | Existing preference namespace/export/import retained; new toggle uses it | NOT TESTED |
| Entitlements/licensing | No status forging or verification edits introduced | NOT TESTED |

The user's successful pre-optimization testing of both .3 hosts is recorded as
USER-REPORTED BASELINE only. All post-change physical feature behavior, visual
alignment, account sessions, performance and battery measurements require actual
iPhone testing. The missing recording does not supply runtime evidence.

Full raw logs, independent per-host VERIFICATION.json files, preservation snapshots,
OPTIMIZATION_VERIFICATION.json and host audit are in the new local release directory.
Original IPA/DEB inputs and assembled IPAs were not uploaded to GitHub.
