# Source provenance

Base: YTKACE **v1.1.1** (tag commit `d9995b92`, MIT, https://github.com/itzzace/ytkace). The full upstream history is kept in this repository's Git log.

## 1. New MarufYT code (original, © arifular1f, MIT)

| File | Purpose |
| --- | --- |
| `Tweak/MarufYT/MarufYTBranding.h/.mm` | Product name, developer, repository and profile URLs; user-facing rebranding; own-view label check; opening URLs |
| `Tweak/MarufYT/MarufYTDesign.h/.mm` | Liquid Glass preset defaults; the capsule depth layer (an outside-only shadow); design tokens |
| `Tweak/MarufYT/MarufYTCreditsController.mm` | About, credits and licences page (inset-grouped table with links) |
| `Tools/marufyt_checks.py` | Static source and regression checks run in CI |
| `Tools/marufyt_package.py` | Local IPA assembly from a user-supplied decrypted YouTube |
| `Documentation/*`, `README.md`, `CHANGELOG.md` | Project documentation |

## 2. Modified upstream files

Each change is small and marked with a `MarufYT` comment where it isn't self-explanatory.

| File | Change |
| --- | --- |
| `Tweak/Runtime/Localization.mm` | Values are rebranded once when a language loads; the key fallback is rebranded too |
| `Tweak/Runtime/Preferences.mm` | Registers `MarufYTPreferenceDefaults()` after the upstream defaults |
| `Tweak/Features/Navigation/TabBarHooks.mm` | Tab title becomes MarufYT; the label check accepts both names; the glass constructor honours the preset; the capsule depth layer is attached, excluded from the fade loop, and removed when glass is turned off |
| `Tweak/Features/Interface/NavigationVisibility.mm` | Own-view label check accepts both prefixes |
| `Tweak/Settings/YTKACERootOptionsController.mm` | Header title; the About section is now Repository, Developer, Credits and device info; the hidden download-log long-press moves to the Developer row |
| `Tweak/Settings/NativeSettingsEntry.mm` | YouTube Settings group title; About rows Repository, arifular1f and Credits |
| `Tweak/Settings/YTKACESettingsPages.mm` | Credits factory points to the MarufYT page; backup dialog title; tab list name; the "Floating Tab Bar Depth" toggle |
| `Tweak/Settings/SettingsEntry.mm`, `YTKACETabEditorController.mm`, `YTKACEDownloadsController.mm` | User-facing product name |
| `Tweak/Features/Downloads/DownloadCoordinator.mm`, `YTKACEDownloadPlayerController.mm`, `Tweak/Features/Onboarding/FirstLaunch.mm` | Alert and dialog titles |
| `Makefile`, `control`, `MarufYT.plist` (was `YTKACE.plist`) | Library name `MarufYT.dylib`; package `com.arifular1f.marufyt`, which conflicts with/replaces `com.itzzace.ytkace` |
| `.github/workflows/build.yml` (was `build-deb.yml`) | Builds ROOTLESS only and runs the MarufYT checks. Upstream's `build-ipa.yml` (downloads YouTube from Dropbox) and `pages.yml` (publishes the upstream website) are removed |
| `LICENSE`, `THIRD_PARTY_NOTICES.md` | Adds MarufYT copyright and a provenance header; upstream text unchanged |

## 3. Unchanged upstream

Everything else under `Tweak/`, `Resources/YTKACE.bundle` (all 15 localizations, the EJS solver, the SponsorBlock artwork), `Vendor/FFmpeg` (prebuilt LGPL static libraries, built by `Scripts/build-ffmpeg.sh`), `Scripts/`, `Tests/`, `Tools/` (except the two MarufYT files above), `docs/`, `web/`, `screenshots/`. The upstream README is kept as `UPSTREAM_README.md`.

## Internal identifiers kept on purpose

Renaming these would wipe users' settings and break the tweak's own-view detection:

- `YTKACE.Preference.*` keys
- `YTKACE*` accessibility identifiers
- notification names and error domains
- `YTKACE-` scratch-file prefixes
- the `Documents/YTKACE` storage folder
- `YTKACE.bundle`
- `FEYTKACE` pivot identifier
- backup format
