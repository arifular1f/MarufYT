# Disposition of prior audit findings

Reviewed 2026-11-02. Scope: continuing `phase2` from `dc7c458`; all existing release bytes and native implementations are preserved. “Implemented” is not a claim of iPhone execution.

| Prior ID | Confirmed disposition |
| --- | --- |
| M1: diagnostics location/protection | Original source fix retained. Static storage call/error-path review completed; effective backup/protection behaviour requires device testing |
| M2: log redaction | Original selected-format redaction retained. Earlier blanket “fixed” language qualified: JSON/cookie-header/identifier coverage remains open; synthetic Python model is not native execution |
| M3: CI supply chain | Full action pins/read-only token retained. Phase 2 now bypasses the moving installer/bootstrap path and locks source, submodules, compiler and SDK; default main workflow remains unchanged |
| L1: repository settings | Previously enabled security settings and deletion/non-fast-forward rules retained; no assumption of mandatory review or checks |
| L2: FFmpeg source hash | Strengthened: default digest authenticated with publisher signature/fingerprint; reused source trees rejected. No vendored libraries replaced |
| L3: accessibility identifiers | Completed Phase 2 source/binary changes retained; actual VoiceOver remains NOT TESTED |
| L4: transitive compiler/SDK | Moving release selectors removed from Phase 2 bootstrap. Versioned URLs, sizes and SHA-256s verified on every cache use; source gitlinks pinned. Hosted image/apt/runtime residuals explicitly recorded |
| L5: service identifiers | Existing video-ID disclosures retained and documented; no service protocol changes or privacy guarantee inferred |
| L6: pseudonymous SponsorBlock ID | Existing preference storage remains; no Google password/token is inferred from this ID. Runtime privacy review remains distinct |
| I1: TLS | No custom trust bypass found by source checks; absence of a literal cleartext endpoint does not prove all response-derived destinations or redirects |
| I2: host authorization | Fixed initial HTTPS destination and ephemeral/cookieless session confirmed in source; runtime redirects/session ownership remain NOT TESTED |
| I3: Keychain marker | Non-secret fixed marker path reviewed; Google sessions/signing effects NOT TESTED |
| I4: JavaScriptCore | Bare app-process context/no native bridge observed; not a separate sandbox or parser-security guarantee |
| I5: external lists | Existing list bounds/data processing preserved; upstream trust and service privacy remain dependencies |
| I6: ROOTLESS packaging | Existing per-host verification/checksum evidence reused; packages unchanged; no package installed |
| I7: permissions | Existing source request scope reviewed; effective signed entitlements and device prompts NOT TESTED |
| C1: scanner disclosure | Fixed in dc7c458; location/fingerprint reports, no matched-value excerpts. Regression tests retained |
| C2: scanner coverage | Fixed in dc7c458; reachable history, path aliases, staged/visible files and binary contents covered; shallow checkouts rejected. Ignored/unreachable material is not claimed scanned |
| C3: default-branch automation | Partially addressed within constraint: actual supported audit-only dispatch on phase2 and existing push/PR checks. Weekly Dependabot activation remains blocked by no-main-change instruction |
| C4: attribution/provenance documentation | Fixed in dc7c458; exact upstream README and copyright retained. No authorship/history rewritten |
| C5: source/relink and runtime assurance | Signed source, 131 normalized-header matches, configuration mapping and isolated relink evidence added. Static runtime review completed with explicit remaining gaps. No blanket compliance or runtime certification |
| C6: transitive dependency risk | Versioned compiler/SDK hashes and direct-source/gitlink bootstrap implemented. Runner image, signed host packages and first-download publisher trust residuals remain |
| C7: runtime privacy | Static review completed and model gaps documented; no native behaviour changed or real credential/service test performed |
| C8: frozen main configuration | Still intentionally unchanged. No claim of default-branch hardening or promotion; SHA-pin policy may reject old tags there |
| C9: dependency vulnerability assurance | Authentic source/configuration evidence strengthened. No comprehensive CVE reachability analysis, media/protocol fuzzing or vulnerability-free certification; library changes would require a separate versioned compatibility cycle |

The audit-only relink probe's first attempt failed with the Darwin-style archive editor. The corrected probe uses the LLVM archiver contained in the same locked compiler archive. Both run results are retained; only successful evidence is described as passing.

Detailed evidence: [toolchain](TRANSITIVE_TOOLCHAIN_LOCK.md), [automation](DEFAULT_BRANCH_AUTOMATION.md), [FFmpeg](FFMPEG_SOURCE_AND_RELINK.md), [static runtime review](RUNTIME_SECURITY_STATIC_REVIEW.md). All physical iPhone acceptance checks remain **NOT TESTED**.
