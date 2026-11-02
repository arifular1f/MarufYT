# Animation optimization

Changed: TabBarHooks.mm and MarufYTDesign.h/.mm; glass accessibility guards in
GlassChrome.mm, GlassSheets.mm, PlayerGlass.mm and Notice.mm. Both hosts share
these paths; their actual native hierarchies can differ.

The opt-in **Lightweight Glass** setting under the glass settings page retains
the native capsule material and selection marker, replaces the private magnifying
lens with a reusable plain selection pill, omits the external depth shadow, and
rejects decorative custom slide gestures. Existing normal-glass preferences and
defaults are retained. It persists under `YTKACE.Preference.Glass.Lightweight`,
which participates in the existing preference export/import namespace. New label
and description use the existing localization fallback; translations for these
two new strings remain English until reviewed translations are available.

Reduce Motion selects this lighter tab treatment and bypasses custom UIKit and
Core Animation spring helpers. Reduce Transparency uses an opaque adaptive capsule
background and restores non-glass chrome/sheets/player/notice surfaces through
their existing fallback paths. Normal mode retains existing glass appearance.

The lens display-link tracker still has its original bounded animation deadline,
but now invalidates off-window/inactive and clears its pending lowering block.
Depth rendering was already rasterized with an explicit shadow path and a
geometry/style early return; this is reused, not rebuilt. Effects are recreated
on material-mode transitions, not every tab layout. No new continuous animation
loop or polling source was added.

Build/source verification cannot establish smoothness. ProMotion, frame pacing,
GPU/offscreen-render costs, rapid navigation, accessibility toggles during an
active gesture, foreground restoration and final visual polish are NOT TESTED.
Existing toasts and download-card animations were reviewed but not globally
disabled or rewritten. Animation coverage is targeted, not an assertion that all
host-owned animations obey custom settings.
