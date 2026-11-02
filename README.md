# MarufYT

**A YouTube enhancement for iOS, maintained by [arifular1f](https://github.com/arifular1f).**

[![Build](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml/badge.svg?branch=phase2)](https://github.com/arifular1f/MarufYT/actions/workflows/build.yml)
![Package](https://img.shields.io/badge/package-ROOTLESS%20arm64-blue)
![Licence](https://img.shields.io/badge/licence-MIT-green)

MarufYT runs inside the original YouTube app. Google sign-in, account switching and YouTube's own interface are kept. It needs no extra account, has no activation service, and sends no analytics ([PRIVACY.md](PRIVACY.md)).

MarufYT is built on [YTKACE](https://github.com/itzzace/ytkace) by itzzace (MIT). See [Credits](#credits).

## Features

- **Ad blocking:** home-feed ads, sponsored app cards, video and Shorts ads, upsell prompts
- **SponsorBlock and DeArrow:** per-category skipping, alerts and segment colours
- **Downloads:** video, audio, Shorts, playlists and subtitles, with a download library
- **Playback:** background audio, Picture-in-Picture, speed and custom speed, loop, sleep timer, gestures, quality presets, captions
- **Customization:** Shorts, home feed, watch page, top bar and tabs
- **Liquid Glass (iOS 26+):** a floating glass tab bar with depth, plus glass top-bar buttons, menus, toasts and player buttons
- **MarufYT settings:** native iOS design (inset-grouped cards, Dynamic Type, restrained accent, Settings-style icons) in 16 languages, with an About section (developer, repository, version, YouTube version, package)

## Versions

| Branch | MarufYT | YouTube | Status |
| --- | --- | --- | --- |
| `phase2` | 1.1.4+marufyt.3 | 21.43.5 (latest) and 21.39.4 (stable fallback) | Development; awaiting device testing before promotion |
| `main`, `stable-21.39.4` | 1.1.1+marufyt.1 | 21.39.4 | Previous release |

The tweak needs iOS 15+. The YouTube 21.39.4 and 21.43.5 IPAs need iOS 17+, and Liquid Glass needs iOS 26+.

## Building

See [Documentation/BUILD_INSTRUCTIONS.md](Documentation/BUILD_INSTRUCTIONS.md).

- **CI:** GitHub Actions builds the ROOTLESS `.deb` and `MarufYT.dylib` with pinned, verified tooling.
- **IPA:** assembled locally from a decrypted YouTube that you supply. This repository never stores or downloads YouTube binaries.

## Security and privacy

- **Reporting vulnerabilities:** privately, see [SECURITY.md](SECURITY.md).
- **Data:** what MarufYT sends and stores is in [PRIVACY.md](PRIVACY.md).
- **Audit reports:** [current finding dispositions](Documentation/audits/FINDING_DISPOSITION.md), [pinned toolchain](Documentation/audits/TRANSITIVE_TOOLCHAIN_LOCK.md), [FFmpeg source/relink evidence](Documentation/audits/FFMPEG_SOURCE_AND_RELINK.md), [static runtime review](Documentation/audits/RUNTIME_SECURITY_STATIC_REVIEW.md), and [earlier reports](Documentation/audits/).

## Credits

MarufYT is a modified version of **YTKACE** by **itzzace** (MIT). Most features come from that project. The upstream history is preserved in this repository, and its README is kept as [UPSTREAM_README.md](UPSTREAM_README.md).

- **Code split:** what MarufYT changed or added is listed in [Documentation/SOURCE_PROVENANCE.md](Documentation/SOURCE_PROVENANCE.md).
- **Third-party components:** FFmpeg (LGPL), SponsorBlock/DeArrow data (CC BY-NC-SA 4.0), the yt-dlp EJS solver (Unlicense), YTPlaybackFix (MIT), and others are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Licence

MIT. See [LICENSE](LICENSE). It keeps the upstream copyright and adds the MarufYT copyright.
