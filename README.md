# MarufYT

**A lightweight YouTube enhancement for iOS, maintained by [arifular1f](https://github.com/arifular1f).**

[![Build](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml/badge.svg?branch=final-update-security)](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml)
![Package](https://img.shields.io/badge/package-ROOTLESS%20arm64-blue)
![YouTube](https://img.shields.io/badge/YouTube-21.43.5%20%7C%2021.39.4-red)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

MarufYT runs inside the original YouTube app. Google sign-in, account switching and YouTube's own interface are kept. It has no account, no activation service and no updater of its own. It is built on [YTKACE](https://github.com/itzzace/ytkace) by itzzace (MIT); see [Credits](#credits).

Current update: **1.1.4+marufyt.8**, on [`final-update-security`](https://github.com/arifular1f/MarufYT/tree/final-update-security), based on Phase 4.1. See the [final update report](Documentation/FINAL_UPDATE/FINAL_UPDATE_REPORT.md) for build evidence and remaining device tests. Protected/default branches have not been promoted.

## Features

- **Ad blocking:** home-feed ads, sponsored cards, video and Shorts ads, upsell prompts.
- **SponsorBlock and DeArrow:** per-category skipping and alerts; cleaner titles and thumbnails. Both are off until you turn them on.
- **Downloads:** video, audio, Shorts, playlists and subtitles, with an in-app library.
- **Playback:** background audio, Picture-in-Picture, speed, loop, sleep timer, gestures, quality presets, captions.
- **Customization:** Shorts, home feed, watch page, top bar and tabs.
- **Simple by default:** YouTube's own docked tab bar and normal Home layout. Optional Liquid Glass tab bars (iOS 26+) are one setting away.
- **Settings:** native inset-grouped iOS design in 16 languages.

## Supported versions

| Build | YouTube | iOS | Status |
| --- | --- | --- | --- |
| Latest | 21.43.5 | 17+ (Liquid Glass options need 26+) | Built and statically verified; on-device checks are listed in [DEVICE_TEST_RESULTS](Documentation/PHASE3/DEVICE_TEST_RESULTS.md) |
| Stable | 21.39.4 | 17+ | Same |

The tweak itself targets iOS 15+, ROOTLESS, arm64. Branch `main` and `stable-21.39.4` hold earlier releases; development happens on feature branches (`final-update-security` carries the current coordinated security update).

## Install

You supply the YouTube app; this repository never contains or downloads it.

1. Get a **decrypted** YouTube IPA of a supported version (21.43.5 or 21.39.4).
2. Take the `.deb` from a successful [Build run on `final-update-security`](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml?query=branch%3Afinal-update-security) for your exact source revision, artifact `MarufYT-rootless`. Verify its SHA256 manifest.
3. Assemble the IPA locally:

   ```sh
   python Tools/marufyt_package.py --youtube YouTube.ipa --deb com.arifular1f.marufyt_<version>_rootless.deb --output MarufYT.ipa
   ```

   The script injects `MarufYT.dylib`, removes other bundled tweaks and the app extensions that block sideloading (listed in the script), and never changes your input file.
4. **Sign** `MarufYT.ipa` with your own Apple ID or certificate using the sideloading tool you prefer, then install it. The IPA is unsigned by design.

Signing, migration and rollback: [Installation](Documentation/INSTALLATION.md). Details, including the build environment: [Documentation/BUILD_INSTRUCTIONS.md](Documentation/BUILD_INSTRUCTIONS.md).

## Privacy and security

- This update removes native authenticated request seeds from disk, purges old seed files and the raw outgoing protobuf dump, and adds memory expiry/account-boundary cleanup.
- MarufYT remote requests require HTTPS. Redirect policies separate ordinary requests from strictly allowlisted SABR media destinations; raw authorization/cookie headers are not replayed to media servers.
- Diagnostics are off by default. Opt-in diagnostics omit object payloads, credentials, URLs, email addresses and video-ID-shaped strings. No generic filter can certify arbitrary text is secret-free.
- SponsorBlock/DeArrow/AiSList remain opt-in. Private Lookup affects SponsorBlock lookup only; see [PRIVACY.md](PRIVACY.md) for transmitted data and remaining host-app behavior.
- No added telemetry SDK or maintainer account/activation service was identified in reviewed source. The original YouTube host still has its own permissions, cookies, analytics and network behavior.
- [Security policy](SECURITY.md), [pre-fix audit](Documentation/FINAL_SECURITY_AUDIT/FINAL_SECURITY_REPORT.md), [current update evidence](Documentation/FINAL_UPDATE/FINAL_UPDATE_REPORT.md). Device login, redirects, migration and feature regressions are **NOT TESTED** until actually exercised on an iPhone.

## Build from source

CI (GitHub Actions, pinned toolchain, read-only token) builds the ROOTLESS `.deb` and `MarufYT.dylib`. Local checks:

```sh
python Tools/marufyt_checks.py
python -m unittest discover -s Tests
```

## Project layout

| Path | Contents |
| --- | --- |
| `Tweak/` | Objective-C++ source: `Features/` (ads, downloads, playback, navigation …), `Settings/`, `UI/`, `Runtime/`, `MarufYT/` (branding, design) |
| `Resources/` | Settings bundle and the 16 localizations |
| `Tools/` | IPA packaging, static checks, host audit, secret scan |
| `Tests/` | Python and native layout tests |
| `Scripts/`, `Vendor/` | FFmpeg build and its pinned source |
| `Documentation/` | Build, modules, provenance, audits, per-phase reports (`PHASE3/`, `PHASE4/`, `history/`) |
| `docs/`, `screenshots/`, `web/` | Upstream YTKACE assets kept for attribution; see [UPSTREAM_README.md](UPSTREAM_README.md) |

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Credits

MarufYT is a modified version of **YTKACE** by **itzzace** (MIT). Most features come from that project and its history is preserved here. What MarufYT changed is listed in [Documentation/SOURCE_PROVENANCE.md](Documentation/SOURCE_PROVENANCE.md). Third-party components (FFmpeg LGPL, SponsorBlock/DeArrow data CC BY-NC-SA 4.0, the yt-dlp EJS solver, YTPlaybackFix and others) are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Licence

MIT. See [LICENSE](LICENSE); it keeps the upstream copyright and adds the MarufYT copyright.
