# Privacy

MarufYT runs entirely inside your YouTube app.

Maintainer: [arifular1f](https://github.com/arifular1f). This document describes the tweak's reviewed behaviour; physical-device verification remains pending.

**MarufYT does not have:**

- analytics, telemetry, crash reporting or tracking;
- an updater;
- an account or activation server.

**The project operates no servers.**

## Network connections

| Destination | When | What is sent |
| --- | --- | --- |
| YouTube and Google (`youtubei.googleapis.com`, `www.youtube.com`, `*.googlevideo.com`, `i.ytimg.com`) | Playback fixes, downloads, playlist downloads, quality and caption features | The same kind of requests the YouTube app makes. Playlist downloads may use your current YouTube sign-in to read playlists you can access. It is used only for these Google requests and is never stored or logged |
| SponsorBlock (`sponsor.ajay.app`) | When SponsorBlock is on, for each video you watch | The video ID (to fetch segments) |
| SponsorBlock: voting or submitting segments | Only when you vote or submit from the player | The segment data, plus a random SponsorBlock user ID created on your device |
| DeArrow (`sponsor.ajay.app`, `dearrow-thumb.ajay.app`) | When DeArrow titles or thumbnails are on | The video ID |
| AiSList lists (`raw.githubusercontent.com/Override92/AiSList`) | When the AI-channel list feature is on | A standard download of the public lists; nothing about you |
| AiSList report (`api.aisloplist.com`) | Only when you tap "Report as AI channel" | The channel handle, video link, and the reporter name you set (default: "MarufYT") |

The table lists the fixed service destinations identified in the reviewed source. Media and artwork hosts can also come from service responses, and redirect destinations have not been captured on a device. No maintainer-operated activation or analytics endpoint was found. YouTube itself has its own network behaviour and privacy policy; this statement does not describe or control all host-app traffic.

## Data stored on your device

| Data | Location | Notes |
| --- | --- | --- |
| Settings | App preferences (sandbox) | Backups you create include only `YTKACE.Preference.*` settings |
| Downloads | `Documents/YTKACE` | Visible in the Files app by design, so you can manage them |
| Diagnostics log | `Library/Application Support/YTKACE/Logs` | Size-limited; backup exclusion/file protection are requested; selected bearer-token, URL-query and `key=value` patterns are redacted; clearable in the log viewer (long-press About → Version). Arbitrary JSON/header formats and backup behaviour are not certified without runtime tests |
| SponsorBlock user ID | App preferences | Random; used only for SponsorBlock votes and submissions; not included in settings backups |
| Caches (player solver, lists, artwork) | `Library/Caches` | Can be removed by iOS at any time |

## Permissions

- **Photos (add-only):** requested only when you save a download or image to Photos.

MarufYT does not request location, contacts, camera, microphone or tracking permission.

## Third-party services

SponsorBlock and DeArrow data is provided by the SponsorBlock project under CC BY-NC-SA 4.0. Its [privacy terms](https://sponsor.ajay.app/) apply. AiSList is a community project with its own terms.
