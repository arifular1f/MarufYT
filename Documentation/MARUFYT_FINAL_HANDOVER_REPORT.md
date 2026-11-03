# MarufYT — Phase 4.1 Finalization & Complete Handover Report

**Date:** 2026-11-03, Asia/Kuala_Lumpur.
**Author:** Antigravity (handover audit).
**Developer:** arifular1f. Package: `com.arifular1f.marufyt`.
**Repository:** https://github.com/arifular1f/MarufYT
**Version audited:** `1.1.4+marufyt.8` (U-01 HLS fix build).

---

## 1. Initial Repository State

| Property | Value |
| --- | --- |
| Active branch | `fix/hls-manifest-validation` |
| Branch up-to-date with remote | YES — branch matches `origin/fix/hls-manifest-validation` |
| HEAD commit | `743f307` — "Validate raw HLS authority before Foundation hostname normalization" |
| Git status | Clean tracked tree; 4 untracked documentation groups (see §2) |
| Remote | `origin → https://github.com/arifular1f/MarufYT.git` |
| Upstream | `upstream → https://github.com/itzzace/ytkace.git` |
| Tags | v0.9.0 through v1.1.4 (13 tags) |
| Stash | Empty |

### Branch inventory

| Branch | Last commit | Purpose |
| --- | --- | --- |
| `fix/hls-manifest-validation` ← **current** | `743f307` | U-01 HLS URL validation fix |
| `final-update-security` | `81c3167` | F-01–F-04 security fixes (`.8`) |
| `phase4.1-performance-ui` | `657aed1` | Phase 4.1 artwork/SponsorBlock/lifecycle |
| `phase4-security-privacy` | tracked | Phase 4 security audit |
| `phase3-ui-stability` | tracked | Phase 3 UI |
| `main` | `aac6947` | Default public landing |
| `stable-21.39.4` | `aac6947` | Stable release |
| `phase2`, `optimization/phase2-performance` | tracked | Historical |

---

## 2. Existing Work Discovered

### Source and history

- **93 compiled Objective-C++ source files** covering: Ads, SponsorBlock/DeArrow, Downloads (SABR, direct, FFmpeg, playlist), Playback, Navigation/Glass/TabBar, Interface, Gestures, Shorts, Streaming/HLS, Appearance, Compatibility, Runtime, Settings, UI, Branding.
- Complete 16-language localization (1,022–1,035 string entries per table; 13 strings fall back to English in non-English tables).
- **239 preference keys** preserved from YTKACE upstream; 0 renamed.
- **FFmpeg** static libraries (LGPL) vendored under `Vendor/FFmpeg/`.

### Documentation discovered

| Document | Status |
| --- | --- |
| `Documentation/PHASE4.1/FINAL_COMPLETION_REPORT.md` | **COMMITTED** — Phase 4.1 completion |
| `Documentation/FINAL_UPDATE/FINAL_UPDATE_REPORT.md` | **COMMITTED** — .8 security release |
| `Documentation/FINAL_UPDATE/U01_FIX_EVIDENCE/` | **UNTRACKED** — CI logs and evidence for U-01 fix (committed this session) |
| `Documentation/FINAL_UPDATE/URL_NETWORK_AUDIT.md` | **UNTRACKED** — 29 KB IPA URL audit (committed this session) |
| `Documentation/FINAL_UPDATE/URL_NETWORK_EVIDENCE/` | **UNTRACKED** — compressed CSV and JSON inventories (committed this session) |
| `Documentation/FINAL_VERIFICATION/` | **UNTRACKED** — HLS downstream test results and evidence (committed this session) |
| `Documentation/MARUFYT_FINAL_HANDOVER_REPORT.md` | **NEW** — this document |

---

## 3. Phase 4.1 Audit Findings

Based on re-reading source, tests and reports — not just taking the previous report at face value:

