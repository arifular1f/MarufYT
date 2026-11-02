# Privacy and Data-Flow Audit (Phase 4)

**Method:** static. Source under `Tweak/`, the compiled `MarufYT.dylib` (string, symbol and class scans) and the Info.plist of both IPAs.
**Not done:** dynamic network observation. No device or proxy capture was available, so **this report does not claim that MarufYT sends no data**. It states what the code is able to send. Runtime capture (e.g. a proxy with a test account) remains **Not tested**.

## Traffic classes

| Class | Meaning | Attributed to MarufYT? |
| --- | --- | --- |
| A | YouTube host-app traffic | No. Not analysed here |
| B | MarufYT-specific requests | Yes (below) |
| C | Upstream YTKACE feature requests (downloads, playback fixes, transcripts) | Yes, inherited code, same destinations |
| D | External services: SponsorBlock, DeArrow, AiSList | Yes, opt-in |

## Endpoints found (source and compiled library agree)

`youtubei.googleapis.com`, `www.youtube.com`, `youtube.com`, `youtu.be`, `i.ytimg.com`, `sponsor.ajay.app`, `dearrow-thumb.ajay.app`, `raw.githubusercontent.com` (AiSList lists), `api.aisloplist.com`, `github.com` (links the user can open). Other strings (`w3.org`, `aomedia.org`, `streams.videolan.org`) are XML namespaces or codec/library text, not endpoints. Media URLs (`*.googlevideo.com`, avatars) arrive in YouTube responses at runtime. Not found: analytics, advertising, crash-reporting or remote-config SDKs (Firebase, Crashlytics, Sentry, Mixpanel, Amplitude, AppsFlyer, Flurry, AppCenter, Bugsnag: absent); no hard-coded IP address.

## Data-flow table

| Source / data | Component | Purpose | Destination | Transport | Class | Finding |
| --- | --- | --- | --- | --- | --- | --- |
| Video ID + category list | `SponsorClient.mm` | Fetch skip segments | `sponsor.ajay.app` | HTTPS | D | Off by default. Full ID sent (S-02) |
| Segment votes/submissions + random SponsorBlock user ID | `SponsorHooks/Menu` | Vote or submit | `sponsor.ajay.app` | HTTPS | D | Only on user action |
| Video ID | `DeArrow.mm` | Titles, thumbnails | `sponsor.ajay.app`, `dearrow-thumb.ajay.app` | HTTPS | D | Off by default |
| None (public lists) | `AiSList.mm` | Channel block/warn lists | `raw.githubusercontent.com` | HTTPS | D | Off by default; refresh when stale; ≤ 8 MiB; cached in Caches |
| Channel handle, video link, reporter name (default "MarufYT") | `AiSListReport.mm` | Report AI channel | `api.aisloplist.com` | HTTPS | D | Only on explicit tap + confirm |
| Video/playlist ID, client context, YouTube bearer token (playlist downloads only), visitor data | `PlaylistDownloader`, `DirectDownloader`, `HLSPlayback`, `TVClient`, `SABRDownloader` | Playback fixes, downloads | `youtubei.googleapis.com`, `*.googlevideo.com` | HTTPS | C | Token only to the fixed `youtubei` URL (S-03). Client model/OS strings are constants except SABR, which sends `UIDevice.systemVersion` to YouTube as the YouTube app does |
| Video ID | `QueueHooks.mm` | oEmbed title/thumbnail | `www.youtube.com` | HTTPS | C | |
| Avatar / post-image / caption URL (from YouTube objects) | `ProfilePictureViewer`, `PostImageSaver`, `TranscriptExport` | Preview, save, transcript | Host named by YouTube | HTTPS only (S-01 fix) | C | Shared session: normal cookies for that host |
| Thumbnails | `PlaylistDownloader`, `QueueHooks` | Artwork | `i.ytimg.com` | HTTPS | C | |

## Category checklist

| Category | Accessed by MarufYT? | Stored locally? | Transmitted? | Notes |
| --- | --- | --- | --- | --- |
| Device identifiers (IDFV/IDFA) | **No**: `identifierForVendor`, `advertisingIdentifier`, `ASIdentifierManager` absent from the dylib | — | — | `NSUserTrackingUsageDescription` is YouTube's |
| IP address | Implicit in any connection | No | Seen by the endpoints above | Unavoidable |
| Location, contacts, camera, microphone | **No** code | — | — | Usage strings in the plist are YouTube's |
| Photos | Add-only write on user save | Photos library | No | `PHPhotoLibrary requestAuthorization(AddOnly)` |
| Clipboard | **Write only** on user actions (copy comment, transcript, log). No reads found | — | No | |
| Search / watch history, browsing | **No** collection code. Video IDs of watched videos are sent to SponsorBlock/DeArrow only when those are on | Short in-memory caches | See table | |
| Account info, auth tokens | Bearer token read in memory for playlist downloads | Not stored, not logged | Only to `youtubei.googleapis.com` | S-03 |
| Keychain | Own dummy item to learn the access group | Own keychain | No | S-05 |
| Downloaded files, Documents | Own `Documents/YTKACE` | Yes, visible in Files | No | Backups are local zips the user creates |
| Device model / OS | Constants, plus `systemVersion` in SABR | — | To YouTube | See above |
| Analytics / crash / telemetry | **No** SDK or code found | — | — | |
| Diagnostics log | Written locally | `Library/Application Support/YTKACE/Logs`, excluded from backup, redacted, ≤ 512 KiB | **No** (user must copy it manually) | |

## Documentation

`PRIVACY.md` lists these destinations and was already consistent with the table. The `README` no longer says "sends no analytics" as an absolute; it states the verified source and binary findings and says plainly that device capture has not been done.

## Open items

1. Dynamic capture with a test account (**Not tested**).
2. SponsorBlock hash-prefix endpoint (S-02): decision needed.
3. Redirect handling of the `Authorization` header (S-03).
