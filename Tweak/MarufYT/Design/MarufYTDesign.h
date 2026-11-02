// MarufYT — Liquid Glass design system.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// Builds on YTKACE's native UIGlassEffect implementation (TabBarHooks.mm,
// GlassChrome.mm, GlassSheets.mm, PlayerGlass.mm) instead of adding a second
// navigation layer:
//   * a "premium" preset that turns the existing glass surfaces on by default
//     on iOS versions that provide UIGlassEffect (explicit user choices win);
//   * shared design tokens;
//   * a depth layer for the floating tab-bar capsule (outside-only shadow).

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

FOUNDATION_EXPORT NSString *const MarufYTDepthShadowKey;

// Preference defaults contributed by the design preset. Merged into
// YTKACERegisterDefaults(). Glass keys are only defaulted on when the
// system provides UIGlassEffect.
FOUNDATION_EXPORT NSDictionary<NSString *, id> *MarufYTPreferenceDefaults(void);

// Same answer as YTKACEFeatureEnabled() for a preset key, but usable from
// image constructors that may run before defaults are registered.
FOUNDATION_EXPORT BOOL MarufYTGlassPreferenceEnabled(NSString *key);

// Tab-bar glass mode used when the user has stored neither
// YTKACE.Preference.Tabs.GlassMode nor the legacy Tabs.Glass switch.
FOUNDATION_EXPORT NSInteger MarufYTPresetTabGlassMode(void);

// Design tokens.
FOUNDATION_EXPORT CGFloat const MarufYTCapsuleShadowRadius;
FOUNDATION_EXPORT CGFloat const MarufYTCapsuleShadowOffsetY;

// Depth layer for the floating tab-bar capsule. Call after the glass view
// has its final frame. Cheap when nothing changed.
FOUNDATION_EXPORT void MarufYTDecorateTabCapsule(UIView *bar, UIView *glass);
FOUNDATION_EXPORT void MarufYTRemoveTabCapsuleDecoration(UIView *bar);
FOUNDATION_EXPORT BOOL MarufYTIsDecorationView(UIView *view);

NS_ASSUME_NONNULL_END