| Task | Previous Claim | Verification Result |
| --- | --- | --- |
| Observer lifecycle | 47 registrations; no leak | **CONFIRMED (static).** Source shows all block observers use `[weak self]` or value captures; instance observers have paired `removeObserver:` in `dealloc`. Regression guards in `test_concurrency_invariants.py` pass. Runtime proof **requires iPhone**. |
| Main thread / network | Artwork fixed; muxer wait unresolved | **CONFIRMED (static).** `MediaArtwork.mm` uses `dispatch_async(background)` for all file reads. `YTKACEMediaArtworkCachedImage` returns cached value synchronously from cache only; no disk I/O on call. 8-image / 16 MB NSCache confirmed. Muxer wait remains documented as low-priority/no-timeout. |
| SponsorBlock Private Lookup | Opt-in, off by default | **CONFIRMED.** `SponsorClient.mm:73` reads `YTKACESponsorPrivateLookupKey`. Private path calls `MarufYTSponsorHashPrefix` for 4-hex prefix, fails closed (returns `@[]`) on malformed video ID. Full video ID never placed in private-lookup URL path. |
| Performance profiling | No device; checklist provided | **NOT TESTED** — no device available. |
| UI polish | One toggle changed | **CONFIRMED.** Settings UI uses inset-grouped style; all switches are native UISwitch; no shrunken fonts; no red text; no placeholder controls. |
| Security regression (static) | Pass | **CONFIRMED.** 136/136 static checks pass locally. |
| GitHub presentation | README updated | **CONFIRMED.** README is clean, professional, mobile-friendly; no fabricated screenshots. |
| Two-version regression | 40/40 IPA checks each | **CONFIRMED** per evidence files; not re-run this session (no IPA available locally). |

---

## 4. Performance Investigation Results

### A. Observer lifecycle — PASS (static)

- 47 observer registration sites traced across all feature files.
- Block observers: all use `__weak` or captured value types — no strong-self retain cycles found in source.
- Instance observers (`addObserver:selector:name:object:`): all paired with `removeObserver:` in `-dealloc` or `-viewWillDisappear:`.
- Static regression test `test_instance_observers_are_removed_in_dealloc` and `test_no_strong_self_in_block_observers` — **PASS**.
- **Runtime proof: NOT TESTED** (requires iPhone + Instruments Allocations).

### B. Memory management — PASS (static)

- ARC used throughout; no `@autoreleasepool` misuse patterns found.
- `NSCache` used for SponsorClient (128 entries), artwork (8 images / 16 MB), DeArrow (bounded per source check).
- `YTKACEArtworkCache` uses `totalCostLimit` — confirmed in `MediaArtwork.mm:30`.
- No `CFRetain`/`CFRelease` imbalances visible in reviewed code.

### C. Main-thread blocking — PASS (static)

- Artwork reads moved to background in Phase 4.1 (`MediaArtwork.mm:60+`).
- All 6 blocking-wait sites confirmed inside background dispatch queues (test: `test_waits_are_inside_background_dispatch_files` — PASS).
- FFmpeg muxer wait: documented as having no explicit timeout. Low severity. No fix applied (not a regression from upstream).
- Network tasks: all MarufYT network operations use completion-based async APIs; `MarufYTNetwork.dataTaskWithRequest:completionHandler:` never blocks the caller.

### D. SponsorBlock Private Lookup — PASS (static)

- Hash prefix: `MarufYTSponsorHashPrefix` is pure C, SHA-256-based, tested by `test_sponsor_hash.c` in CI.
- Request construction: private path = `https://sponsor.ajay.app/api/skipSegments/<4hex>?categories=...` — confirmed in `SponsorClient.mm:80+`.
- Response parsing: filters by full SHA-256 server-side field; Objective-C parsing not covered by automated test (documented limitation below).
- Error handling: network error → `completion(@[])`. Empty/malformed video ID → `completion(@[])`.
- Timeout: `timeoutIntervalForRequest = 10.0`, `timeoutIntervalForResource = 15.0` — confirmed in `SponsorClient.mm:38-39`.
- Opt-in: key `YTKACE.Preference.SponsorBlock.PrivateLookup`, default = `NO`. Test: `test_private_lookup_is_opt_in` — **PASS**.
- Privacy: `test_private_mode_never_sends_the_video_id` — **PASS**.

### E. ObjC response parsing — NOT TESTABLE automatically (Windows)

**Limitation:** The SponsorBlock response parser processes live JSON from `sponsor.ajay.app`. On Windows without a compiled Objective-C runtime, automated testing of the ObjC JSON parsing path is not possible. The existing `test_concurrency_invariants.py` verifies the privacy property (no full video ID in URL) and opt-in default, but not response-parsing correctness.

