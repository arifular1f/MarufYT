# Changelog

## 1.1.4+marufyt.3 (2026-11-02): security, localization and accessibility

### Security and privacy
- **Diagnostics log:**
  - Moved from `Documents/YTKACE/Logs` (visible in the Files app because file sharing is on, and included in device backups) to `Library/Application Support/YTKACE/Logs`.
  - Excluded from backup and given `CompleteUntilFirstUserAuthentication` file protection.
  - The old Documents log file is removed once. Downloads are not touched.
- **Log redaction:** every log line has bearer tokens, URL query strings (stream signatures, keys, client IPs) and token-like parameters removed before it is written, including in debug mode.

### Accessibility and localization
- **VoiceOver:** player overlay buttons (Download, PiP, Loop, Sleep Timer, Speed −/value/+, Transcript, SponsorBlock) announce localized, branded names instead of internal identifiers.
- **Translations:** all 11 strings added by MarufYT are translated into all 16 languages. 13 untranslated upstream strings remain unchanged and fall back to English.

### Repository and CI
- **Actions:**
  - pinned to full commit SHAs;
  - credentials not persisted;
  - per-job read-only permissions, timeouts and concurrency.
- **Theos installer:** fetched from a pinned commit, verified by SHA-256, and Theos checked out at that commit. Toolchain provenance is recorded per build.
- **CI secret scan:** `Tools/marufyt_secret_scan.py` checks the full history on every run.
- **Dependabot:** updates for GitHub Actions.
- **New documents:** `SECURITY.md`, `PRIVACY.md` and `Documentation/REQUIREMENTS_CHECKLIST.md`; audit reports in `Documentation/audits/`.
- **Repository config:**
  - issue templates rebranded to MarufYT, with a private security-report link;
  - the upstream donation config (`FUNDING.yml`) removed from this repository, while upstream credit remains in `LICENSE`, `THIRD_PARTY_NOTICES.md` and `UPSTREAM_README.md`.

## 1.1.4+marufyt.2 (2026-11-02) — Phase 2

Based on upstream YTKACE `main` at `11249ee` (after v1.1.4), which adds fixes for newer YouTube versions, including the YouTube glass tab bar (`YTFloatingPivotBarView`).

### Design system (new: `Tweak/MarufYT/Design/MarufYTTheme`)
- Semantic, dynamic colours for light, dark and OLED.
  - A restrained cobalt accent (#3563D9 light, #7C9CFF dark) replaces YouTube red. It is used only for switches, sliders, steppers, checkmarks and the search caret.
  - Values are secondary grey.
  - Surfaces are iOS-style grouped pages with card cells.
- Dynamic Type everywhere in settings (body, subheadline, footnote, monospaced-digit readouts), instead of fixed 10–17 pt sizes.
- Native row heights (self-sizing, no fixed 40 pt rows), full-size switches (no 0.95 scaling) and hairline colour swatches.
- Pickers show the value with an up/down chevron, the iOS pop-up menu affordance.

### Settings
- The main screen, all settings pages, the tab editor and the search results are now inset-grouped.
- Main menu: Settings-style coloured icon tiles.
- About shows Developer (arifular1f), Repository (arifular1f/MarufYT), Version (with CI build number), YouTube version and Package (ROOTLESS · arm64).
  - The Credits row is removed. Attribution stays in `LICENSE` and `THIRD_PARTY_NOTICES.md`.
  - The device model and bundle ID are no longer shown.
- SponsorBlock is regrouped into Main, Alerts, DeArrow, Skipping and Segment Colors.
  - Skipping has one row per category, with its colour dot.
  - Every key, option and default is unchanged.
- The Liquid Glass page adds a *Floating Tab Bar Depth* toggle.

### Branding
- All user-visible names, dialogs, the tab title, the library title, the settings group and the 15 localizations show MarufYT.
- The AiSList user agent and default reporter name are MarufYT.
- The tab-bar mode formerly called "YTKACE" is now called "MarufYT".

### Liquid Glass
- Adapted the preset to upstream's new tab-bar mode setting (Default, MarufYT capsule, YouTube, Off). The MarufYT capsule is preferred only when you have stored neither a mode nor the legacy switch.

### Build and tools
- The CI build step fails on compiler errors (`pipefail`) and stamps the run number into the build.
- `Tools/marufyt_host_audit.py` (static host compatibility audit) and `Tools/phase2_apply.py` (record of the Phase 2 transformation) are added.
- The packager finds `YTKACE.bundle` in either deb layout and removes `AppMigrationExtension.appex`, as upstream's sideload script does.

## 1.1.1+marufyt.1 (2026-11-02)

The first MarufYT release, based on YTKACE 1.1.1. It added branding, About, Credits, the Liquid Glass preset, the floating tab-bar depth layer, CI and the packager. The source is kept on branch `stable-21.39.4`.
