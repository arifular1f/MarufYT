# MarufYT optimization release report

Status: **implementation, native build and static packaging verification complete;
physical acceptance remains open**. No measured speed, memory, FPS or battery
improvement is claimed. Exact visual correction on 21.43.5 is not yet verified.

Base phase2: `6d079b17cdd30685b5480a2e373c357356ed28ae`.
Dedicated branch: `optimization/phase2-performance`.
Native implementation commits: `4d3c6c1cc53d585e2be21d379fc709a2f15649bc`
and `2d5318a8a92879c51cf31b6b0094b0b492f15315`.
`main`, `phase2`, stable branch and default branch were not changed.

## Delivered changes

- Immediate selection at custom tab-drag release; native button tracking is
  cancelled when the custom drag takes ownership, replacing the 200 ms correction.
- Replacement tab icons/labels use converted host view anchors with a bounded
  intrinsic fallback. Capsule width/center use the host safe area rather than a
  full-screen short-side assumption. No new host-version-specific coordinate table.
- Opt-in persistent Lightweight Glass; normal material identity retained. Reduce
  Motion and Reduce Transparency use simpler accessible presentation paths.
- Transient lens work stops off-window/inactive and releases pending completion.
- DeArrow cache: 160 entries / 24 MiB decoded cost budget. Library metadata cache:
  64 entries / 32 MiB decoded cost budget, with queued operation cancellation at
  controller deallocation. These are advisory NSCache limits, not RAM ceilings.
- Existing download positioning timer is reused and tolerant; inactive layout is
  skipped. Playback/download work is retained.

Affected files and evidence are detailed in the companion audits. Changes are
targeted; Google authentication, licensing, network accuracy, download pipelines,
original host code sections, existing resource files and old releases are retained.

## Build and verification

[CI 41415092947](https://github.com/arifular1f/MarufYT/actions/runs/41415092947)
succeeded at `2d5318a`: 13 unit tests, 115 static checks, zero secret-scan findings,
90 native files compiled with no compiler warnings/errors. Toolchain inputs and
action SHAs remain pinned under the existing workflow. No default/main workflow
change or second native build was necessary. Both hosts independently assembled
and passed 40 structural checks each, plus 10 optimization artifact checks.
All 237 .3 compiled preferences remain, all other DEB payload files are identical,
18 protected IPA/DEB files and 240 old release files are unchanged.

New local output: `release/MarufYT-Optimization-1.1.4+marufyt.4/`.
Subdirectories: `Latest-YouTube-21.43.5/`, `Stable-YouTube-21.39.4/`,
`CI-Artifact/`, `Source/`, `Corresponding-Source/`, `Documentation/`.
Each host directory contains its IPA, DEB, dylib, assembly and verification reports,
toolchain provenance and SHA256 manifest. IPAs require local signing.

| Artifact | SHA256 |
| --- | --- |
| Latest 21.43.5 IPA | `18fd283abfbd69f23b908724da7b2e67bf5023c763232b544849a9c9cb1a1c69` |
| Stable 21.39.4 IPA | `ff73dba1d5199cc3c7bf0af692c637abc09820d31257d9184360277f796ceea0` |
| ROOTLESS .4 DEB (same compiled package in both folders) | `88c9c68e6bc2ce49ee646217aa6907785da9e50e597d9d0cda7b2968e296e64f` |

## Open acceptance items

No accessible screen recording or connected iPhone was available. The user
explicitly authorized the source audit to proceed without the video. Remaining:
frame-by-frame review; top logo/right controls and settings/About/library visual
verification; rapid tap/drag cancellation and duplicate action tests; accessibility
changes during gestures; foreground/background restoration; all feature runtime
regressions; display-size/Dynamic Type tests; Instruments allocations, Time
Profiler, Core Animation and Energy Log comparison. See PERFORMANCE_BEFORE_AFTER.md
for the measurement matrix and REGRESSION_TEST_RESULTS.md for individual features.

The static host audit still flags a differing page-style glass selector and newer
floating-bar renderer path. Existing method/type guards remain, but these cannot
prove pixel alignment or runtime fallback correctness. Repeated normal-mode
hierarchy traversal, concurrent SponsorBlock cold requests, AiSList failure retry,
download background timer wakeups and in-flight metadata operations remain
profiling candidates. New lightweight setting strings currently use English
fallback. Those limitations are retained explicitly rather than marked passed.

Rollback uses the preserved .3 host IPA after compatible signing; no previous
release has been overwritten and no history rewrite or promotion was performed.
