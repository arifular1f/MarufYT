# FFmpeg source provenance and LGPL relink evidence

Date: 2026-11-02. The four existing vendored libraries and all release packages remain unchanged.

## Authenticated source and correspondence evidence

| Item | Recorded evidence |
| --- | --- |
| Release | FFmpeg 8.1.2 |
| Archive | `https://www.ffmpeg.org/releases/ffmpeg-8.1.2.tar.xz` |
| SHA-256 | `464beb5e7bf0c311e68b45ae2f04e9cc2af88851abb4082231742a74d97b524c` |
| Detached signature | Same URL with `.asc` appended |
| Signing key fingerprint | `FCF986EA15E6E293A5644F10B4322F04D67658D8`, matching FFmpeg's published release-key fingerprint |
| Signature result | GnuPG verification returned success and a matching `VALIDSIG`; no owner-trust setting was fabricated |
| Header comparison | All 131 non-generated public headers match the signed release after CRLF/LF normalization; two generated headers are tracked separately |
| Embedded library configuration | Static build, iOS 15 arm64, file protocol, selected demuxers/codecs, network disabled; no `--enable-gpl` or `--enable-nonfree` in the recorded configuration |
| Historical binary provenance | Library hashes match the prior audit; version/configuration strings and generated version header identify 8.1.2 |

`Tools/ffmpeg-source.lock.json` stores the source digest and signing reference. The existing rebuild script defaults to that authenticated digest and refuses a reused source directory, so checking an archive no longer silently authorizes an old modified source tree. Other versions still require an explicit verified digest. Configuration flags and native feature code are not changed.

The new local handoff includes the source tarball, detached signature, public release key, licence texts, complete MarufYT source snapshot for the binary-source commit, configuration/provenance evidence and relink instructions. Original distribution files and notices remain intact. The upstream source build paths found in library strings are not republished as private configuration; the documentation describes flags with installation paths generalized.

## Actual relink demonstration

The audit-only workflow runs:

```sh
python3 Tools/relink_probe.py --theos "$THEOS" --output relink-evidence
```

It compiles a small source-available arm64 consumer of `av_version_info`, links it against the unmodified `libavutil.a`, creates a separate library copy, replaces only `version.o` with a deliberately modified implementation, and links the same consumer again. The output checks require the modified marker in the new binary, different output hashes, and an unchanged original library hash. All commands, probe sources, objects and hashes are retained as evidence.

This demonstrates actual static-object replacement and linking, not merely a visible source file or proposed command. The test is not a full MarufYT rebuild, does not produce a replacement IPA/DEB, and does not execute the arm64 outputs on an iPhone. LLVM's archiver from the pinned compiler archive is used; the first attempt with the Darwin-style archiver failed and is retained as failed evidence.

## Recipient modification/relink path

1. Retain the MIT project source, full third-party notices, FFmpeg licence texts and exact signed source materials with the distribution.
2. Verify the archive digest and detached signature against the published fingerprint. Do not treat an unauthenticated hash supplied alongside a download as equivalent to that verification.
3. In a separate source checkout/build directory, modify FFmpeg and regenerate its static libraries using the provided configuration. Record patches and the chosen compiler/SDK. Preserve the original libraries and releases; do not run a rebuild script against the only copy of them.
4. Replace the libraries in that separate MarufYT checkout, run its tests and `make package FINALPACKAGE=1 THEOS_PACKAGE_SCHEME=rootless`, and keep the relinked module/output separate. The module source is MIT and no project restriction on modifying/relinking or reverse engineering the LGPL component is added.
5. If testing a sideloaded app, use your legitimately supplied host and compatible signing. Re-signing, app-store host rights and on-device function are independent of LGPL engineering evidence.

## Limits and distribution status

The authenticated source, exact header correspondence, configuration strings, licence texts, full consumer source and successful isolated relink provide substantially stronger evidence than the earlier build-script-only claim. They do not establish bit-identical reproduction of the historical libraries or rule out undocumented implementation patches without an upstream build attestation. A full modified-library MarufYT application rebuild and physical installation are not claimed. This document completes the engineering evidence/distribution checklist; it does not issue a blanket legal-compliance certification.

Before wider redistribution, retain exact corresponding materials and review all applicable licence conditions for the actual distribution. FFmpeg/data/artwork/host ownership is not transferred by MarufYT's MIT licence. Configuration-specific vulnerability reachability and native-media fuzzing remain separate security questions; a source signature does not prove absence of vulnerabilities.

Primary references: [FFmpeg release-key guidance](https://ffmpeg.org/download.html), [publisher licence guidance](https://ffmpeg.org/legal.html), [GNU static LGPL explanation](https://www.gnu.org/licenses/gpl-faq.html#LGPLStaticVsDynamic), and the existing [distribution review](LICENSE_DISTRIBUTION_REVIEW.md).
