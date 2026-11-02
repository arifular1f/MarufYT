# MarufYT modules

## Branding (`Tweak/MarufYT/MarufYTBranding.*`)

The single source of the product identity. Dependencies: Foundation and UIKit (`openURL`).

- `MarufYTBrandedString()` replaces the upstream product name in user-facing text. `Localization.mm` applies it once per language load, so all 15 translations are rebranded without editing their keys.
- `MarufYTIsOwnAccessibilityText()` keeps the navigation-cleanup hooks from hiding MarufYT's own buttons under either name.

## Design system (`Tweak/MarufYT/MarufYTDesign.*`)

This module builds on YTKACE's native Liquid Glass implementation (`TabBarHooks.mm`, `GlassChrome.mm`, `GlassSheets.mm`, `PlayerGlass.mm`, `Notice.mm`). It does not create a second navigation layer, so hit-testing, the selection lens, scroll-to-minimize and safe-area geometry all stay upstream's.

- **Preset.** `MarufYTPreferenceDefaults()` turns these on by default when `UIGlassEffect` exists (iOS 26 and later): the tab bar, top-bar buttons, menus and sheets, toasts and popups, and player buttons. `registerDefaults` never overrides a value the user has set.
  - `MarufYTGlassPreferenceEnabled()` gives the same answer for the image constructor that removes `UIDesignRequiresCompatibility`. That constructor can run before defaults are registered.
- **Capsule depth.** `MarufYTDecorateTabCapsule()` puts a shadow-only view behind the floating glass capsule.
  - **Outside only:** an even-odd mask clips the shadow to the area outside the capsule, so the translucent glass is never darkened.
  - **Cheap:** it uses an explicit `shadowPath` (no offscreen shadow pass) and does no work when the frame and style haven't changed.
  - **No interference:** it's hidden in the minimized circle state, never receives touches, and is ignored by accessibility.
  - **Toggle:** *Liquid Glass → Floating Tab Bar Depth* (`YTKACE.Preference.Glass.DepthShadow`, on by default).

## Credits (`Tweak/MarufYT/MarufYTCreditsController.mm`)

An inset-grouped page with three sections:

- **MarufYT:** version, Developer (→ https://github.com/arifular1f) and Repository (→ https://github.com/arifular1f/MarufYT)
- **Built on:** YTKACE by itzzace, with a link
- **Third-party components:** each component, with its licence and a link

It is reached from MarufYT settings → About → Credits and from YouTube Settings → MarufYT → Credits.
