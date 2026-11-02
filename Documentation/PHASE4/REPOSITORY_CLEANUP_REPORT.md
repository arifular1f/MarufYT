# Repository Cleanup Report (Phase 4)

406 tracked files reviewed by folder and purpose. Nothing was deleted blindly; every move was done with `git mv` so history follows the file.

## Classification

| Path | Class | Decision |
| --- | --- | --- |
| `Tweak/`, `Resources/`, `Makefile`, `control`, `MarufYT.plist` | Required source / build | Keep |
| `Vendor/FFmpeg/` | Required build dependency (LGPL libraries, licence texts) | Keep; legally required |
| `Scripts/` | Required build scripts (FFmpeg, IPA, signing helpers) | Keep |
| `Tools/`, `Tests/` | Required (packaging, checks, tests, secret scan) | Keep |
| `.github/` | Required workflow, Dependabot, issue templates | Keep; added `phase4-*` branch trigger |
| `LICENSE`, `THIRD_PARTY_NOTICES.md`, `UPSTREAM_README.md` | Required licence / attribution | Keep, untouched |
| `SECURITY.md`, `PRIVACY.md` | Required security documentation | Keep |
| `Documentation/audits/` | Security audit evidence | Keep |
| `Documentation/BUILD_INSTRUCTIONS.md`, `MODULES.md`, `SOURCE_PROVENANCE.md`, `REQUIREMENTS_CHECKLIST.md` | Current documentation | Keep |
| Nine Phase 2 reports (`ANIMATION_OPTIMIZATION_REPORT`, `CPU_BATTERY_…`, `DEVICE_COMPATIBILITY_…`, `FINAL_OPTIMIZATION_…`, `MEMORY_…`, `PERFORMANCE_BEFORE_AFTER`, `REGRESSION_TEST_RESULTS`, `TOUCH_RESPONSE_AUDIT`, `UI_ALIGNMENT_AUDIT`) | Historical, not duplicates, but cluttered the top level | **Moved** to `Documentation/history/phase2/`; the two inbound links (`MODULES.md`, `SOURCE_PROVENANCE.md`) updated |
| `docs/COMPATIBILITY.md` | Outdated: described a YouTube 21.26.4 baseline and "YTKACE" | **Rewritten** for 21.43.5 and 21.39.4 |
| `docs/ASSET_PROVENANCE.md`, `CLEAN_ROOM.md`, `FEATURE_MATRIX.md` | Provenance / feature documentation | Keep. `FEATURE_MATRIX.md` still uses upstream wording; not rewritten (Unknown accuracy, needs owner review) |
| `screenshots/`, `web/index.html` | Upstream YTKACE assets, referenced by `UPSTREAM_README.md`; `web/` is a YTKACE landing page | **Kept**: attribution value, not MarufYT's own images. Not used in the new README. Removing them is an owner decision |
| `README.md` | Out of date branch table, absolute "no analytics" claim | **Rewritten** |

## Searched and found nothing to remove

- Committed binaries (`.ipa .deb .dylib .p12 .mobileprovision .pem`): none tracked. `__pycache__` / `.pyc`: not tracked.
- Credentials: full-history scan 0 findings, so no rotation or history action was needed.
- `NSLog` calls: none. No `TODO`-style debug backdoors found.
- Unused source files: not determined. Every file in the Makefile list is compiled; unreferenced `.mm` files were not enumerated (Needs investigation).

## Why folders show old dates on GitHub

GitHub shows the last commit that touched a folder **on the branch being viewed (`main`)**. `main` still holds the 1.1.1 release; Phases 2–4 live on `phase2`, `optimization/phase2-performance`, `phase3-ui-stability` and `phase4-security-privacy`. On this branch the last-change dates are: Tweak, Resources, Tools, Tests, Scripts, Documentation and `.github` 2026-11-02; `docs` 2026-10-29 before this change; `Vendor` 2026-09-20, `screenshots` and `web` 2026-09-28. The last three have genuinely not changed and are intentionally untouched. Dates on `main` will update when the work is merged into `main`, which requires your approval and has not been done. No timestamps, empty commits or placeholder files were used.
