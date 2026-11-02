# MarufYT consolidated requirements checklist

**Covers all prompts:**

- MarufYT Premium (Phase 1)
- Phase 2 (UI, branding, YouTube migration)
- The two-IPA requirement
- Repository and security
- "Both workstreams mandatory"

**Status column ("before"):** the state found at the start of the security/completion pass (2026-11-02), compared with the repository at `phase2` @ `fafc680`. The final state is in the "Resolution" column.

**Status values:**
- **Implemented:** already in place.
- **Needs implementation:** missing.
- **Needs verification:** present, but needs re-checking (statically) in this pass.
- **N/A:** not applicable.

## Workstream A: MarufYT Phase 2

| # | Requirement | Before | Resolution |
| --- | --- | --- | --- |
| A1 | Design system: semantic colours, typography, spacing, radii, separators | Implemented (`MarufYTTheme`) | Re-verified (static checks) |
| A2 | Replace excessive red value text; restrained accent | Implemented | Guarded by a static check |
| A3 | Native UIKit controls bound to real preferences; no fake controls | Implemented | Preference-key regression re-run |
| A4 | Redesign all settings pages (main, Playback, Shorts, quality, Navigation/Top Bar, Liquid Glass, General/Other, Player, SponsorBlock, Downloads, Background Audio, Feed, Interface/Watch Page) | Implemented (all pages share the themed controller) | Re-verified |
| A5 | SponsorBlock and DeArrow redesign, keeping every category and setting | Implemented | Re-verified (key checks) |
| A6 | Liquid Glass preserved and improved (capsule, lens, depth, safe area, no duplicate bar) | Implemented (preset, depth, mode-1 suppresses YouTube's floating bar) | Device check pending |
| A7 | Home screen visual audit | Audited. YouTube's feed, cards and chips are server-driven (Elements/ComponentKit), so they are not restyled blind | Unchanged; documented as a limitation; existing Home & Feed / Top Bar options apply |
| A8 | Player UI audit; every button connected to its real implementation | **Needs implementation** (MarufYT player buttons announce raw internal IDs to VoiceOver; untranslated) | Localized, branded VoiceOver labels for all 9 overlay buttons |
| A9 | Complete MarufYT branding on every user-visible surface | Implemented | Re-verified |
| A10 | Remove the Credits row; keep attribution in the source distribution | Implemented | Re-verified |
| A11 | About: name, developer, version, YouTube version, build, ROOTLESS, repository | Implemented | Re-verified |
| A12 | Preserve all YTKACE features and settings | Implemented (baseline comparison with 1.1.4) | Re-run on the new build |
| A13 | **Maintain all 16 localizations** | **Needs implementation** (11 new labels English-only in 15 languages) | Translations added to all 16 tables; parity check added |
| A14 | Version discovery; supplied newer IPA identified | Implemented (21.43.5) | — |
| A15 | Host compatibility audit and report | Implemented | Re-run |
| A16 | Separate migration branch; old version still buildable | Implemented (`phase2`; `stable-21.39.4`) | — |
| A17 | Two separate ROOTLESS IPAs: 21.43.5 Latest and 21.39.4 Stable | Implemented (one folder) | Rebuilt as **separate** Latest and Stable packages |
| A18 | **Separate DEB packages, reports and SHA-256 per build** | **Needs implementation** (one shared DEB and report) | Each build folder has its own DEB (the same binary works for both hosts), verification report and SHA256SUMS |
| A19 | Performance: no swizzling, timers or extra rendering | Implemented | Re-verified |
| A20 | No dead code, debug hooks or temporary logging in MarufYT code | Implemented | Static check |
| A21 | Do not promote phase2 to main | Implemented | Kept |

## Workstream B: repository ownership and security

| # | Requirement | Before | Resolution |
| --- | --- | --- | --- |
| B1 | Secret audit of all branches and full history | Needs implementation | `Tools/marufyt_secret_scan.py` (positive-control tested); 0 findings; also runs in CI |
| B2 | GitHub configuration audit (secrets, keys, hooks, collaborators, settings) | Needs implementation | Done (read-only API audit) |
| B3 | Harden Actions: permissions, SHA-pinned actions, credential persistence, timeouts, concurrency | **Needs implementation** (tag-pinned actions, credentials persisted, no timeouts, all actions allowed) | Fixed |
| B4 | Dependency handling (Theos installer, FFmpeg, upstream) | **Needs implementation** (installer run from moving `master`) | Installer pinned to a commit and verified by SHA-256; Dependabot for actions; dependency report |
| B5 | Repo security features (Dependabot alerts, private vulnerability reporting, branch protection) | **Needs implementation** (off / none) | Enabled; rulesets block force-push and deletion |
| B6 | iOS review: ROOTLESS injection, file permissions, Keychain, network, TLS, storage, privacy | Needs implementation | Reviewed. Fixed: diagnostics log moved out of the Files-visible `Documents`, excluded from backup, file protection, redaction |
| B7 | Branding: description, topics, README, SECURITY.md, PRIVACY.md, issue templates | **Needs implementation** (upstream-branded issue templates, no SECURITY/PRIVACY) | Done |
| B8 | Preserve YTKACE MIT attribution and third-party licences; no falsified history | Implemented | Re-verified (no history rewrite) |
| B9 | Verify both Phase 2 IPAs | Needs verification | Done (new build) |
| B10 | Preserve features, sources and existing release artifacts | Needs verification | Checksums of all earlier releases verified unchanged |
| B11 | Security, repository, dependency and release audit reports | Needs implementation | `release/MarufYT-Phase2.1/Audit/` |

## Not possible in this environment

- **iPhone runtime testing:** no device is connected. Every device item stays NOT TESTED until you test it physically.
- **Visual restyling of YouTube's server-driven home feed and cards:** not attempted without a device to verify on (A7).
