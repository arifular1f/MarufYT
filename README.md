# MarufYT

**A lightweight YouTube enhancement for iOS, maintained by [arifular1f](https://github.com/arifular1f).**

[![Build](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml/badge.svg)](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml)
![Package](https://img.shields.io/badge/package-ROOTLESS%20arm64-blue)
![YouTube](https://img.shields.io/badge/YouTube-21.43.5%20%7C%2021.39.4-red)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

MarufYT runs inside the original YouTube app. Google sign-in, account switching and YouTube's own interface are kept. It has no account, no activation service and no updater of its own. It is built on [YTKACE](https://github.com/itzzace/ytkace) by itzzace (MIT); see [Credits](#credits).

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

The tweak itself targets iOS 15+, ROOTLESS, arm64. Branch `main` and `stable-21.39.4` hold earlier releases; development happens on feature branches (`phase4-security-privacy` is the latest).

## Install

You supply the YouTube app; this repository never contains or downloads it.

1. Get a **decrypted** YouTube IPA of a supported version (21.43.5 or 21.39.4).
2. Take the `.deb` from the latest [CI run](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml) artifact (`MarufYT-rootless`).
3. Assemble the IPA locally:

   ```sh
   python Tools/marufyt_package.py --youtube YouTube.ipa --deb com.arifular1f.marufyt_<version>_rootless.deb --output MarufYT.ipa
   ```

   The script injects `MarufYT.dylib`, removes other bundled tweaks and the app extensions that block sideloading (listed in the script), and never changes your input file.
4. **Sign** `MarufYT.ipa` with your own Apple ID or certificate using the sideloading tool you prefer, then install it. The IPA is unsigned by design.

Details, including the build environment: [Documentation/BUILD_INSTRUCTIONS.md](Documentation/BUILD_INSTRUCTIONS.md).

## Privacy and security

- MarufYT contains no analytics, advertising, crash-reporting or telemetry SDK (verified in source and in the compiled library; see the [data-flow audit](Documentation/PHASE4/PRIVACY_DATA_FLOW_AUDIT.md)).
- Its own network requests go only to the services listed in [PRIVACY.md](PRIVACY.md). SponsorBlock, DeArrow and AiSList are off by default; SponsorBlock can optionally send only a hash prefix of the video ID (Settings → SponsorBlock → Private Lookup).
- Network behaviour has been reviewed statically. It has **not** yet been captured on a device, so the project does not claim "zero data".
- Report vulnerabilities privately: [SECURITY.md](SECURITY.md). Audit reports: [Documentation/PHASE4/](Documentation/PHASE4/) and [Documentation/audits/](Documentation/audits/).

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
