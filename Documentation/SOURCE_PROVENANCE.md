# Source provenance (branch `phase2`)

**Base:** upstream YTKACE `main` at **`11249ee`** (2026-11-01, after tag v1.1.4), MIT, https://github.com/itzzace/ytkace. The full upstream history is kept in Git. The previous MarufYT release (based on v1.1.1) is preserved on branch `stable-21.39.4`.

## 1. New MarufYT code (original, © arifular1f, MIT)

| File | Purpose |
| --- | --- |
| `Tweak/MarufYT/Branding/MarufYTBranding.h/.mm` | Identity, version/build/host helpers, rebranding of user-facing text, own-view label check, opening URLs |
| `Tweak/MarufYT/Design/MarufYTTheme.h/.mm` | Settings design system: colours, typography, metrics, control styling, icon tiles |
| `Tweak/MarufYT/Design/MarufYTDesign.h/.mm` | Liquid Glass preset, tab-bar mode preset, capsule depth layer |
| `Tools/marufyt_checks.py` | Static source checks (CI) |
| `Tools/marufyt_package.py` | Local IPA assembly |
| `Tools/marufyt_host_audit.py` | Static compatibility audit between two YouTube hosts |
| `Tools/phase2_apply.py` | Exact record of the Phase 2 changes applied to upstream files |
| `Documentation/*`, `README.md`, `CHANGELOG.md`, `.github/workflows/build.yml` | Project documentation and CI |

## 2. Modified upstream files

| File | Change |
| --- | --- |
| `Tweak/UI/Assets.mm` | `YTKACEAccentColor()` returns the MarufYT accent |
| `Tweak/Runtime/Localization.mm` | Values rebranded per language load; key fallback rebranded |
| `Tweak/Runtime/Preferences.mm` | Registers `MarufYTPreferenceDefaults()` |
| `Tweak/Features/Navigation/TabBarHooks.mm` | Tab title; label check for both names; glass mode falls back to the preset; constructor honours the preset; depth layer attached, excluded from the fade loop, and removed with the glass |
| `Tweak/Features/Interface/NavigationVisibility.mm` | Own-view label check accepts both names |
| `Tweak/Features/Interface/AiSListReport.mm` | User agent and default reporter name |
| `Tweak/Features/Downloads/DownloadCoordinator.mm`, `YTKACEDownloadPlayerController.mm`, `Tweak/Features/Onboarding/FirstLaunch.mm` | Branded titles |
| `Tweak/Settings/YTKACERootOptionsController.mm` | Inset-grouped themed table, icon tiles, MarufYT header, new About section (no Credits), concise product line |
| `Tweak/Settings/YTKACESettingsPages.mm` | Inset-grouped themed pages; values grey with a menu chevron; Dynamic Type; native heights; SponsorBlock regrouping; colour dots; depth toggle; branded literals |
| `Tweak/Settings/YTKACETabEditorController.mm`, `YTKACESettingsSearch.mm`, `NativeSettingsEntry.mm`, `SettingsEntry.mm`, `YTKACEDownloadsController.mm` | Theme and branding; YouTube Settings About rows Developer and Repository |
| `Makefile`, `control`, `MarufYT.plist` | `MarufYT.dylib`, build number define, package `com.arifular1f.marufyt` |
| `LICENSE`, `THIRD_PARTY_NOTICES.md` | MarufYT copyright line and provenance header added; upstream text unchanged |

Removed: upstream workflows `build-ipa.yml` (downloads YouTube from Dropbox), `pages.yml` (publishes the upstream site) and `build-deb.yml` (replaced by `build.yml`).

## 3. Unchanged upstream

Everything else: features, hooks, `Resources/YTKACE.bundle` (localizations, EJS solver, artwork), `Vendor/FFmpeg`, `Scripts/`, `Tests/`, upstream `Tools/`, `docs/`, `web/` and `screenshots/`.

## Internal identifiers kept on purpose

These keep their upstream names:

- `YTKACE.Preference.*` keys
- `YTKACE*` accessibility identifiers
- notification names and error domains
- `YTKACE-` scratch files
- the `Documents/YTKACE` folder
- `YTKACE.bundle`
- the `FEYTKACE` pivot identifier
- the backup format

Renaming them would wipe users' settings and break the tweak's own-view detection.
