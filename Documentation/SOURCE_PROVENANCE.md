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
| `Tools/phase2_translations.py` | Adds the MarufYT strings to all 16 localization tables (idempotent) |
| `Tools/marufyt_secret_scan.py` | Full-history credential scanner (CI) |
| `SECURITY.md`, `PRIVACY.md`, `.github/dependabot.yml`, `Documentation/REQUIREMENTS_CHECKLIST.md`, `Documentation/audits/*` | Security policy, privacy statement, dependency updates, requirement tracking, audit reports |
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
| `Tweak/Features/Downloads/DownloadLog.mm` | Security: log moved to Application Support, excluded from backup, file protection, redaction of tokens and URL queries, one-time removal of the old Documents log |
| `Tweak/UI/OverlayButtonHost.mm` | Accessibility: localized VoiceOver labels for player buttons |
| `Resources/YTKACE.bundle/*.lproj/Localizable.strings` | 11 MarufYT strings appended to each of the 16 tables (upstream entries unchanged) |
| `.github/ISSUE_TEMPLATE/*` | Rebranded; private security-report link. `.github/FUNDING.yml` (upstream donation link) removed from this repository |
| `Makefile`, `control`, `MarufYT.plist` | `MarufYT.dylib`, build number define, package `com.arifular1f.marufyt` |
| `LICENSE`, `THIRD_PARTY_NOTICES.md` | MarufYT copyright line and provenance header added; upstream text unchanged |

Removed: upstream workflows `build-ipa.yml` (downloads YouTube from Dropbox), `pages.yml` (publishes the upstream site) and `build-deb.yml` (replaced by `build.yml`).

## 3. Unchanged upstream

Everything else remains upstream unless listed above or in the follow-up exception here. In particular, feature implementations, vendored libraries and solver bytes retain the audited release state. Follow-up audit exceptions: `Scripts/build-ffmpeg.sh` requires a verified archive hash (commit `8a63e14`); `Tests/test_secret_scan.py` adds independent security regression fixtures; the secret scanner and security documentation were strengthened without changing native implementation sources. `UPSTREAM_README.md` is an exact copy of the README at the pinned upstream commit `11249eef76801b2f6323ab094d37893a4098b4f7`.

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
