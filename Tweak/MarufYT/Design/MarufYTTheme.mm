// MarufYT — settings design system.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

#import "MarufYTTheme.h"
#import "../../Runtime/Preferences.h"

CGFloat const MarufYTCornerRadius = 12.0;
CGFloat const MarufYTIconCornerRadius = 7.0;

static UIColor *MarufYTDynamic(UIColor *(^provider)(UITraitCollection *traits)) {
    return [UIColor colorWithDynamicProvider:provider];
}

static BOOL MarufYTDark(UITraitCollection *traits) {
    UIUserInterfaceStyle style = traits.userInterfaceStyle;
    if (style == UIUserInterfaceStyleUnspecified) {
        style = UITraitCollection.currentTraitCollection.userInterfaceStyle;
    }
    return style == UIUserInterfaceStyleDark;
}

#pragma mark Colour tokens

UIColor *MarufYTAccentColor(void) {
    static UIColor *color;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        // Calm cobalt: #3563D9 light, #7C9CFF dark. Distinct from YouTube red.
        color = MarufYTDynamic(^UIColor *(UITraitCollection *traits) {
            return MarufYTDark(traits)
                ? [UIColor colorWithRed:0.486 green:0.612 blue:1.000 alpha:1.0]
                : [UIColor colorWithRed:0.208 green:0.388 blue:0.851 alpha:1.0];
        });
    });
    return color;
}

UIColor *MarufYTValueColor(void) {
    return UIColor.secondaryLabelColor;
}

UIColor *MarufYTPageBackgroundColor(void) {
    static UIColor *color;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        color = MarufYTDynamic(^UIColor *(UITraitCollection *traits) {
            if (YTKACEOLEDActive(traits)) return UIColor.blackColor;
            // Dark matches YouTube's own background; light is the iOS grouped grey.
            return MarufYTDark(traits) ? [UIColor colorWithWhite:0.075 alpha:1.0]
                                       : [UIColor colorWithRed:0.949 green:0.949 blue:0.969 alpha:1.0];
        });
    });
    return color;
}

UIColor *MarufYTCardBackgroundColor(void) {
    static UIColor *color;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        color = MarufYTDynamic(^UIColor *(UITraitCollection *traits) {
            if (YTKACEOLEDActive(traits)) return [UIColor colorWithWhite:0.07 alpha:1.0];
            return MarufYTDark(traits) ? [UIColor colorWithWhite:0.135 alpha:1.0] : UIColor.whiteColor;
        });
    });
    return color;
}

UIColor *MarufYTSeparatorColor(void) {
    return UIColor.separatorColor;
}

#pragma mark Typography

UIFont *MarufYTTitleFont(void) {
    return [UIFont preferredFontForTextStyle:UIFontTextStyleBody];
}

UIFont *MarufYTSubtitleFont(void) {
    return [UIFont preferredFontForTextStyle:UIFontTextStyleSubheadline];
}

UIFont *MarufYTValueFont(void) {
    return [UIFont preferredFontForTextStyle:UIFontTextStyleBody];
}

UIFont *MarufYTReadoutFont(void) {
    UIFont *body = [UIFont preferredFontForTextStyle:UIFontTextStyleBody];
    UIFont *digits = [UIFont monospacedDigitSystemFontOfSize:body.pointSize weight:UIFontWeightRegular];
    return [[UIFontMetrics metricsForTextStyle:UIFontTextStyleBody] scaledFontForFont:digits
                                                                  maximumPointSize:body.pointSize];
}

UIFont *MarufYTFootnoteFont(void) {
    return [UIFont preferredFontForTextStyle:UIFontTextStyleFootnote];
}

#pragma mark Metrics

CGFloat MarufYTScaledHeight(CGFloat base) {
    return ceil([UIFontMetrics.defaultMetrics scaledValueForValue:base]);
}

#pragma mark Styling helpers

void MarufYTStyleSettingsTable(UITableView *tableView) {
    tableView.backgroundColor = MarufYTPageBackgroundColor();
    tableView.separatorColor = MarufYTSeparatorColor();
    tableView.tintColor = MarufYTAccentColor();
    tableView.cellLayoutMarginsFollowReadableWidth = YES;
}

void MarufYTStyleCell(UITableViewCell *cell) {
    cell.backgroundColor = MarufYTCardBackgroundColor();
    cell.tintColor = MarufYTAccentColor();
    cell.textLabel.font = MarufYTTitleFont();
    cell.textLabel.textColor = UIColor.labelColor;
    cell.textLabel.adjustsFontForContentSizeCategory = YES;
    cell.detailTextLabel.font = MarufYTSubtitleFont();
    cell.detailTextLabel.textColor = UIColor.secondaryLabelColor;
    cell.detailTextLabel.adjustsFontForContentSizeCategory = YES;
}

void MarufYTStyleSectionHeader(UIView *view) {
    if (![view isKindOfClass:UITableViewHeaderFooterView.class]) return;
    UITableViewHeaderFooterView *header = (UITableViewHeaderFooterView *)view;
    header.textLabel.font = MarufYTFootnoteFont();
    header.textLabel.textColor = UIColor.secondaryLabelColor;
    header.textLabel.adjustsFontForContentSizeCategory = YES;
}

void MarufYTStyleSwitch(UISwitch *toggle) {
    toggle.onTintColor = MarufYTAccentColor();
    toggle.transform = CGAffineTransformIdentity;
}

void MarufYTStyleSlider(UISlider *slider) {
    slider.minimumTrackTintColor = MarufYTAccentColor();
    slider.maximumTrackTintColor = UIColor.tertiarySystemFillColor;
}

