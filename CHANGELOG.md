# Changelog

## 1.1.1+marufyt.1 (2026-11-02)

Based on YTKACE 1.1.1 by itzzace.

### Added
- MarufYT branding module. The settings title, YouTube Settings group, tab name, dialogs and all 15 localizations show "MarufYT".
- About section: **Repository** (github.com/arifular1f/MarufYT), **Developer** (github.com/arifular1f) and **Credits**.
- Credits and licences page, listing YTKACE by itzzace, FFmpeg, SponsorBlock/DeArrow, the yt-dlp EJS solver, YTPlaybackFix, YTLiquidGlass, meriyah and astring.
- Liquid Glass preset. YTKACE's glass tab bar, top-bar buttons, menus, toasts and player buttons are on by default on iOS 26 and later. Your own choices are kept.
- Floating tab-bar depth: a soft shadow drawn only outside the glass capsule. Toggle it in *Liquid Glass → Floating Tab Bar Depth*.
- `Tools/marufyt_checks.py` (static regression checks) and `Tools/marufyt_package.py` (local IPA assembly).

### Changed
- The library is now `MarufYT.dylib`, and the package is `com.arifular1f.marufyt`. It conflicts with and replaces `com.itzzace.ytkace`.
- CI builds ROOTLESS only. The upstream IPA workflow (which downloaded YouTube from Dropbox) and the Pages workflow are removed.

### Unchanged
- All YTKACE features, hooks and preference keys. Existing settings and backups carry over.
- Google sign-in and the sideload compatibility hooks.
