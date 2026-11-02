# Requirements closure and remaining verification

Date: 2026-11-02. This supplements the existing consolidated `Documentation/REQUIREMENTS_CHECKLIST.md`; it does not replace its completed implementations or turn static evidence into runtime passes.

| Requirement group | Actual disposition |
| --- | --- |
| Preserve completed Phase 2 UI, pages, real preference bindings, accessibility and localization (A1–A5, A8–A13) | Existing code/resources and compiled `.3` packages preserved; 101 current source checks pass. Existing per-host binary checks retained. iPhone layout and functional behaviour NOT TESTED |
| Liquid Glass, feed/player audit and performance (A6–A7, A19–A20) | Existing implementation and documented scope retained; no new rendering/hooks/timers. Home/card restyling and device performance remain unverified; no visual/runtime claim is added |
| Newer supplied host, compatibility, fallback, distinct packages (A14–A18) | Both Phase 2 and Phase 2.1 Latest/Stable IPAs and DEBs retained; checksums verified. Existing `.3` reports: 40/40 checks per host. Labels do not certify App Store recency or on-device stability |
| No main promotion (A21 and current instructions) | `main`/`stable-21.39.4` remain at `aac6947f69446e649c66a2d4b0634d55a1600f06`; branch stays `phase2`; no history rewrite |
| Credential/source security (B1, B6) | Scanner strengthened with regression fixtures, current reachable-history/index/visible-tree scan clean; selected trust/storage/authorization boundaries reviewed. Logging formats, redirects and native parsers still lack dynamic/fuzz coverage |
| GitHub configuration and Actions (B2–B5) | Current settings read back; Phase 2 action pins, token permissions, checkout settings and installer digest checked. Frozen default-branch workflow remains older; weekly Dependabot config is not active there. Transitive toolchain pinning remains incomplete |
| Ownership, branding, licences (B7–B8) | Maintainer/upstream identity and MIT notices retained; missing upstream README restored from exact pinned source; source-provenance description corrected. FFmpeg exact corresponding-source and relink evidence remain open |
| Dual-host release and prior integrity (B9–B10) | Existing binary reports reused after byte-preservation/checksum verification; all prior release/input files kept. No unnecessary rebuild or overwrite |
| Final reports and documentation (B11) | Follow-up audit, licence review, requirements closure, local evidence and final release handoff added; prior reports/archives preserved |

## Required device gate

Application launch on each host, Google login/logout/session restoration, account switching, settings navigation/search, downloads, background audio/PiP, SponsorBlock, feed/Shorts/player/navigation changes, theme/Dynamic Type/VoiceOver and frame-rate/memory measurements remain **NOT TESTED**. Signing and host entitlements can affect sessions independently of source preservation. No current device or simulator execution is claimed.

## Open items requiring a different scope or evidence

1. Activating the prepared weekly Dependabot configuration and aligning the old default-branch workflow requires an explicitly authorized default-branch change; this follow-up deliberately does not make one.
2. FFmpeg distribution evidence needs authenticated corresponding-source provenance and a demonstrated modification/relink path for the exact shipped libraries. Updating to another library version would require a separate compatibility/build/test cycle and must not silently replace these releases.
3. Native logging-format/redirect/backup/session claims and parser security need focused runtime tests or fuzzing. Source assertions and zero GitHub alerts are not substitutes.

These limitations are recorded rather than silently changing requirements, rebuilding the application, or marking pending device acceptance complete.
