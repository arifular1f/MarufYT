# Remaining-item audit final report

Date: 2026-11-02 (Asia/Kuala_Lumpur). Continued from `dc7c458` on `phase2`; no main/default-branch change, history rewrite or release replacement.

## Results

1. **Supported automation implemented and exercised:** the existing registered workflow accepts `audit_only=true` on `phase2`. [Audit-only run 41412551311](https://github.com/arifular1f/MarufYT/actions/runs/41412551311) passed tests, locked-toolchain installation and isolated relinking. Native release compilation and package collection/upload were skipped. Default-branch-only weekly Dependabot scheduling remains inactive because main must not change.
2. **Transitive pins implemented:** fresh Theos commit checkout, eight explicit direct gitlinks plus recursively pinned descendants, compiler/SDK versioned assets with lengths/hashes, verified archive-only cache, bounded safe extraction. The former moving installer is not executed. Hosted image/apt/runner-runtime versions remain explicitly recorded residuals.
3. **FFmpeg provenance and relink materials completed:** signed source verified against the publisher's fingerprint; all 131 non-generated headers match after line-ending normalization; generated headers/configuration and unchanged library hashes mapped; full native consumer source and source/licence materials assembled locally. The successful probe actually replaced a static object and relinked a separate arm64 consumer. Full application rebuilding, historical bit-identical reproduction and blanket legal certification are not claimed.
4. **Static runtime review completed:** logging, storage/backup, authorization/redirects, Keychain, backup import, JavaScriptCore and service/parser boundaries inspected. A synthetic regex model documents both covered formats and remaining JSON/cookie-header gaps. No Foundation/iPhone execution or credential/service request was performed.
5. **All previous findings dispositioned:** see [the ID-by-ID table](FINDING_DISPOSITION.md). No open risk is silently relabelled fixed merely because a setting exists or CI is green.
6. **Packages preserved:** both Latest/Stable IPAs, both DEBs and all prior release/input files are checked against the pre-pass snapshot. No release output is rebuilt, deleted or overwritten. Supplementary evidence goes into a new local subdirectory.

## Actual tests and source provenance

- 13 unit tests (including cache-integrity, traversal and escaping-symlink cases) pass.
- 101 source checks pass; full reachable-history credential scanning runs in the audit workflow and locally.
- Pinned compiler and SDK archives were verified before execution; installed source/submodule/compiler/host-package provenance is uploaded.
- Relink evidence includes probe sources, objects, commands and both output hashes. Original vendored hash remains unchanged; the modified marker is present in the separate relinked output.
- First probe run [41412176944](https://github.com/arifular1f/MarufYT/actions/runs/41412176944) failed at the Darwin-style archive editor. The corrected implementation uses the LLVM archiver in the same pinned archive; the succeeding run above is the passing evidence.
- Implementation commits: `d7034bf` (locks/bootstrap/audit mode) and `135bf76` (portable archiver/evidence diagnostics). The final documentation commit publishes this report; exact publication SHA is recorded in the local final handoff and Git history.
- Existing native release provenance remains [41408429223](https://github.com/arifular1f/MarufYT/actions/runs/41408429223) at `34a1947`. Neither audit commit is represented as the source of those existing IPA/DEB bytes.

## Remaining limitations

- **Physical iPhone acceptance: NOT TESTED.** Launch, Google sign-in, account switching, signing/session continuity, features, layouts and performance remain unverified on device.
- **Default branch:** weekly configuration activation and the older main workflow cannot be fixed under the explicit no-main-change instruction. No external scheduler/token workaround is introduced.
- **Platform:** GitHub image/agent/runtime and signed Ubuntu package updates are not fully immutable. Compiler/SDK hashes were measured from versioned publisher HTTPS assets without an independent publisher signature; FFmpeg source has verified signature evidence.
- **Licence/provenance:** engineering correspondence/relink evidence is provided, but historical binary reproducibility, undocumented-source-patch exclusion and a full modified-library application/device test are not established. Applicable distribution obligations remain separate from this engineering audit.
- **Runtime security:** unsupported log formats/identifiers, redirects, effective file/backup protection and parser/resource exhaustion require further native testing or a separately versioned remediation. No vulnerability-free or fully sandboxed claim is made.

## Documents and local evidence

- [Default-branch/branch automation](DEFAULT_BRANCH_AUTOMATION.md)
- [Transitive toolchain pins](TRANSITIVE_TOOLCHAIN_LOCK.md)
- [FFmpeg source and LGPL relinking](FFMPEG_SOURCE_AND_RELINK.md)
- [Static runtime review](RUNTIME_SECURITY_STATIC_REVIEW.md)
- [All finding dispositions](FINDING_DISPOSITION.md)
- New local handoff: `release/MarufYT-Phase2.1/Remaining-Items-2026-11-02/`, including `Corresponding-Source/`, `CI-Evidence/`, signature/source/model reports, preserved-package checks and a supplementary SHA256 manifest.

Earlier reports, licence attributions, source bundles and per-host checksum manifests remain preserved as historical evidence. This report supersedes their remaining-item status without rewriting those releases.
