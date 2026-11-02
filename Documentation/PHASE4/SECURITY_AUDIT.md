# Security Audit (Phase 4)

Scope: source at the Phase 3 head (`0cebe48`), the compiled `MarufYT.dylib` (`bec57086…`, build `1.1.4+marufyt.5`) and the two Phase 3 IPAs. Method: source reading, `grep` over `Tweak/`, string and symbol scans of the dylib, and a full-history secret scan (`Tools/marufyt_secret_scan.py`: 28 refs, 189 commits, 1,647 blobs, **0 findings**).

Status words: **Verified**, **Fixed**, **Not vulnerable (evidence)**, **Needs investigation**, **Not tested**.

## Findings

| ID | Severity | Location | Evidence | Impact | Disposition |
| --- | --- | --- | --- | --- | --- |
| S-01 | Low | `PostImageSaver.mm`, `ProfilePictureViewer.mm`, `TranscriptExport.mm` | Image and caption URLs taken from YouTube objects were passed to `NSURLSession` without a scheme check | A malformed or downgraded `http://` URL could be requested in clear text (the host's ATS would normally block it; that was not relied on) | **Fixed**: `Tweak/Runtime/URLPolicy.h` `MarufYTIsSecureURL()` requires https and a host before each fetch; static check added. Not exercised on a device |
| S-02 | Low (privacy) | `SponsorClient.mm` | `GET https://sponsor.ajay.app/api/skipSegments?videoID=<id>` sends the full video ID | The SponsorBlock server sees each watched video ID while SponsorBlock is on. SponsorBlock also offers a 4-character SHA-256-prefix endpoint that reveals less | **Needs decision**: switching changes the response format and cannot be device-tested here, so it was not changed blind. `PRIVACY.md` already says the video ID is sent |
| S-03 | Info | `PlaylistDownloader.mm` (`YTKACEPlaylistAuthHeader`) | The YouTube bearer token comes from the host's authorizer and is set as `Authorization` only on requests to the hard-coded `https://youtubei.googleapis.com/youtubei/v1/browse`, on an ephemeral session with cookies off. Log lines are redacted for `Bearer …` | Token is not sent to any MarufYT-operated or third-party host | **Not vulnerable (source)**. Redirect behaviour was not observed (Foundation normally strips `Authorization` on cross-host redirects; not verified here): **Needs investigation** |
| S-04 | Info | `YTKACEBackupManager.mm` (restore) | Entries must be `SettingsBackup.plist` or `Downloads/…`; paths are standardized and `..` or absolute paths are rejected; only stored (uncompressed) entries are accepted, CRC is verified, files are created in a fresh temp directory | Path traversal or zip bomb through a crafted backup | **Not vulnerable (source)**. Not fuzzed |
| S-05 | Info | `SideloadCompatibility.mm` | `SecItemAdd/CopyMatching` only on a dummy item (`YTKACEDummyItem`) to learn the app's own keychain access group | No other keychain item is read | **Verified** |
| S-06 | Info | whole tweak | No `NSLog`. No custom TLS trust (`didReceiveChallenge`, `allowsInvalidCertificates` absent). The dylib imports no `system`, `popen`, `posix_spawn`, `exec*`, `fork`, `dlopen` or `ptrace` | No command execution, no TLS bypass | **Verified** |
| S-07 | Info | `YTKACERootOptionsController.mm` | Long-pressing About → Version for 3 s opens the local diagnostics log and writes a layout snapshot | Local only, no remote trigger, no network call. Not a backdoor | **Verified**, documented |
| S-08 | Info | `Tools/marufyt_package.py` | Packaging sets `UIFileSharingEnabled` and `LSSupportsOpeningDocumentsInPlace` so downloads in `Documents/YTKACE` appear in Files | Anyone with the unlocked phone can browse downloaded media in Files | By design; documented in `PRIVACY.md`. The diagnostics log is not in Documents |
| S-09 | Info | `DirectDownloader.mm`, `HLSPlayback.mm`, `TVClient.mm`, `PlaylistDownloader.mm` | Requests present constant client identities (visionOS, TV, iOS 18.6 / `iPhone16,2`) to `youtubei.googleapis.com` | Not a leak (constants). May conflict with YouTube's terms | Noted; outside security scope |
| S-10 | Unknown | `TVClient.mm`, `HLSPlayback.mm`, `DirectDownloader.mm`, `PlaylistDownloader.mm` | `dispatch_semaphore_wait` after `NSURLSession` tasks (up to 35 s) | If run on the main thread the UI would freeze | **Needs investigation**: callers were not traced to prove they run off the main thread. `AiSList.mm` runs on a utility queue |
| S-11 | n/a | memory safety | No sanitizer, fuzzing or static-analyzer run | Unknown | **Not tested** |
| S-12 | Info | secrets | Full-history scan, current tree, both IPAs' `Info.plist` and the dylib show no key, token or certificate patterns. `.gitignore` blocks `*.p12 *.mobileprovision *.pem *.key *.ipa *.deb` | — | **Verified** (pattern scan only) |

## Not covered

Third-party binaries inside the user-supplied YouTube IPA, FFmpeg's own code, and runtime behaviour on a device.
