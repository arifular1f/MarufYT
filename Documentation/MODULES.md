# MarufYT modules (`Tweak/MarufYT/`)

## Branding (`Branding/MarufYTBranding.*`)

The single source of the product identity:

- `MarufYTProductName`, `MarufYTDeveloperName`
- repository and profile URLs; `MarufYTRepositoryDisplay`
- `MarufYTPackageDescription`
- `MarufYTVersionString()`, from the control file at build time
- `MarufYTBuildNumber()`, the CI run number via `MARUFYT_BUILD`
- `MarufYTHostVersion()`

How branding is applied:

- **Localization:** `MarufYTBrandedString()` rebrands localized values once per language load, so all 15 translations change without editing their keys.
- **Own-view detection:** `MarufYTIsOwnAccessibilityText()` keeps the navigation-cleanup hooks from hiding MarufYT's own buttons under either name.

## Design (`Design/`)

### `MarufYTTheme.*`: the settings design system

| Token or helper | Value |
| --- | --- |
| Accent | Cobalt #3563D9 / #7C9CFF. Used only for switches, sliders, steppers, checkmarks and the caret. `YTKACEAccentColor()` returns it |
| Values | `secondaryLabelColor` |
| Page / card | Grouped grey #F2F2F7 / white (light); 0.075 / 0.135 (dark, matching YouTube); black / 0.07 (OLED) |
| Typography | Dynamic Type: body (titles and values), subheadline (descriptions), footnote (headers and notes), monospaced-digit body (readouts) |
| Metrics | 12 pt card radius, 7 pt icon radius; `MarufYTScaledHeight()` scales fixed rows with the content size |
| Helpers | `MarufYTStyleSettingsTable`, `MarufYTStyleCell`, `MarufYTStyleSectionHeader`, `MarufYTStyleSwitch`, `MarufYTStyleSlider`, `MarufYTMenuValueView` (value + up/down chevron), `MarufYTIconTile` / `MarufYTIconTileWithImage` (cached; at most 64 tiles), `MarufYTTintForPage` |

### `MarufYTDesign.*`: the Liquid Glass preset and capsule depth

Optimization .4 adds `MarufYTLightweightGlassEnabled()` and the persistent
`YTKACE.Preference.Glass.Lightweight` setting. It follows Reduce Motion and Reduce
Transparency, suppresses optional capsule depth and selects the simpler tab pill.
Normal glass defaults remain unchanged. See FINAL_OPTIMIZATION_REPORT.md.

- **Preset:** top bar, menus, toasts and player glass default to on when `UIGlassEffect` exists.
- **Tab bar mode:** `MarufYTPresetTabGlassMode()` (the floating capsule) is used only when you have stored neither `Tabs.GlassMode` nor the legacy `Tabs.Glass` switch.
- **Depth layer:** `MarufYTDecorateTabCapsule()` adds a shadow that is masked to outside the capsule and rasterized. Toggle: `YTKACE.Preference.Glass.DepthShadow`.

## Where the modules are used

All upstream changes are listed in `SOURCE_PROVENANCE.md`.

- **Settings screens:** root, pages, tab editor and search.
- **Runtime:** localization, preference defaults, the tab bar and navigation visibility.
