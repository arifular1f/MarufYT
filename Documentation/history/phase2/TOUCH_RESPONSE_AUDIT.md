# Touch response audit

Scope: both YouTube hosts, optimization branch based on phase2 `6d079b1`.
Source implementation: `2d5318a` (includes `4d3c6c1`).

`TabBarHooks.mm` previously deferred selection by 200 ms when a drag began on
the current tab and retained its native button. This was a correction after native
touch handling, not a required authentication or playback dependency. The custom
drag now calls `cancelTrackingWithEvent:nil` on that button, clears its highlight,
and selects the target synchronously when the gesture ends. Lens settling remains
independent. Cancelled gestures still do not activate another tab.

Ordinary untouched native buttons retain their original action path. The custom
recognizer remains singular per bar, does not delay touch end, rejects scrubber
targets and rejects lightweight/accessibility mode. Decorations remain
noninteractive. No new recognizer, global debounce, main-queue sleep or preference
synchronize call was introduced. Zero-duration long press can still interact with
host recognizers: physical rapid-tap/drag/cancel tests remain mandatory.

Replacement tab icons now follow converted native image/label bounds rather than
fixed top/bottom offsets. This changes presentation only; the original native
control/hit-test machinery remains authoritative. Hit regions, overlap, double
activation and dragging from the selected tab are **NOT TESTED on a device**.

Source checks assert removal of delayed correction and retention of cancellation.
Native compilation and package checks are recorded in REGRESSION_TEST_RESULTS.md.
Actual touch-to-display latency before/after is NOT TESTED; removing a 200 ms
scheduled delay is not a claim that every tap becomes 200 ms faster.