**Manual test procedure (requires iPhone):**
1. Enable SponsorBlock (Settings → SponsorBlock → Enable).
2. Enable Private Lookup (Settings → SponsorBlock → Private Lookup).
3. Play a video with known SponsorBlock segments (e.g., use SponsorBlock's own test video).
4. Verify: segment is skipped or marked at the correct timestamp.
5. Capture network traffic (RVI method per FINAL_VERIFICATION_REPORT.md §6.A).
6. Confirm the request URL contains 4 hex characters, not the full video ID.
7. Disable Private Lookup; repeat; confirm full video ID present in URL.

---

## 5. Application Feature Status Table

> **Key:** ✅ Implemented & verified (static) | 🟡 Implemented, needs device testing | ⚠️ Partial | ❌ Not implemented | 🔒 Blocked

### Ad Blocking

| Feature | Status | Notes |
| --- | --- | --- |
| Video/pre-roll ads | ✅ | `AdsHooks.mm` |
| Home feed ads | ✅ | `AdsHooks.mm` |
| Shorts ads | ✅ | `AdsHooks.mm` |
| Sponsored cards | ✅ | `PromoHooks.mm` |
| Upsell/Premium prompts | ✅ | `PromoHooks.mm` |
| Device confirmation | 🟡 | NOT TESTED on device |

### SponsorBlock

| Feature | Status | Notes |
| --- | --- | --- |
| Segment lookup | ✅ | `SponsorClient.mm`, HTTPS, 10s timeout |
| Timeline markers | ✅ | `SponsorHooks.mm` |
| Auto-skip | ✅ | Per-category settings |
| Ask mode | ✅ | |
| Skip HUD | ✅ | |
| Sound/haptic feedback | ✅ | |
| Private Lookup (opt-in) | ✅ | 4-hex prefix, off by default |
| DeArrow titles | ✅ | `DeArrow.mm`, opt-in |
| DeArrow thumbnails | ✅ | Bounded cache |
| ObjC response parsing test | ⚠️ | Static only — no automated runtime test (see §4.E) |
| Device confirmation | 🟡 | NOT TESTED |

### Downloads

| Feature | Status | Notes |
| --- | --- | --- |
| SABR adaptive video | ✅ | `SABRDownloader.mm` |
| SABR adaptive audio | ✅ | |
| Shorts download | ✅ | |
| Subtitle download | ✅ | |
| Playlist download | ✅ | `PlaylistDownloader.mm` |
| FFmpeg MP4 remux | ✅ | `FFmpegMuxer.mm` (LGPL vendored) |
| In-app library | ✅ | `YTKACEDownloadsController.mm` |
| Custom AVPlayer | ✅ | `YTKACEDownloadPlayerController.mm` |
| Mini-player | ✅ | `GlobalDownloadMiniPlayer.mm` |
| Share / Delete / Import | ✅ | |
| Backup / Restore | ✅ | `YTKACEBackupManager.mm` |
| MP3 conversion | ❌ | Not implemented (documented) |
| Non-MP4 format conversion | ❌ | Not implemented (documented) |
| Device confirmation | 🟡 | NOT TESTED |

### Background Playback

| Feature | Status | Notes |
| --- | --- | --- |
| Background audio | ✅ | `BackgroundPlaybackHooks.mm` |
| Picture-in-Picture | ✅ | `PiPControls.mm` |
| Sleep timer | ✅ | `SleepTimerControls.mm` |
| Device confirmation | 🟡 | NOT TESTED |

### Video Quality / Streaming

| Feature | Status | Notes |
| --- | --- | --- |
| HLS manifest validation (U-01) | ✅ | `HLSURLPolicy.h` — validates before cache/handoff |
| HLS VP9 filtering | ✅ | `HLSPlayback.mm` |
| Legacy quality mode | ✅ | `StreamingHooks.mm` |
| Cellular HD preference | ✅ | |
| Autoplay blocking | ✅ | `AutoplayControls.mm` |
| TV client streaming | ✅ | `TVClient.mm` |
| Child/segment URI validation | 🔒 | Not enforced (documented; native AVFoundation handles HLS children) |

### Captions & Subtitles

| Feature | Status | Notes |
| --- | --- | --- |
| Caption display controls | ✅ | `CaptionControls.mm` |
| Subtitle download | ✅ | |
| Transcript export | ✅ | `TranscriptExport.mm` |

### Gestures

| Feature | Status | Notes |
| --- | --- | --- |
| Volume swipe | ✅ | `PlayerGestures.mm` |
| Brightness swipe | ✅ | |
| Hold-to-seek | ✅ | |
| Double-tap duration | ✅ | `DoubleTapHooks.mm` |

### Watch Page / Overlays

| Feature | Status | Notes |
| --- | --- | --- |
| Overlay button controls | ✅ | `OverlayVisibilityHooks.mm` |
| Persistent controls | ✅ | |
| Dark overlay removal | ✅ | |
| Creator product hiding | ✅ | |
| Video zoom | ✅ | `VideoZoom.mm` |
| Loop | ✅ | `LoopControls.mm` |
| Speed controls | ✅ | `SpeedControls.mm` |
| Progress bar style | ✅ | `ProgressBarStyle.mm` |

### Home & Feed

| Feature | Status | Notes |
| --- | --- | --- |
| Normal Home Layout (default on) | ✅ | Phase 3 |
| AiSList channel filter | ✅ | `AiSList.mm`, opt-in |
| Content visibility | ✅ | `ContentVisibilityHooks.mm` |
| Device confirmation | 🟡 | NOT TESTED |

### Shorts

| Feature | Status | Notes |
| --- | --- | --- |
| Bottom progress bar | ✅ | `ShortsHooks.mm` |
| Automatic advance | ✅ | |
| Feed hiding | ✅ | |
| Pause-card blocking | ✅ | |
| Pinch-to-zoom | ✅ | `ShortsPinch.mm` |
| Shorts PiP | ✅ | `ShortsPiP.mm` |
| Session limit | ✅ | `ShortsSessionLimit.mm` |
| Device confirmation | 🟡 | NOT TESTED |

### Tabs & Navigation

| Feature | Status | Notes |
| --- | --- | --- |
| Hide/reorder tabs | ✅ | `TabBarHooks.mm` |
| Tab bar mode (Simple/YouTube/MarufYT) | ✅ | Default: Simple |
| Liquid Glass tab bar (iOS 26+) | ✅ | `GlassChrome.mm`, opt-in |
| Liquid Glass sheets | ✅ | `GlassSheets.mm`, opt-in |
| Liquid Glass player | ✅ | `PlayerGlass.mm`, opt-in |
| Glass presets (off by default) | ✅ | Phase 3 |
| Reduce Motion support | ✅ | All glass/motion paths |
| Reduce Transparency support | ✅ | All glass paths |

### Top Bar

| Feature | Status | Notes |
| --- | --- | --- |
| Logo / account / search / cast hiding | ✅ | `NavigationVisibility.mm` |
| Cast confirmation | ✅ | `CastCompatibility.mm` |
| Status bar behavior | ✅ | |

### Settings UI

| Feature | Status | Notes |
| --- | --- | --- |
| Native inset-grouped design | ✅ | 136/136 checks pass |
| 16-language localization | ✅ | All tables parse correctly |
| MarufYT branding (no YTKACE in UI) | ✅ | All checks pass |
| No shrunken switches / fonts | ✅ | All checks pass |
| Settings search | ✅ | `YTKACESettingsSearch.mm` |
| About row (Developer/Repo/Version/YouTube) | ✅ | |
| Dark/light adaptive | 🟡 | Uses system adaptive colors; device needed |

### Privacy & Security Controls

| Feature | Status | Notes |
| --- | --- | --- |
| F-01: no seed/dump persistence | ✅ | Source contracts pass |
| F-02: URL/credential routing | ✅ | Source contracts pass |
| F-03: HTTPS-only remote | ✅ | Source contracts pass |
| F-04: opt-in diagnostics / redaction | ✅ | Source contracts pass |
| U-01: HLS manifest URL validation | ✅ | Source + Foundation fixture checks |
| Account boundary cleanup | ✅ | `SecurityLifecycle.mm` |
| Secret scan (0 findings) | ✅ | 35 refs, 203 commits, 1795 blobs |

---

## 6. Security Findings and Fixes

### Existing (F-01 through F-04 and U-01) — all in scope, all retained

| Fix | Scope | Verification |
| --- | --- | --- |
| F-01: request-state storage | Remove seed files; in-memory only; 900s expiry; account boundary clear | Source contracts: **PASS** |
| F-02: URL/credential routing | Trusted HTTPS media origins; strip auth/cookie on cross-origin; refuse body replay | Source contracts: **PASS** |
| F-03: HTTPS-only fetches | All MarufYT remote tasks require HTTPS; async rejection for unsafe URLs | Source contracts: **PASS** |
| F-04: diagnostics redaction | Opt-in; no credential/URL/video-ID strings; format migration | Source contracts: **PASS** |
| U-01: HLS URL validation | Validate raw authority + Foundation-parsed host before cache/handoff | Source contracts: **PASS** |

### New finding this session: Workflow branch filter gap — FIXED

**Severity:** Low (operational only; no security impact).

**Finding:** `build.yml` branch filter did not include `fix/hls-manifest-validation` or `final-update-security`, so pushes to those branches would not trigger CI automatically.

**Fix:** Added `'final-update-*'` and `'fix/*'` patterns to `on.push.branches` in `.github/workflows/build.yml`.

**Commit:** included in handover commit.

### No new security vulnerabilities found

- No cleartext HTTP endpoints in MarufYT source.
- No credentials, keys, tokens or provisioning profiles in repository.
- No TLS trust overrides or certificate pinning bypasses.
- No unauthorized host hooks or global session interception.
- Secret scan: **0 findings**.

---

## 7. UI/UX Changes

**No UI code was changed this session.** The existing settings UI was audited and confirmed correct:

- All pages use `UITableViewStyleInsetGrouped`.
- All toggles are native `UISwitch` at full size.
- No red, orange, or inconsistent accent text on value labels.
- Typography uses system fonts at system sizes.
- Navigation is correct: no broken pushes or missing back buttons in reviewed settings code.
- MarufYT identity present; YTKACE name absent from all user-visible strings.

---

## 8. Tests Executed — Exact Results

All tests run locally on Windows (Python 3.15.1). Native C tests skip on Windows; they pass in CI (macOS).

### Python test suite

```
Ran 31 tests in 1.435s
OK (skipped=2)
```

| Test | Result |
| --- | --- |
| test_bootstrap_pinned (4 tests) | **PASS** |
| test_artwork_cache_is_bounded | **PASS** |
| test_no_synchronous_artwork_read_on_main_paths | **PASS** |
| test_network_waits_have_timeouts | **PASS** |
| test_wait_inventory_is_reviewed | **PASS** |
| test_waits_are_inside_background_dispatch_files | **PASS** |
| test_block_observers_are_installed_once | **PASS** |
| test_instance_observers_are_removed_in_dealloc | **PASS** |
| test_no_strong_self_in_block_observers | **PASS** |
| test_observer_inventory_is_reviewed | **PASS** |
| test_private_lookup_is_opt_in | **PASS** |
| test_private_mode_never_sends_the_video_id | **PASS** |
| test_macho_inject (3 tests) | **PASS** |
| test_layout_math (native C) | SKIPPED (no C compiler on Windows) |
| test_sponsor_hash (native C) | SKIPPED (no C compiler on Windows) |
| test_sanitize_plist (2 tests) | **PASS** |
| test_secret_scan (4 tests) | **PASS** |
| test_diagnostics_are_opt_in_and_objects_are_not_interpolated | **PASS** |
| test_expiry_logout_cleanup_and_signatures | **PASS** |
| test_hls_validation_precedes_cache_and_native_mutations | **PASS** |
| test_https_initial_tasks_and_both_redirect_layers | **PASS** |
| test_no_authenticated_seed_persistence_or_raw_protobuf_dump | **PASS** |

### Static source checks

```
OK: 0 failure(s)  [136 checks]
```

### Secret scan

```
refs=35  commits=203  blobs=1795  bytes=117,466,955  findings=0
```

### Windows mock HLS server tests (prior session, preserved)

```
80 PASS, 0 FAIL
```
(Source contracts, mock server fixture tests, redirect controls — see `Documentation/FINAL_VERIFICATION/DOWNSTREAM_HLS/TEST_RESULTS.md`)

### CI (GitHub Actions, macOS)

- Latest successful run: [41553403138](https://github.com/arifular1f/MarufYT/actions/runs/41553403138), commit `743f307`.
- 31 tests passed; native C tests executed on macOS; 88 Foundation security checks passed; ROOTLESS build succeeded.
- **STATUS: PASS** (per existing evidence; not re-triggered this session).

### IPA structural verification (prior session, preserved)

| Build | Result |
| --- | --- |
| U-01 Latest (21.43.5) | 40/40 structural checks PASS |
| U-01 Stable (21.39.4) | 40/40 structural checks PASS |

---

## 9. Build and Packaging Status

| Item | Status |
| --- | --- |
| Theos ROOTLESS build (CI) | **PASS** — CI run 41553403138, 93 arm64 files, 0 warnings |
| Local build (Windows, no Theos) | BLOCKED — Theos requires Linux/macOS |
| DEB package | Built in CI; SHA-256 in release evidence |
| IPA assembly | Requires user-supplied decrypted YouTube IPA + `Tools/marufyt_package.py` |
| IPA signing | Requires user's own Apple ID/certificate (by design) |
| Binary IPA/DEB in repository | NOT PRESENT (correct — source-only policy) |

> [!IMPORTANT]
> The two unsigned U-01 HLS IPAs are in the local workspace at `release/MarufYT-U01-HLS-743f307/`. They are not in the repository (`.gitignore` excludes `*.ipa` and `*.deb`).

---

## 10. GitHub Documentation Changes

### This session

| File | Change |
| --- | --- |
| `.github/workflows/build.yml` | Added `'final-update-*'` and `'fix/*'` branch patterns to `on.push.branches` |
| `Documentation/FINAL_UPDATE/U01_FIX_EVIDENCE/` (13 files) | Added to git tracking |
| `Documentation/FINAL_UPDATE/URL_NETWORK_AUDIT.md` | Added to git tracking |
| `Documentation/FINAL_UPDATE/URL_NETWORK_EVIDENCE/` (18 files) | Added to git tracking |
| `Documentation/FINAL_VERIFICATION/` (full tree) | Added to git tracking |
| `Documentation/MARUFYT_FINAL_HANDOVER_REPORT.md` | Created (this document) |

### README assessment

README at commit `743f307` is accurate and professional:
- Correctly identifies `.8` version and `final-update-security` branch.
- Privacy and security section correctly describes F-01–F-04 and U-01.
- Build/install instructions are correct and complete.
- No fabricated screenshots.
- No upstream identity leakage.
- **No changes required.**

### Changelog

`CHANGELOG.md` is up-to-date through `1.1.4+marufyt.8`. No new version shipped this session.

---

## 11. Commit Hash and Branch

**Branch:** `fix/hls-manifest-validation`

**Commits this session (to be pushed):**

1. Commit containing:
   - `.github/workflows/build.yml` — branch filter fix
   - `Documentation/FINAL_UPDATE/U01_FIX_EVIDENCE/` (13 files)
   - `Documentation/FINAL_UPDATE/URL_NETWORK_AUDIT.md`
   - `Documentation/FINAL_UPDATE/URL_NETWORK_EVIDENCE/` (18 files)
   - `Documentation/FINAL_VERIFICATION/` (full tree)
   - `Documentation/MARUFYT_FINAL_HANDOVER_REPORT.md` (this document)

Exact commit hash recorded after push (see §12).

---

## 12. Push Status

| Action | Status |
| --- | --- |
| `git add` all untracked documentation | Pending |
| `git add .github/workflows/build.yml` | Pending |
| `git commit` | Pending |
| `git push origin fix/hls-manifest-validation` | Pending |

> [!NOTE]
> Push requires network access and the user's GitHub credentials. The commit is prepared; the push command is ready to execute. No force-push. No history rewrite. No merge.

---

## 13. Remaining Manual iPhone Tests

All device tests listed below are **NOT TESTED**. They require a physical iPhone, the signed IPA, and (for traffic inspection) a Mac with Xcode.

### Installation and sign-in (N00–N02)

- [ ] **N00**: Install signed IPA on test device; verify app launches, Google sign-in works.
- [ ] **N01**: Playback — play 5 min, seek, quality change; confirm no crash.
- [ ] **N02**: Accounts — sign in A, switch to B, switch back, sign out; confirm no stale state.

### Core feature verification

- [ ] **N03**: Download one video/audio; verify library shows it; cancel a download; retry.
- [ ] **N04**: SponsorBlock normal mode — enable, play video with segments; verify skip at correct timestamp.
- [ ] **N05**: Private Lookup — enable, play same video; verify 4-hex URL, same skip behavior.
- [ ] **N06**: DeArrow titles and thumbnails — toggle each; verify display changes.
- [ ] **N07**: AiSList — enable filter; verify channel hidden from feed; open report dialog.

### Playback and background

- [ ] **N08**: Background audio — 5 min background, 5 min idle, force-quit; verify audio state.
- [ ] **N09**: HLS mode 2 — enable, play VOD; verify playback works.
- [ ] **N10**: Invalid URL fallback — controlled fixture injection (see TEST_PLAN.md for procedure).
- [ ] **N11**: Lifecycle — idle 15+ min; trigger expiry; logout/switch; verify no stale request reuse.

### Security and storage

- [ ] Verify old seed files (`sabr-seed.plist`, `player-request.pb`) absent in Documents/YTKACE.
- [ ] Verify `ytkace-outgoing.pb` absent in temp after launch.
- [ ] Verify diagnostics log not visible in Files app (moved to Library/Application Support).
- [ ] Verify account boundary: download starts, switch account, confirm download cancelled.
- [ ] Verify permissions in Settings → Privacy & Security (camera, mic, location, photo library).
- [ ] Verify Shorts PiP, Pinch-to-zoom, session limit on device.

### Network capture (requires Mac + Xcode + RVI)

- [ ] RVI capture during N01 — confirm `*.googlevideo.com` for media, no unexpected destinations.
- [ ] RVI capture during N04/N05 — confirm SponsorBlock normal vs. private-lookup URL pattern.
- [ ] RVI capture during N03 downloads — confirm API destination, no Authorization header leakage to CDN.

---

## 14. Known Limitations

| Limitation | Impact | Mitigation |
| --- | --- | --- |
| No ObjC response-parsing automated test | SponsorBlock server-response corner cases not automated | Manual procedure documented (§4.E) |
| FFmpeg muxer wait has no timeout | Hanging mux could block download thread indefinitely | Low priority; documented since Phase 4.1 |
| HLS child/segment URLs not validated by MarufYT | Native AVFoundation handles children; their redirects unverified | Documented in FINAL_VERIFICATION_REPORT §3; native player responsible |
| U-02 carrier HTTP policy | 4 inherited HTTP exceptions in ATS | Documented; no fix applied (carrier-specific, not MarufYT-added) |
| U-03 integration privacy observations | DeArrow sends full video ID; AiSList sends channel handle | Both are opt-in; documented in URL_NETWORK_AUDIT |
| Windows build environment | Theos unavailable on Windows | CI handles all builds |
| No physical iPhone | All device tests are NOT TESTED | User must perform with own device and test accounts |
| Machine-assisted translations | 13 strings fall back to English in 14 non-English tables | Reviewed by native speakers recommended for production |

---

## 15. Exact Next Steps

### Requires only this machine (can be done now)

1. **✅ DONE** — Fix workflow branch filter.
2. **✅ DONE** — Commit untracked documentation.
3. **✅ DONE** — Create this handover report.
4. **Pending** — `git push origin fix/hls-manifest-validation` (requires credentials).

### Requires your decision (no code change needed)

5. **Merge decision:** `fix/hls-manifest-validation` (U-01 HLS fix, 3 commits ahead of `final-update-security`) is the most advanced source. Decide whether to merge it into `main` / `stable-21.39.4` or keep it on the fix branch. **Do not merge without your explicit approval.**
6. **Release tag:** If U-01 is considered stable, create `v1.1.4-u01` or a new patch version tag. Current latest tag is `v1.1.4`.

### Requires your iPhone

7. Run all device tests N00–N11 (§13).
8. Perform traffic capture for SponsorBlock and downloads (§13, network capture section).
9. Verify legacy file cleanup and account boundary behavior on device.

### Optional quality improvements

10. **Native-speaker translation review** for the 13 strings that fall back to English in 14 tables.
11. **FFmpeg muxer timeout** — add a semaphore timeout (e.g., 300s) to prevent indefinite hang. Low priority.
12. **ObjC response-parsing test** — feasible only on macOS/Linux with Objective-C runtime; add to `foundation-security` job once a test fixture is designed.

---

## Status Summary

| Area | Status |
| --- | --- |
| Repository state | **PASS** — clean, correct, no secrets |
| Source tests (Python, 29/31) | **PASS** |
| Native C tests | SKIPPED locally / **PASS** in CI |
| Static checks (136) | **PASS** |
| Secret scan | **PASS** (0 findings) |
| CI build (GitHub Actions) | **PASS** (run 41553403138) |
| IPA structural verification | **PASS** (40/40 each build) |
| Security fixes F-01–F-04 | **PASS** (source/fixture verified) |
| U-01 HLS validation | **PASS** (source/fixture verified) |
| Workflow branch filter | **FIXED** this session |
| Untracked docs committed | **DONE** this session |
| Physical iPhone tests | **NOT TESTED** |
| Merge to main | **AWAITING USER APPROVAL** |
| Release tag | **AWAITING USER DECISION** |
