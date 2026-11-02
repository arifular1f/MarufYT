// MarufYT — project branding and identity.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// Single source of truth for the user-facing product identity. Internal
// identifiers (preference keys, accessibility identifiers, backup formats,
// notification names, storage folders) intentionally keep their upstream
// YTKACE names so existing settings, downloads and backups keep working.

#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

FOUNDATION_EXPORT NSString *const MarufYTProductName;
FOUNDATION_EXPORT NSString *const MarufYTDeveloperName;
FOUNDATION_EXPORT NSString *const MarufYTRepositoryURLString;
FOUNDATION_EXPORT NSString *const MarufYTRepositoryDisplay;
FOUNDATION_EXPORT NSString *const MarufYTDeveloperURLString;
FOUNDATION_EXPORT NSString *const MarufYTPackageDescription;
FOUNDATION_EXPORT NSString *const MarufYTUpstreamName;

// "1.1.4+marufyt.2" (from the package control file at build time).
FOUNDATION_EXPORT NSString *MarufYTVersionString(void);
// CI run number, or "local" for developer builds.
FOUNDATION_EXPORT NSString *MarufYTBuildNumber(void);
// Version of the YouTube app MarufYT is running in.
FOUNDATION_EXPORT NSString *MarufYTHostVersion(void);

// Replaces the upstream product name in user-facing text. Returns the input
// unchanged (same object) when there is nothing to replace.
FOUNDATION_EXPORT NSString *_Nullable MarufYTBrandedString(NSString *_Nullable text);

// YES for accessibility labels that mark this tweak's own views, under either
// the current or the upstream product name.
FOUNDATION_EXPORT BOOL MarufYTIsOwnAccessibilityText(NSString *_Nullable text);

FOUNDATION_EXPORT void MarufYTOpenURLString(NSString *string);

NS_ASSUME_NONNULL_END
