# UI Stability Report (Phase 3)

Branch `phase3-ui-stability`, package `1.1.4+marufyt.5`. Evidence: `SCREEN_RECORDING_AUDIT.md`.

**Status of every claim below: derived from the supplied recording and from reading source. Nothing here was observed on a device running the new build.**

## Root causes and what changed

| ID | Symptom you reported | Root cause found | Change | Evidence level |
| --- | --- | --- | --- | --- |
| P3-01 | Tab bar looked different and overlapped content | The MarufYT capsule was near-transparent (it hides YouTube's own blur) and floated over the feed | Default tab bar is now "Simple" (YouTube's classic docked bar). Capsule is opt-in | Recording + source |
| P3-02 | Whole app looked like a different design | Removing `UIDesignRequiresCompatibility` switches the app to the iOS 26 glass design; Phase 2 also defaulted four glass presets on | The key is only removed when the user stores a glass choice. Glass presets are no longer defaulted on | Source; see note below |
| P3-03 | MarufYT tab icon and label misaligned | Layout was anchored to native views MarufYT had already blanked, so each pass moved it | Layout is computed from the tab's own bounds plus a native sibling's measured geometry (pure function, tested) | Recording + source + unit tests |
| P3-04 | Labels differ between tabs on 21.43.5 | 21.43.5 adds `hideLabel` and an icon-only experiment; MarufYT forced its own label rule | MarufYT's label now follows the host and the user's setting | Source (static diff of hosts) |
| P3-05 | Too many effects, heavy animation | Springs, scale pulses, lens tracking, depth shadow | See `ANIMATION_SIMPLIFICATION_REPORT.md` | Source |
| P3-06 | Home shows a row of text tabs | YouTube's server-driven tabbed Home ("Fox") | "Normal Home Layout" default ON; see `HOME_LAYOUT_FIX_REPORT.md` | Recording + source |
| P3-07 | Capsule jumps during early layout | Height depended on the bottom safe-area inset, which is 0 early | Capsule geometry depends only on bar size and the host item height | Source + unit tests |

### New finding from the host audit (this stage)

The 21.43.5 `Info.plist` already contains `UIDesignRequiresCompatibility = true`; 21.39.4 has no such key. With the new defaults MarufYT leaves the key alone, so 21.43.5 stays in the host's compatibility look. Removal still happens only if the user picks a glass mode. How 21.39.4 renders without the key on iOS 27.2 is not known from static analysis and is **NOT TESTED**.

## Not resolved

- **Delayed layout shift on 21.43.5.** The recording does not show drift over time. The leading hypothesis is YouTube's remote cold-config flags arriving after launch. It was not reproduced and is not claimed fixed. The on-demand layout snapshot (long-press About → Version) exists so the next recording can capture the real values.
- Why the Subscriptions icon sits raised on 21.43.5.
- Feed-to-chip-row spacing (V-06).
- Whether the 21.43.5 install had `Tabs.LabelsHidden` stored.

## Verification actually performed

- `Tools/marufyt_checks.py`: 0 failures.
- `Tests/`: Python suite passes; native `test_layout_math` (14 tests) passes in CI.
- CI build on `ee3daa9`: tweak builds, 0 warnings (warnings are errors).
