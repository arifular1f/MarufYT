// MarufYT — project branding.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// Single source of truth for user-facing product identity. Internal
// identifiers (preference keys, accessibility identifiers, backup formats,
// notification names) intentionally keep their upstream YTKACE names so
// existing settings and backups keep working.

#import <Foundation/Foundation.h>

@class UIViewController;

NS_ASSUME_NONNULL_BEGIN

FOUNDATION_EXPORT NSString *const MarufYTProductName;
FOUNDATION_EXPORT NSString *const MarufYTDeveloperName;
FOUNDATION_EXPORT NSString *const MarufYTRepositoryURLString;
FOUNDATION_EXPORT NSString *const MarufYTDeveloperURLString;
FOUNDATION_EXPORT NSString *const MarufYTUpstreamName;
FOUNDATION_EXPORT NSString *const MarufYTUpstreamAuthor;
FOUNDATION_EXPORT NSString *const MarufYTUpstreamURLString;

// Replaces the upstream product name in user-facing text. Returns the input
// unchanged (same object) when there is nothing to replace.
FOUNDATION_EXPORT NSString *_Nullable MarufYTBrandedString(NSString *_Nullable text);

// YES for accessibility labels/identifiers that mark this tweak's own views,
// under either the current or the upstream product name.
FOUNDATION_EXPORT BOOL MarufYTIsOwnAccessibilityText(NSString *_Nullable text);

FOUNDATION_EXPORT void MarufYTOpenURLString(NSString *string);

// Credits & licences page (MarufYTCreditsController.mm).
FOUNDATION_EXPORT UIViewController *MarufYTMakeCreditsController(void);

NS_ASSUME_NONNULL_END