UIView *MarufYTMenuValueView(NSString *text, CGFloat maxWidth) {
    UILabel *label = [UILabel new];
    label.text = text;
    label.font = MarufYTValueFont();
    label.adjustsFontForContentSizeCategory = YES;
    label.textColor = MarufYTValueColor();
    label.lineBreakMode = NSLineBreakByTruncatingTail;
    UIImageSymbolConfiguration *glyph =
        [UIImageSymbolConfiguration configurationWithTextStyle:UIFontTextStyleFootnote
                                                         scale:UIImageSymbolScaleSmall];
    UIImageView *chevron = [[UIImageView alloc] initWithImage:
        [UIImage systemImageNamed:@"chevron.up.chevron.down" withConfiguration:glyph]];
    chevron.tintColor = UIColor.tertiaryLabelColor;
    chevron.contentMode = UIViewContentModeCenter;
    [label sizeToFit];
    [chevron sizeToFit];
    CGFloat spacing = 5.0;
    CGFloat labelWidth = MIN(CGRectGetWidth(label.bounds), MAX(0.0, maxWidth - CGRectGetWidth(chevron.bounds) - spacing));
    CGFloat height = MAX(CGRectGetHeight(label.bounds), CGRectGetHeight(chevron.bounds));
    UIView *container = [[UIView alloc] initWithFrame:
        CGRectMake(0.0, 0.0, labelWidth + spacing + CGRectGetWidth(chevron.bounds), height)];
    label.frame = CGRectMake(0.0, (height - CGRectGetHeight(label.bounds)) * 0.5, labelWidth, CGRectGetHeight(label.bounds));
    chevron.frame = CGRectMake(labelWidth + spacing, (height - CGRectGetHeight(chevron.bounds)) * 0.5,
                               CGRectGetWidth(chevron.bounds), CGRectGetHeight(chevron.bounds));
    [container addSubview:label];
    [container addSubview:chevron];
    container.isAccessibilityElement = YES;
    container.accessibilityLabel = text;
    return container;
}

UIImage *MarufYTIconTile(NSString *symbol, UIColor *tint) {
    UIImageSymbolConfiguration *configuration =
        [UIImageSymbolConfiguration configurationWithPointSize:15.0 weight:UIImageSymbolWeightSemibold];
    return MarufYTIconTileWithImage([UIImage systemImageNamed:symbol withConfiguration:configuration],
                                    symbol, tint);
}

UIImage *MarufYTIconTileWithImage(UIImage *glyph, NSString *cacheKey, UIColor *tint) {
    if (glyph == nil) return nil;
    static NSCache<NSString *, UIImage *> *cache;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        cache = [NSCache new];
        cache.countLimit = 64;
    });
    CGFloat side = 29.0;
    // Tiles are resolved per appearance so cached images stay correct in both modes.
    UIColor *resolved = [tint resolvedColorWithTraitCollection:UITraitCollection.currentTraitCollection];
    CGFloat r = 0, g = 0, b = 0, a = 0;
    [resolved getRed:&r green:&g blue:&b alpha:&a];
    NSString *key = [NSString stringWithFormat:@"%@|%.3f|%.3f|%.3f", cacheKey, r, g, b];
    UIImage *cached = [cache objectForKey:key];
    if (cached != nil) return cached;
    UIImage *white = [glyph imageWithTintColor:UIColor.whiteColor renderingMode:UIImageRenderingModeAlwaysOriginal];
    // Fit custom (asset) glyphs into the same 17 pt box as SF Symbols.
    CGSize size = white.size;
    CGFloat box = 17.0;
    CGFloat scale = MIN(1.0, MIN(box / MAX(size.width, 1.0), box / MAX(size.height, 1.0)));
    size = CGSizeMake(size.width * scale, size.height * scale);
    UIGraphicsImageRenderer *renderer =
        [[UIGraphicsImageRenderer alloc] initWithSize:CGSizeMake(side, side)];
    UIImage *tile = [renderer imageWithActions:^(__unused UIGraphicsImageRendererContext *context) {
        [resolved setFill];
        [[UIBezierPath bezierPathWithRoundedRect:CGRectMake(0, 0, side, side)
                                    cornerRadius:MarufYTIconCornerRadius] fill];
        [white drawInRect:CGRectMake((side - size.width) * 0.5, (side - size.height) * 0.5,
                                     size.width, size.height)];
    }];
    tile = [tile imageWithRenderingMode:UIImageRenderingModeAlwaysOriginal];
    [cache setObject:tile forKey:key];
    return tile;
}

UIColor *MarufYTTintForPage(NSString *pageID) {
    static NSDictionary<NSString *, UIColor *> *palette;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        palette = @{
            @"player": UIColor.systemIndigoColor,
            @"quality": UIColor.systemBlueColor,
            @"captions": UIColor.systemTealColor,
            @"gestures": UIColor.systemPurpleColor,
            @"sponsorblock": UIColor.systemGreenColor,
            @"watch": UIColor.systemOrangeColor,
            @"feed": UIColor.systemBlueColor,
            @"shorts": UIColor.systemPinkColor,
            @"tabs": UIColor.systemGrayColor,
            @"topbar": UIColor.systemGrayColor,
            @"glass": UIColor.systemCyanColor,
            @"downloads": MarufYTAccentColor(),
            @"general": UIColor.systemGrayColor
        };
    });
    return (pageID.length != 0 ? palette[pageID] : nil) ?: MarufYTAccentColor();
}
