// MarufYT — settings design system: colour tokens, typography, metrics and
// control styling shared by every MarufYT settings screen.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// All colours are dynamic (light, dark, OLED black) and all fonts follow
// Dynamic Type. Controls are native UIKit; this module only styles them.

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

#pragma mark Colour tokens

// Restrained MarufYT accent for switches, sliders, steppers, checkmarks and
// the search caret. Never used for body text or values.
FOUNDATION_EXPORT UIColor *MarufYTAccentColor(void);
// Current values (picker selections, slider readouts, inputs).
FOUNDATION_EXPORT UIColor *MarufYTValueColor(void);
// Grouped page background and card (cell) surface; OLED-aware.
FOUNDATION_EXPORT UIColor *MarufYTPageBackgroundColor(void);
FOUNDATION_EXPORT UIColor *MarufYTCardBackgroundColor(void);
FOUNDATION_EXPORT UIColor *MarufYTSeparatorColor(void);

#pragma mark Typography (Dynamic Type)

FOUNDATION_EXPORT UIFont *MarufYTTitleFont(void);        // row titles (body)
FOUNDATION_EXPORT UIFont *MarufYTSubtitleFont(void);     // row descriptions (subheadline)
FOUNDATION_EXPORT UIFont *MarufYTValueFont(void);        // values (body)
FOUNDATION_EXPORT UIFont *MarufYTReadoutFont(void);      // numeric readouts (body, monospaced digits)
FOUNDATION_EXPORT UIFont *MarufYTFootnoteFont(void);     // section headers and notes

#pragma mark Metrics

FOUNDATION_EXPORT CGFloat const MarufYTCornerRadius;     // cards, notices
FOUNDATION_EXPORT CGFloat const MarufYTIconCornerRadius; // settings icons
// A native row height scaled for the current content size category.
FOUNDATION_EXPORT CGFloat MarufYTScaledHeight(CGFloat base);

#pragma mark Styling helpers

// Inset-grouped page appearance (background, separators, header spacing).
FOUNDATION_EXPORT void MarufYTStyleSettingsTable(UITableView *tableView);
// Resets a reused cell to the design-system defaults.
FOUNDATION_EXPORT void MarufYTStyleCell(UITableViewCell *cell);
FOUNDATION_EXPORT void MarufYTStyleSectionHeader(UIView *view);
FOUNDATION_EXPORT void MarufYTStyleSwitch(UISwitch *toggle);
FOUNDATION_EXPORT void MarufYTStyleSlider(UISlider *slider);
// Value text plus a small up/down chevron for menu-backed pickers.
FOUNDATION_EXPORT UIView *MarufYTMenuValueView(NSString *_Nullable text, CGFloat maxWidth);
// A rounded tile (white glyph on a tinted square) for settings row icons.
// Resolved for the current appearance and cached (bounded).
FOUNDATION_EXPORT UIImage *_Nullable MarufYTIconTile(NSString *symbol, UIColor *tint);
FOUNDATION_EXPORT UIImage *_Nullable MarufYTIconTileWithImage(UIImage *_Nullable glyph, NSString *cacheKey, UIColor *tint);
// Tile colour for a settings page identifier (stable, restrained palette).
FOUNDATION_EXPORT UIColor *MarufYTTintForPage(NSString *_Nullable pageID);

NS_ASSUME_NONNULL_END
