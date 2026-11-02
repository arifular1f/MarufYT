# Tab Bar Fix Report (Phase 3)

## Modes

Stored values are unchanged: `YTKACE.Preference.Tabs.GlassMode`.

| Value | Picker label | Meaning |
| --- | --- | --- |
| 3 | **Simple** (new default) | YouTube's classic docked tab bar, no MarufYT drawing |
| 0 | Default | The host's own bar for that version |
| 2 | YouTube | YouTube's native floating glass (21.43.5 has `YTFloatingPivotBarView`) |
| 1 | MarufYT | MarufYT Liquid Glass capsule |

Resolution order (tested function `MarufYTResolveTabMode`): stored value 0..3, then the legacy `Tabs.Glass` bool, then the unset default (3). Out-of-range stored values are ignored. Nothing is written to preferences.

## Overlap

In Simple mode MarufYT does not draw or reposition the bar, so the bar is the host's docked bar and the feed's bottom inset is the host's. The old overlap came from the floating capsule; it is not present in this mode. The capsule's height is now independent of the safe-area inset.

## Geometry (pure C, `MarufYTLayoutMath.h`)

- `MarufYTCapsuleFrame`: y=0, height = min(max(item,44)+14, barHeight), margins 14/21, width capped to `86*tabs+16` for 1–4 tabs. Example from the tests: 430×83 bar, 49 item, 5 tabs → {21, 0, 388, 63}.
- `MarufYTTabSlots` / `MarufYTTabItemFrame`: index-based slots that tile the capsule.
- `MarufYTReplacementTabLayout`: icon and label positions for MarufYT's own tab (Downloads/extra), derived from the tab's bounds and a native sibling's measured geometry; applying it twice gives the same result (fixed-point test).
- `MarufYTShouldHideReplacementLabel`: follows the user's label preference, the item's own hide flag, and what native siblings show.

No screen coordinates are hardcoded and no timer or poll repairs layout.

## Differences between hosts (static names)

| Only in 21.43.5 | Only in 21.39.4 |
| --- | --- |
| `YTFloatingPivotBarView`, `hideLabel`/`setHideLabel:`, icon-only pivot experiment, `YTFloatingPivotBarView setRenderer:` | `_enableFloatingBar`, `_floatingBarStyle`, `shouldPositionPivotBarAtBottom`, `YTPivotBarView liquidGlassEffectForPageStyle:` |

Missing classes and selectors are skipped at runtime, so no version-specific adapter was needed for the default mode. The two missing/gained targets affect only the opt-in glass modes.

## Verification

Native unit tests pass in CI (14 tests, `-Werror`). On-device appearance of every mode on both hosts is **NOT TESTED**.

## Revert

Settings → Tab Bar → choose "MarufYT" (previous Phase 2 look) or "Default".
