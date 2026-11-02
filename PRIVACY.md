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
| YouTube and Google (`youtubei.googleapis.com`, `www.youtube.com`, `*.googlevideo.com`, `i.ytimg.com`) | Playback fixes, downloads, playlist downloads, quality and caption features | The same kind of requests the YouTube app makes. Playlist downloads may use your current YouTube sign-in to read playlists you can access. It is used for these Google requests. The .8 update removes raw request-seed persistence; the original host and Foundation still manage their own session/cookie storage, and device behavior must be verified |
| SponsorBlock (`sponsor.ajay.app`) | When SponsorBlock is on, for each video you watch | The video ID (to fetch segments) |
| SponsorBlock with **Private Lookup** on (off by default) | Same, instead of the row above | Only the first 4 hex characters of the SHA-256 of the video ID. The server replies with every video sharing that prefix and MarufYT keeps its own. Your IP address and timing are still visible to the server |
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
| Diagnostics log | `Library/Application Support/YTKACE/Logs` | Size-limited; backup exclusion/file protection are requested; off by default; object payloads are omitted and credential/URL/email/video-ID patterns are filtered; clearable in the log viewer (long-press About → Version). Arbitrary unlabeled personal data and backup behaviour are not certified without runtime tests |
| SponsorBlock user ID | App preferences | Random; used only for SponsorBlock votes and submissions; not included in settings backups |
| Caches (player solver, lists, artwork) | `Library/Caches` | Can be removed by iOS at any time |

## Permissions

- **Photos (add-only):** requested only when you save a download or image to Photos.

No direct location, contacts, camera, microphone or tracking-permission request was identified in the reviewed tweak. The original YouTube host declares these capabilities and can request/use them with the applicable OS permissions. A dylib runs in the host process, not a separate privacy sandbox.

## Third-party services

SponsorBlock and DeArrow data is provided by the SponsorBlock project under CC BY-NC-SA 4.0. Its [privacy terms](https://sponsor.ajay.app/) apply. AiSList is a community project with its own terms.

## Coordinated .8 security update

Authenticated native headers/bodies are no longer written to request seed files. Legacy `sabr-seed.plist`, `player-request.pb` and the outgoing protobuf dump are queued for deletion from their exact old locations. Media and preferences are preserved. Existing copied files and old backups cannot be recalled; ordinary deletion is not forensic secure erase.

Captured request state is memory-only, expires lazily after 15 minutes of inactivity, and is cleared at recognized, ABI-guarded sign-out/account-removal/identity-change methods; active SABR sessions are cancelled. Those wrappers do not replace native Google account actions. Actual coverage, account switching, signing and foreground/background behavior require iPhone testing.

MarufYT-created remote requests use HTTPS guards and validated redirects. SABR media is restricted to Google video hosts with allowlisted non-Authorization/Cookie headers. Generic cross-origin redirects omit identifying service headers and reject body replay. This does not control every request inside the proprietary host or guarantee a complete list of runtime/redirect destinations. Device/locale/screen/timezone and visitor/PoToken context can be sent to Google media services; those attributes are not automatically anonymous.

Normal diagnostics and debug messages are now disabled unless the existing Debug Logs setting is enabled. When enabled, formatted object payloads/C strings are not interpolated; event templates/numeric data are retained with known sensitive formats omitted. The old diagnostics log is removed once during log-format migration. No log-upload service is added. Never share unreviewed logs or backups.

Current [security policy](SECURITY.md), [update evidence](Documentation/FINAL_UPDATE/FINAL_UPDATE_REPORT.md) and [historical pre-fix audit](Documentation/FINAL_SECURITY_AUDIT/FINAL_SECURITY_REPORT.md) distinguish source/static results from actual device tests. No current screenshots were supplied, so no screenshot or test result was fabricated.
