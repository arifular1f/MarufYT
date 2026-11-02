# MarufYT

MarufYT is a YouTube enhancement for iOS by [arifular1f](https://github.com/arifular1f). It is built on [YTKACE](https://github.com/itzzace/ytkace) by itzzace (MIT).

It runs inside the original YouTube app. Google sign-in, account switching and YouTube's own interface are kept. It needs no extra account, has no activation service, and sends no analytics.

## Features

These come from YTKACE and are kept unchanged:

- Ad blocking: feed, sponsored app cards, video, Shorts and upsell prompts
- SponsorBlock and DeArrow
- Video, audio, Shorts and playlist downloads, with a download library
- Background playback, Picture-in-Picture, speed, loop and sleep timer
- Gestures, quality presets, and Shorts, feed and tab customization
- Liquid Glass tab bar, top bar, menus, toasts and player buttons (iOS 26 and later)

MarufYT adds:

- MarufYT branding, plus an About section with Repository, Developer and Credits rows
- A Liquid Glass design preset: glass surfaces are on by default where `UIGlassEffect` exists, and any setting you change yourself is kept
- A floating tab-bar depth layer: a soft shadow drawn outside the glass capsule only, so the glass itself never darkens

## Compatibility

| Item | Value |
| --- | --- |
| YouTube | 21.39.4 (the host YTKACE 1.1.1 was released for) |
| iOS | 15 or later for the tweak; 17 or later for the YouTube 21.39.4 IPA; Liquid Glass needs 26 or later |
| Package | ROOTLESS (`iphoneos-arm64`) |

## Building

See [BUILD_INSTRUCTIONS.md](Documentation/BUILD_INSTRUCTIONS.md).

GitHub Actions builds the ROOTLESS `.deb` and `MarufYT.dylib`. The IPA is assembled locally from a decrypted YouTube that you supply. No YouTube binaries are stored in or downloaded by this repository.

## Licence

MIT. See `LICENSE` and `THIRD_PARTY_NOTICES.md`. FFmpeg is LGPL. SponsorBlock data is CC BY-NC-SA 4.0.

The upstream README is kept as `UPSTREAM_README.md`.
