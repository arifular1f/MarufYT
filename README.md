# MarufYT

MarufYT is a YouTube enhancement for iOS by [arifular1f](https://github.com/arifular1f). It is built on [YTKACE](https://github.com/itzzace/ytkace) by itzzace (MIT).

It runs inside the original YouTube app. Google sign-in, account switching and YouTube's own interface are kept. It needs no extra account, has no activation service, and sends no analytics.

## Features

These come from YTKACE and are kept unchanged:

- Ad blocking: feed, sponsored app cards, video, Shorts and upsell prompts
- SponsorBlock and DeArrow
- Video, audio, Shorts, playlist and subtitle downloads, with a library
- Background playback, Picture-in-Picture, speed, loop and sleep timer
- Gestures, quality presets, captions, and Shorts, feed, watch-page, top-bar and tab customization
- Liquid Glass tab bar, top bar, menus, toasts and player buttons (iOS 26 and later)

MarufYT adds:

- A native iOS settings design system: inset-grouped cards, Dynamic Type, restrained accent colour, grey values and Settings-style icons
- An About section with Developer, Repository, Version, YouTube version and Package
- A regrouped SponsorBlock page
- A Liquid Glass preset, and a depth layer under the floating tab bar

## Branches

| Branch | YouTube host | Status |
| --- | --- | --- |
| `phase2` | 21.39.4 and 21.43.5 | Current development; source based on upstream `main` |
| `stable-21.39.4` / `main` | 21.39.4 | Previous release (1.1.1+marufyt.1) |

## Building

See [BUILD_INSTRUCTIONS.md](Documentation/BUILD_INSTRUCTIONS.md).

GitHub Actions builds the ROOTLESS `.deb` and `MarufYT.dylib`. The IPA is assembled locally from a decrypted YouTube that you supply. No YouTube binaries are stored in or downloaded by this repository.

## Licence

MIT. See `LICENSE` and `THIRD_PARTY_NOTICES.md`. FFmpeg is LGPL. SponsorBlock data is CC BY-NC-SA 4.0.

The upstream README is kept as `UPSTREAM_README.md`.
