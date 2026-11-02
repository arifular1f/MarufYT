# Device Test Results (Phase 3)

**Every Phase 3 behaviour on a device is NOT TESTED.** No iPhone was available to this work, and the new builds have not been installed anywhere.

## What exists

| Source | What it is |
| --- | --- |
| Your screen recording `IMG_2949.MP4` + two screenshots | Observations of the **previous** build (`1.1.4+marufyt.4 (12)`) on iPhone 15 Pro Max, iOS 27.2: YouTube 21.39.4 and 21.43.5. Used only as the baseline in `SCREEN_RECORDING_AUDIT.md` |
| Automated tests | Static checks, Python tests, and native layout-math tests (CI). These do not exercise UIKit |
| CI build | The tweak compiles on ubuntu-24.04 with warnings as errors |

## Checklist for you

Mark each on the real device for **each** build (21.43.5 Latest, 21.39.4 Stable).

| # | Check | 21.43.5 | 21.39.4 |
| --- | --- | --- | --- |
| 1 | Fresh install: Tab Bar shows "Simple", Home shows normal feed + chips | NOT TESTED | NOT TESTED |
| 2 | Layout identical after 5 min, after background/foreground, after rotation | NOT TESTED | NOT TESTED |
| 3 | Bottom bar never covers video titles or metadata | NOT TESTED | NOT TESTED |
| 4 | MarufYT tab (Downloads) icon and label align with siblings | NOT TESTED | NOT TESTED |
| 5 | Google sign-in and account switching still work | NOT TESTED | NOT TESTED |
| 6 | Existing stored settings are kept after upgrade | NOT TESTED | NOT TESTED |
| 7 | Reduce Motion on: overlays appear without movement | NOT TESTED | NOT TESTED |
| 8 | Switching Tab Bar to YouTube / MarufYT works and switching back restores Simple | NOT TESTED | NOT TESTED |

## If the shift still happens

Long-press Settings → About → Version for 3 s. This writes a one-time layout snapshot (host version, safe area, relevant view frames, key preferences) into the diagnostics log, then opens it. Capture it right after launch and again when the layout has drifted; the difference shows what moved.
