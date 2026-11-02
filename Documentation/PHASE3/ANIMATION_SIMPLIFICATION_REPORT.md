# Animation Simplification Report (Phase 3)

## Helper

`MarufYTAnimate(duration, animations, completion)` in `MarufYTDesign`: ease-out, begins from the current state, allows interaction. If **Reduce Motion** is on it applies the end state immediately. Durations: `MarufYTMotionQuick` 0.15 s (fades, highlights), `MarufYTMotionStandard` 0.2 s (small slides).

## Replaced

| Where | Before | After |
| --- | --- | --- |
| Downloads library long-press | scale to 0.94, then 0.6-damping spring, menu only after a 0.14 s delay | alpha highlight (0.15 s), menu opens immediately |
| Download progress card appear | 18 pt slide, spring 0.82 | 12 pt slide (none under Reduce Motion), 0.2 s ease-out |
| SponsorBlock banner | spring 0.75, 0.35 s | 0.2 s ease-out |
| Global mini player snap to corner | spring 0.82, 0.45 s | 0.2 s ease-out |

## Deliberately not changed (stated plainly)

- **Spring animations remain in the opt-in glass tab-bar code** (`TabBarHooks.mm`) and in the audio/download player screens (`YTKACEAudioPlayerController.mm`, `YTKACEDownloadPlayerController.mm`). The default tab bar (Simple) does not run them. Replacing them was out of scope for this build and is a candidate for a later change.
- The existing Reduce Motion / Reduce Transparency handling (`MarufYTLightweightGlassEnabled`) is unchanged: when either is on, lens tracking and depth effects stay off.
- No new animation, blur or rendering layer was added.

## Verification

Static check asserts the four files above contain no `usingSpringWithDamping` and use `MarufYTAnimate`. Perceived smoothness and button latency are **NOT TESTED**; no frame-rate numbers exist.
