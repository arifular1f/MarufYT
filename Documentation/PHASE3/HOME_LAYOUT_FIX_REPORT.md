# Home Layout Fix Report (Phase 3)

## What YouTube is doing

The text-tab Home row in the recording is YouTube's server-driven "Fox" redesign. It is switched by `YTColdConfig` flags (for example `mainAppCoreClientIosEnableScrollableTabsInFox`) and acted on by `YTBrowseViewController` and `YTTabsViewController`. MarufYT already had a setting that overrides this: **Normal Home Layout** (`YTKACE.Preference.Feed.HomeTabsHidden`), implemented in `Features/Interface/HomeTabs.mm`.

## Change

- Default for that setting is now **ON** in both places a default is registered (`Runtime/Preferences.mm` and `MarufYTPreferenceDefaults()`).
- `registerDefaults` never overrides a stored value, so anyone who turned it off keeps it off. No stored preference is rewritten.
- The feed itself is not replaced, and no category list is hardcoded: chips come from YouTube.

## Limits

- Cold-config flags are read at launch, so a changed value needs an app restart. Because YouTube can deliver flags after launch, a Home change that appears later is possible; this is the unproven drift hypothesis.
- Top bar and chip rows are YouTube's own views. Phase 3 did not move them. The only MarufYT effect on them in the new default is none (glass presets are off).
- Spacing between the feed and the chip row (V-06 in the audit) is unexplained and unchanged.

## Verification

Static checks confirm both defaults and the unchanged persistence behaviour. Home appearance on 21.43.5 and 21.39.4 is **NOT TESTED** on a device.

## Revert

Settings → turn off "Normal Home Layout", then restart the app.
