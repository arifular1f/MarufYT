# MarufYT Phase 2 follow-up audit

Subsequent remaining-item closure: [FINDING_DISPOSITION.md](FINDING_DISPOSITION.md), with concrete toolchain, automation, FFmpeg and static runtime evidence. Earlier limitations below are retained as the dc7c458 checkpoint rather than rewritten history.

Date: 2026-11-02 (Asia/Kuala_Lumpur). Starting point: clean `phase2` at `34a19471e404e40b33e0c6ef9f2185b441bc5329`.

The earlier security pass and the `1.1.4+marufyt.3` release were already completed. The latest successful native build is [41408429223](https://github.com/arifular1f/MarufYT/actions/runs/41408429223). The older `.2` Phase 2 release is retained as well. This follow-up changes security tooling, tests and documentation only; native sources, resources, vendored libraries, package metadata and release binaries are preserved. No rebuild or promotion is needed for those changes.

## Completed follow-up work

- Hardened the credential scanner: findings contain locations/fingerprints instead of credential text; binary content is included; every unique committed tree is checked for sensitive filename aliases; staged versions and visible working files are included; shallow history is rejected.
- Added regression fixtures for redaction, binary-embedded matches, sensitive names, historical aliases, staged-only credentials and untracked content. Fixtures construct synthetic values; no real credentials are used.
- Expanded ignore rules for local signing material and credentials. Ignored files are not claimed scanned merely because visible working files are scanned.
- Restored `UPSTREAM_README.md` exactly from the pinned upstream commit. The previous README and attribution reports promised this file, but it was absent.
- Corrected the scope of workflow/Dependabot, account-authorization, privacy and licensing claims. Earlier static checks and zero alert counts are not presented as a full runtime or dependency-security certification.
- Reviewed current GitHub security settings and SHA pins; verified the pinned installer digest and vendored component hashes against prior evidence. Reused the successful native build and per-host verification rather than repackaging either host.

## Findings and disposition

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| C1 | Medium | Original scanner printed part of each matched credential in stdout and its report | Fixed: no matched text is emitted; location and SHA-256 fingerprint only |
| C2 | Medium | Binary content, reused-blob filename aliases and index/working-only changes could evade the original scan | Fixed and regression tested; coverage explicitly described |
| C3 | Medium / configuration gap | Weekly Dependabot config exists on `phase2`, not default `main`; therefore that version-update schedule is not active | Documented. `main` and default branch remain unchanged as requested |
| C4 | Low / documentation | README linked a missing upstream README; provenance claimed all Scripts/Tests unchanged despite documented changes | Fixed; upstream authorship and exact source reference retained |
| C5 | Medium / assurance gap | Earlier documentation overstated FFmpeg distribution compliance and log-redaction coverage | Corrected claims; exact corresponding-source/relink evidence and runtime logging coverage remain open |
| C6 | Residual supply chain | Installer/action pins are verified, but SDK/toolchain transitive downloads remain partly moving targets | Existing limitation retained; recording a version is not equivalent to pinning every download |
| C7 | Residual privacy | SponsorBlock/DeArrow video identifiers, pseudonymous preferences and in-memory host authorization are used by original features | Documented; native behavior preserved; redirects/session/logging require device testing |
| C8 | Default-branch limitation | Frozen `main` has the older tag-pinned workflow and lacks the new security tooling/config | Documented; repository SHA-pin policy may reject that old workflow. No claim that Phase 2 hardening is deployed to every branch |
| C9 | Dependency assurance | Dependabot alert counts do not cover every vendored native library/JavaScript component or establish FFmpeg CVE applicability | No vulnerability-free claim; manual component/configuration review and fuzzing remain outstanding |

No credential exposure was found by the current scan. This means no matching credential was detected in its stated coverage, not a proof that arbitrary secrets cannot exist. Source review of selected trust/storage/authorization boundaries is not a line-by-line audit of every upstream parser, and no exploitability claim is made without reproduction.

## GitHub Actions and repository review

On `phase2`, all three referenced actions use full commit SHAs; checkout does not persist credentials; workflow/job permissions are read-only; jobs have timeouts; no `pull_request_target` or privileged untrusted-checkout trigger is used; no user-supplied event field is interpolated into a shell script. The Theos installer is hash-checked before execution. Repository security state is recorded locally without secret or variable values.

Rulesets preventing force-push/deletion are different from requiring review or passing checks. Do not infer mandatory review from the presence of a ruleset. No destructive history operations, default-branch changes, merges or promotions were performed.

The scanner examines all **locally reachable refs**, including upstream remote refs. The upstream `gh-pages` history contains 22 open-source YTKACE DEB paths; these are artifact-policy observations, not credential findings or evidence of Google binaries in the published MarufYT branches. They were not deleted or newly pushed. Publication scope and upstream-ref scan scope are distinct.

## Requirements and release status

The existing `Documentation/REQUIREMENTS_CHECKLIST.md` remains the baseline for completed UI, localization, branding, dual-host packaging and feature-preservation work. Its runtime-dependent requirements remain **NOT TESTED**. The two host packages contain the original compiled Phase 2.1 changes, not this later scanner/documentation revision.

Keep `main` and `stable-21.39.4` at `aac6947f69446e649c66a2d4b0634d55a1600f06`. “Latest” means the newer supplied host, not an independently verified current App Store release. “Stable” denotes the preserved fallback build, not a new claim of tested iPhone stability.

All previous release/input files were snapshotted before the follow-up and compared afterward. Existing checksum manifests for MarufYT Phase 2 and Phase 2.1 are verified. One older, unrelated YouTube Plus extension CI checksum file uses its pre-download `output/` prefix after artifacts were flattened; its actual dylib digest is separately checked, and the historical manifest is not rewritten.

Physical iPhone launch, Google sign-in, account switching, UI layout, features, performance, signing and session continuity remain **NOT TESTED**. No Frida/device/network capture, parser fuzzing, new native compilation or new IPA build is claimed in this follow-up.

Local evidence and release handoff: `release/MarufYT-Phase2.1/Completion-Audit-2026-11-02/` and its `FINAL_COMPLETION_REPORT.md`. Earlier reports remain unchanged as historical evidence; this document qualifies their broader claims.

Primary references: [GitHub Actions security](https://docs.github.com/en/actions/reference/security/secure-use), [Dependabot default-branch requirement](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file), [FFmpeg security information](https://github.com/FFmpeg/web/blob/master/src/security), and [licence review](LICENSE_DISTRIBUTION_REVIEW.md).
