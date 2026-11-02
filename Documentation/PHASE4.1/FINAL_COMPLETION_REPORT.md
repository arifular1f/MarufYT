# Final Completion Report (Phase 4.1)

Branch `phase4.1-performance-ui` (base `c044eb4`, the verified Phase 4 head). Package `1.1.4+marufyt.7`. `main` and all protected branches untouched; nothing merged. CI run `41434077642` on `1bd5c82`: tests (including both native C suites) and build succeeded, 0 warnings.

## Results by task

| Task | Status |
| --- | --- |
| 1 Observer lifecycle | **Investigated, not an issue.** 47 registrations traced; no leak or duplicate registration confirmed; static regression guards added. Runtime proof **requires an iPhone** (`OBSERVER_LIFECYCLE_REPORT.md`) |
| 2 Main thread / network | **Confirmed and fixed:** synchronous artwork reads on the main thread (mini player, audio player, Now Playing). **Investigated, not an issue:** all six blocking-wait files run on background queues. **Confirmed but unresolved (low):** the muxer wait in the importer has no timeout (`MAIN_THREAD_NETWORK_REPORT.md`) |
| 3 SponsorBlock privacy | **Implemented, opt-in, default off**, after checking the server source and the live API. Native known-answer tests pass in CI. ObjC response parsing is **not** covered by an automated test (`SPONSORBLOCK_PRIVACY_REPORT.md`) |
| 4 Performance profiling | **Not tested.** No device or Instruments. A reproducible iPhone checklist is provided; no numbers exist (`PERFORMANCE_PROFILE.md`) |
| 5 UI polish | **No UI code changed** beyond one standard toggle row. Layout shift **not reproduced and not claimed fixed** on either version (`UI_STABILITY_REPORT.md`) |
| 6 Security regression | **Pass (static):** no new secrets, hosts, tracker strings, permissions or risky symbols (`SECURITY_REGRESSION_REPORT.md`) |
| 7 GitHub presentation | README and PRIVACY updated for the new option. **No screenshot gallery:** the only images supplied show the pre-Phase-3 look, and none of the current build exists; the repository's other screenshots are YTKACE's and are not used. Send screenshots of the current build to add one |
| 8 Two-version regression | Both IPAs built and statically verified (40/40 each). Feature behaviour on a device: **Not tested** |
| 9 Release | Rebuilt because source changed: `release/MarufYT-Phase4.1/` (new; earlier releases untouched; inputs re-verified) |

## Changes

1. `MediaArtwork`: bounded cache + async loader; three main-thread call sites fixed.
2. `SponsorClient` + `MarufYTSponsorHash.h`: optional 4-hex-character lookup, Settings toggle, 2 strings × 16 languages (machine-assisted, not native-reviewed).
3. `Tests/test_concurrency_invariants.py`, `Tests/native/test_sponsor_hash.c` and wrapper; static checks.
4. Version bump, CHANGELOG, `PRIVACY.md`, CI branch filter for `phase4.*`.

## Release

| Build | IPA SHA-256 |
| --- | --- |
| Latest, YouTube 21.43.5 | `a71af6720ff67ef36d304f5902136f80314cb85fc7cf313d2b7b4ad2a7a6515a` |
| Stable, YouTube 21.39.4 | `6e28622c4c6a0983bbc6d6ac1919c5bb760d48c6a17b5298d64971d92343ec7b` |

DEB `ba8c76df659f7f153cf279f2f5b50333a99f49cdbaee34840d662a669837349f`; dylib `a9beeafb04fc7b08ec69e6ff994c501dbe35150f730309ec955a6a760f374f84`. IPAs are unsigned and are not in the repository.

## Still needs a person with the phone

Run the checklist in `PERFORMANCE_PROFILE.md`; capture layout snapshots on each YouTube version right after launch and later; open and close the Downloads library and players repeatedly under Allocations; try Private Lookup on a few videos with and without SponsorBlock segments; confirm sign-in and account switching.

## Not claimed

Zero data transmission, absence of memory leaks, UI stability, performance or battery improvement, or that the delayed layout shift is fixed.
