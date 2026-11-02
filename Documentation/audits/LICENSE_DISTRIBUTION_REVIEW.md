# Ownership, branding and distribution evidence

Reviewed 2026-11-02, branch `phase2`. This records evidence and open obligations; it is not a blanket certification of distribution compliance.

Update: [FFMPEG_SOURCE_AND_RELINK.md](FFMPEG_SOURCE_AND_RELINK.md) records the signed-source/fingerprint verification, normalized header correspondence, distribution materials and isolated modified-object relink demonstration added after this baseline review. Historical bit-identical library reproduction and full-application/device execution are not asserted.

| Component | Ownership/licence evidence | Result |
| --- | --- | --- |
| YTKACE source | Pinned upstream `11249eef76801b2f6323ab094d37893a4098b4f7`, retained history and MIT notice | Attribution retained. MarufYT does not claim authorship of upstream work |
| MarufYT additions | Own copyright in LICENSE, provenance map and module headers | Maintainer `arifular1f`; source changes distinguished from upstream |
| Upstream README | Restored exact README bytes from the pinned upstream commit | Previously promised README link now resolves; historical upstream branding/donation content remains attributed to upstream |
| FFmpeg static libraries | Four vendored hashes match the previous dependency audit; LGPL-2.1 and LGPL-3 texts, headers and build script present | Version/configuration claims alone do not establish exact corresponding-source provenance or a tested relink path |
| yt-dlp EJS / meriyah / astring | Both vendored solver hashes match the previous audit; notices and embedded licence headers retained | Attribution evidence present; not a fresh upstream security certification |
| YTPlaybackFix | MIT notice retained in adapted source and third-party notices | Attribution retained |
| SponsorBlock / DeArrow | Service/artwork/data attribution in third-party notices | Separate data/service terms apply; MIT does not relicense those assets or data |
| YouTube / Apple / Google | User-supplied host, system frameworks, runtime SF Symbols | Not owned or relicensed by MarufYT. MIT applies to the project's licensed code, not the host application or trademarks |

FFmpeg's publisher asks distributors to provide source matching the shipped binaries and build information. Static linking also needs an appropriate modification/relink route under the applicable LGPL terms. Existing source/build scripts are useful evidence, but this audit did not reconstruct the historical library build from an authenticated source archive or demonstrate end-to-end relinking. Keep that item open before broader binary distribution; do not describe the presence of licence files alone as full compliance.

Primary references: [FFmpeg publisher licence guidance](https://ffmpeg.org/legal.html), [publisher-maintained guidance source](https://github.com/FFmpeg/web/blob/master/src/legal), and [GNU explanation of static LGPL linking](https://www.gnu.org/licenses/gpl-faq.html#LGPLStaticVsDynamic).

## Distribution checklist

- Keep the YTKACE and MarufYT copyright notices, component notices and licence texts with the source distribution.
- Preserve a source snapshot and toolchain provenance for each binary release; do not claim a later tools/documentation commit produced an earlier binary.
- Record the exact FFmpeg corresponding source, any local patches, configuration and library hash mapping; demonstrate that a recipient can modify/relink the LGPL component.
- Retain service/artwork/data attribution and check their separate terms for the intended distribution.
- Keep original Google/YouTube binaries, user certificates, account credentials and private configuration outside the public source repository.
- Treat device behaviour, signing compatibility, asset provenance, source correspondence and security as separate verification questions.

The existing Phase 2 and Phase 2.1 release archives remain unchanged. These documentation corrections do not certify runtime testing or change any licence grant.
