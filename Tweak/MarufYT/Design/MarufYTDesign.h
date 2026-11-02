// MarufYT — appearance defaults and the optional Liquid Glass capsule.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// Since Phase 3 the default look is simple and host-native: YouTube's classic
// docked tab bar, no glass presets, no depth layer. This module provides:
//   * the default preference values (stored user choices always win);
//   * the optional depth layer for the MarufYT Liquid Glass capsule, which is
//     off unless the user turns it on.

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

FOUNDATION_EXPORT NSString *const MarufYTDepthShadowKey;
FOUNDATION_EXPORT NSString *const MarufYTLightweightGlassKey;
// Keep native materials, but omit decorative lens tracking and depth effects.
FOUNDATION_EXPORT BOOL MarufYTLightweightGlassEnabled(void);

// Default values contributed by MarufYT. Merged into YTKACERegisterDefaults();
// registerDefaults never overrides a value the user has stored.
FOUNDATION_EXPORT NSDictionary<NSString *, id> *MarufYTPreferenceDefaults(void);

// Same answer as YTKACEFeatureEnabled() for a preset key, but usable from
// image constructors that may run before defaults are registered.
FOUNDATION_EXPORT BOOL MarufYTGlassPreferenceEnabled(NSString *key);

// Tab-bar mode used when the user has stored neither
// YTKACE.Preference.Tabs.GlassMode nor the legacy Tabs.Glass switch:
// 3, YouTube's classic docked bar.
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
