# Dependency audit: MarufYT (branch `phase2`)

Current update: [TRANSITIVE_TOOLCHAIN_LOCK.md](TRANSITIVE_TOOLCHAIN_LOCK.md) supersedes the historical installer/latest-download description below. [FFMPEG_SOURCE_AND_RELINK.md](FFMPEG_SOURCE_AND_RELINK.md) records the newly authenticated source and actual isolated link demonstration. Existing vendored/release bytes remain unchanged.

Date: 2026-11-02.

## Build-time

| Dependency | Version / pin | Verification | Notes |
| --- | --- | --- | --- |
| `actions/checkout` | v6.1.0 @ `d23441a48e516b6c34aea4fa41551a30e30af803` | SHA pin; repository requires SHA pinning | `persist-credentials: false` |
| `actions/cache` | v4.3.0 @ `0057852bfaa89a56745cba8c7296529d2fc39830` | SHA pin | Cache key includes the Theos commit |
| `actions/upload-artifact` | v7.0.2 @ `cf430e030ddbb5b0abf93d22962f4752f3646cd9` | SHA pin | 30-day retention |
| roothide/theos | `3ac89c984ec652fd16bcd91b33ae16de45ce76fa` (2026-10-28) | `bin/install-theos` SHA-256 `b9a86c31d0ef7b3f029c484160bbc034e1700688c07f528c8a0f49f123dc7d60`; checkout at the commit | SDK and toolchain come from the installer's "latest" (residual risk L4); versions are recorded in `provenance.txt` |
| Runner images | `ubuntu-latest` (tests), `ubuntu-24.04` (build) | GitHub-hosted | The build is held on 24.04 because the Theos installer needs `libxml2` |
| Python tooling | Standard library only | — | No pip packages |

## Vendored (in the repository)

| Component | Licence | Files and SHA-256 |
| --- | --- | --- |
| FFmpeg 8.1.2 (upstream-built, LGPL; no `--enable-gpl` / `--enable-nonfree`) | LGPL-2.1+ | `libavcodec.a` `bdc2d8386edc0834c2cc4faed0be4aa06e6585d5957c38b48cf369b1411e9c5a`; `libavformat.a` `f65df5d33fef83861b997807673e5edbd7c1f4f9e364ad3f2962841401ce695e`; `libavutil.a` `9078a6b37af3bf47b0f0e6142ec45f0995f8ebffe701717ea5e11b57fe425df3`; `libswscale.a` `b46f06e3eb3d0dd49c68aa60a82603a4599b78ea9b1a3b5a41c42d2a7ce5692d` |
| yt-dlp EJS solver 0.8.0 (bundles meriyah, ISC, and astring, MIT) | Unlicense / ISC / MIT | `yt.solver.core.min.js` `333f68fff3afa5761db121a7af203dd61da8215cc1f58ffb6e4f3df63da224c5`; `yt.solver.lib.min.js` `4958f109843696fe5f7d38322e7390f23bae46b0b7c082c4377f0defbc7fa31c` |
| YTKACE (upstream source) | MIT | Merged from `itzzace/ytkace` `main` @ `11249ee`; full history kept |

**FFmpeg rebuild path:** `Scripts/build-ffmpeg.sh` now requires a verified `FFMPEG_SHA256` (see BUILD_INSTRUCTIONS §3).

**Licence evidence:** FFmpeg is linked statically; the LGPL texts and build script are present. This alone does not establish complete distribution compliance. Corresponding-source availability and a usable modification/relink path need to be documented for the exact vendored binaries. See `LICENSE_DISTRIBUTION_REVIEW.md`; no blanket compliance certification is made.

## Runtime

| Dependency | Notes |
| --- | --- |
| iOS system frameworks and libraries | All 23 `MarufYT.dylib` load commands point to `/System/Library` or `/usr/lib`. No CydiaSubstrate or ElleKit linkage (hooks use the Objective-C runtime) |
| Host app | YouTube 21.43.5 or 21.39.4, supplied by the user; never redistributed by this repository |

## External services (runtime)

| Service | Purpose |
| --- | --- |
| Google / YouTube | Playback, downloads, playlists |
| SponsorBlock / DeArrow (`sponsor.ajay.app`, `dearrow-thumb.ajay.app`) | Segments and branding (CC BY-NC-SA 4.0 data) |
| AiSList (`api.aisloplist.com`, GitHub raw) | Optional AI-channel lists and reports |

There is no MarufYT-operated service.

## Update policy

- **Actions:** weekly updates are configured on `phase2` but inactive while `.github/dependabot.yml` is absent from the default branch. Repository security alerts are a separate setting. Keep manual review until a default-branch change is explicitly authorized.
- **Theos:** move it deliberately by updating `THEOS_COMMIT` and `THEOS_INSTALLER_SHA256` together.
- **Upstream YTKACE:** merge tagged releases or reviewed `main` commits into a branch. Run `Tools/marufyt_checks.py`, `Tools/marufyt_secret_scan.py` and `Tools/marufyt_host_audit.py` before releasing.
