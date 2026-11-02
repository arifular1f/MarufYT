#!/usr/bin/env python3
"""One-off: re-apply MarufYT branding and apply the Phase 2 design system on top
of upstream YTKACE main. Every anchor must match exactly once or nothing is
written. Kept in the repository as a record of the exact transformation.

Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
pending = {}


def edit(path, pairs, imports=()):
    p = ROOT / path
    s = pending.get(p) or p.read_text(encoding='utf-8')
    for old, new in pairs:
        n = s.count(old)
        if n != 1:
            sys.exit(f'{path}: anchor found {n}x: {old[:90]!r}')
        s = s.replace(old, new)
    for line in imports:
        if line in s:
            continue
        i = s.index('\n#import <')
        s = s[:i] + '\n' + line + s[i:]
    pending[p] = s


B = '#import "../MarufYT/Branding/MarufYTBranding.h"'
T = '#import "../MarufYT/Design/MarufYTTheme.h"'
B2 = '#import "../../MarufYT/Branding/MarufYTBranding.h"'
D2 = '#import "../../MarufYT/Design/MarufYTDesign.h"'

# ---------------------------------------------------------------- runtime ----
edit('Tweak/Runtime/Localization.mm', [
    ('    return [NSDictionary dictionaryWithContentsOfFile:path];\n}',
     '    NSDictionary<NSString *, NSString *> *strings = [NSDictionary dictionaryWithContentsOfFile:path];\n'
     '    if (strings == nil) return nil;\n'
     '    // MarufYT: rebrand values once per language load; keys stay upstream.\n'
     '    NSMutableDictionary<NSString *, NSString *> *branded =\n'
     '        [NSMutableDictionary dictionaryWithCapacity:strings.count];\n'
     '    [strings enumerateKeysAndObjectsUsingBlock:^(NSString *key, NSString *value, __unused BOOL *stop) {\n'
     '        branded[key] = [value isKindOfClass:NSString.class] ? MarufYTBrandedString(value) : value;\n'
     '    }];\n'
     '    return branded;\n}'),
    ('    return value.length != 0 ? value : key;', '    return value.length != 0 ? value : MarufYTBrandedString(key);'),
], ['#import "../MarufYT/Branding/MarufYTBranding.h"'])

edit('Tweak/Runtime/Preferences.mm', [
    ('        @"YTKACE.Preference.Tabs.Order": ',
     '        @"YTKACE.Preference.Tabs.Order": '),
], ['#import "../MarufYT/Design/MarufYTDesign.h"'])
prefs = pending[ROOT / 'Tweak/Runtime/Preferences.mm']
start = prefs.index('        @"YTKACE.Preference.Tabs.Order": ')
end = prefs.index('    }];', start) + len('    }];')
pending[ROOT / 'Tweak/Runtime/Preferences.mm'] = (
    prefs[:end] + '\n    // MarufYT design preset (Liquid Glass on by default where supported).\n'
    '    // registerDefaults never overrides a value the user has set.\n'
    '    [YTKACEDefaults() registerDefaults:MarufYTPreferenceDefaults()];' + prefs[end:])

edit('Tweak/UI/Assets.mm', [
    ('UIColor *YTKACEAccentColor(void) {\n    return [UIColor colorWithRed:0.749 green:0.0 blue:0.075 alpha:1.0];',
     'UIColor *YTKACEAccentColor(void) {\n    // MarufYT: restrained accent instead of YouTube red (see MarufYTTheme).\n'
     '    return MarufYTAccentColor();'),
], ['#import "../MarufYT/Design/MarufYTTheme.h"'])

# ------------------------------------------------------------- navigation ----
edit('Tweak/Features/Navigation/TabBarHooks.mm', [
    ('            YTKACEPivotIdentifier,\n            @"YTKACE",', '            YTKACEPivotIdentifier,\n            MarufYTProductName,'),
    ('        formattedSelector,\n        @"YTKACE"\n    );', '        formattedSelector,\n        MarufYTProductName\n    );'),
    ('    BOOL exactLabel = [text caseInsensitiveCompare:@"YTKACE"] == NSOrderedSame;',
     '    BOOL exactLabel = [text caseInsensitiveCompare:MarufYTProductName] == NSOrderedSame ||\n'
     '        [text caseInsensitiveCompare:MarufYTUpstreamName] == NSOrderedSame;'),
    ('        label.text = @"YTKACE";', '        label.text = MarufYTProductName;'),
    ('    if ([value respondsToSelector:@selector(integerValue)]) return [value integerValue];\n'
     '    return [defaults boolForKey:@"YTKACE.Preference.Tabs.Glass"] ? 1 : 0;',
     '    if ([value respondsToSelector:@selector(integerValue)]) return [value integerValue];\n'
     '    id legacy = [defaults objectForKey:@"YTKACE.Preference.Tabs.Glass"];\n'
     '    if (legacy != nil) return [legacy boolValue] ? 1 : 0;\n'
     '    // MarufYT: no stored choice, use the design preset.\n'
     '    return MarufYTPresetTabGlassMode();'),
    ('        if ([defaults boolForKey:key]) any = YES;',
     '        // MarufYT: may run before defaults are registered, so apply the preset here too.\n'
     '        if (MarufYTGlassPreferenceEnabled(key)) any = YES;'),
    ('        if (sibling == glass || sibling == ownPill || sibling == ownLens) continue;',
     '        if (sibling == glass || sibling == ownPill || sibling == ownLens ||\n'
     '            MarufYTIsDecorationView(sibling)) continue;'),
    ('    glass.alpha = 1.0;\n', '    glass.alpha = 1.0;\n    MarufYTDecorateTabCapsule(receiver, glass);\n'),
], [B2, D2])
tab = pending[ROOT / 'Tweak/Features/Navigation/TabBarHooks.mm']
# Remove the depth layer wherever upstream tears the glass down.
marker = '            blur.hidden = NO;\n'
count = tab.count(marker)
if count < 1:
    sys.exit('TabBarHooks: glass teardown not found')
tab = tab.replace(marker, '            MarufYTRemoveTabCapsuleDecoration(receiver);\n' + marker)
pending[ROOT / 'Tweak/Features/Navigation/TabBarHooks.mm'] = tab
# "defaults" is now only used through the helper in the glass constructor.
if 'NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;\n    BOOL any = ' in tab:
    pending[ROOT / 'Tweak/Features/Navigation/TabBarHooks.mm'] = tab.replace(
        '    NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;\n    BOOL any = ', '    BOOL any = ')

edit('Tweak/Features/Interface/NavigationVisibility.mm', [
    ('        [view.accessibilityLabel hasPrefix:@"YTKACE"] ||',
     '        MarufYTIsOwnAccessibilityText(view.accessibilityLabel) ||'),
], [B2])

# ---------------------------------------------------- branded dialogs/labels --
edit('Tweak/Settings/SettingsEntry.mm', [
    ('    button.accessibilityLabel = @"YTKACE Settings";',
     '    button.accessibilityLabel = MarufYTBrandedString(@"YTKACE Settings");'),
], [B])
edit('Tweak/Features/Downloads/DownloadCoordinator.mm', [
    ('[self showAlertWithTitle:@"YTKACE" message:YTKACELocalized(@"No active video was found.")]',
     '[self showAlertWithTitle:MarufYTProductName message:YTKACELocalized(@"No active video was found.")]'),
    ('[self showAlertWithTitle:@"YTKACE" message:YTKACELocalized(@"No active Short was found.")]',
     '[self showAlertWithTitle:MarufYTProductName message:YTKACELocalized(@"No active Short was found.")]'),
], [B2])
edit('Tweak/Features/Onboarding/FirstLaunch.mm', [
    ('    if (YTKACEShowYouTubeDialog(\n        @"YTKACE",', '    if (YTKACEShowYouTubeDialog(\n        MarufYTProductName,'),
], [B2])
edit('Tweak/Features/Interface/AiSListReport.mm', [
    ('[request setValue:@"YTKACE" forHTTPHeaderField:@"User-Agent"];',
     '[request setValue:MarufYTProductName forHTTPHeaderField:@"User-Agent"];'),
    ('    if (name.length == 0) name = @"YTKACE";', '    if (name.length == 0) name = MarufYTProductName;'),
], [B2])
edit('Tweak/Settings/YTKACEDownloadsController.mm', [
    ('    self.libraryTitleLabel.text = @"YTKACE";', '    self.libraryTitleLabel.text = MarufYTProductName;'),
], [B])

# ------------------------------------------------------------ tab editor ----
edit('Tweak/Settings/YTKACETabEditorController.mm', [
    ('[self tab:@"ytkace" title:@"YTKACE" symbol:', '[self tab:@"ytkace" title:MarufYTProductName symbol:'),
    ('    return [super initWithStyle:UITableViewStylePlain];', '    return [super initWithStyle:UITableViewStyleInsetGrouped];'),
    ('    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;\n    self.tableView.rowHeight = 48.0;\n'
     '    if (@available(iOS 15.0, *)) {\n        self.tableView.sectionHeaderTopPadding = 0.0;\n    }\n',
     '    self.tableView.rowHeight = UITableViewAutomaticDimension;\n    self.tableView.estimatedRowHeight = 48.0;\n'
     '    MarufYTStyleSettingsTable(self.tableView);\n'),
    ('    self.tableView.backgroundColor =\n        YTKACEInterfaceBackgroundColor(self.traitCollection);',
     '    self.tableView.backgroundColor = MarufYTPageBackgroundColor();'),
    ('    header.textLabel.font = [UIFont systemFontOfSize:11.0];\n    header.textLabel.textColor = UIColor.secondaryLabelColor;',
     '    MarufYTStyleSectionHeader(header);'),
    ('    cell.textLabel.font = [UIFont systemFontOfSize:17.0];\n    cell.backgroundColor = YTKACEInterfaceBackgroundColor(self.traitCollection);',
     '    MarufYTStyleCell(cell);'),
    ('        cell.detailTextLabel.text = YTKACETintTitles()[YTKACETintIndex()];\n        cell.detailTextLabel.textColor = YTKACEAccentColor();',
     '        cell.detailTextLabel.text = YTKACETintTitles()[YTKACETintIndex()];\n        cell.detailTextLabel.textColor = MarufYTValueColor();'),
    ('        cell.detailTextLabel.text = YTKACEFrostedTitles()[(NSUInteger)YTKACEFrostedTabBarMode()];\n        cell.detailTextLabel.textColor = YTKACEAccentColor();',
     '        cell.detailTextLabel.text = YTKACEFrostedTitles()[(NSUInteger)YTKACEFrostedTabBarMode()];\n        cell.detailTextLabel.textColor = MarufYTValueColor();'),
    ('            @"YTKACE.Preference.Tabs.Startup", startupTitles, startupValues, 0);\n        cell.detailTextLabel.textColor = YTKACEAccentColor();',
     '            @"YTKACE.Preference.Tabs.Startup", startupTitles, startupValues, 0);\n        cell.detailTextLabel.textColor = MarufYTValueColor();'),
    ('        toggle.transform = CGAffineTransformMakeScale(0.95, 0.95);\n        toggle.onTintColor = YTKACEAccentColor();',
     '        MarufYTStyleSwitch(toggle);'),
], [B, T])

# ------------------------------------------------------- settings pages ----
edit('Tweak/Settings/YTKACESettingsPages.mm', [
    # Surfaces
    ('static UIColor *YTKACESettingsBackground(void) {\n    return [UIColor colorWithDynamicProvider:^UIColor *(UITraitCollection *traits) {\n'
     '        return YTKACEInterfaceBackgroundColor(traits);\n    }];\n}',
     'static UIColor *YTKACESettingsBackground(void) {\n    return MarufYTPageBackgroundColor();\n}'),
    ('static UIColor *YTKACESettingsCellBackground(void) {\n    return [UIColor colorWithDynamicProvider:^UIColor *(UITraitCollection *traits) {\n'
     '        return YTKACEInterfaceBackgroundColor(traits);\n    }];\n}',
     'static UIColor *YTKACESettingsCellBackground(void) {\n    return MarufYTCardBackgroundColor();\n}'),
    # Restart notice
    ('    notice.backgroundColor = [UIColor colorWithWhite:0.72 alpha:0.96];\n    notice.layer.cornerRadius = 8.0;',
     '    notice.backgroundColor = UIColor.secondarySystemBackgroundColor;\n    notice.layer.cornerRadius = MarufYTCornerRadius;'),
    ('    label.text = YTKACELocalized(@"Your changes take effect once YouTube restarts.");\n    label.textColor = UIColor.labelColor;\n'
     '    label.font = [UIFont systemFontOfSize:13.0];',
     '    label.text = YTKACELocalized(@"Your changes take effect once YouTube restarts.");\n    label.textColor = UIColor.labelColor;\n'
     '    label.font = MarufYTFootnoteFont();\n    label.adjustsFontForContentSizeCategory = YES;'),
    # Picker list controller
    ('                  defaultIndex:(NSUInteger)defaultIndex {\n    self = [super initWithStyle:UITableViewStylePlain];',
     '                  defaultIndex:(NSUInteger)defaultIndex {\n    self = [super initWithStyle:UITableViewStyleInsetGrouped];'),
    ('    cell.textLabel.text = _titles[(NSUInteger)indexPath.row];\n    cell.textLabel.font = [UIFont systemFontOfSize:17.0];\n'
     '    cell.textLabel.textColor = UIColor.labelColor;\n    cell.backgroundColor = YTKACESettingsCellBackground();',
     '    MarufYTStyleCell(cell);\n    cell.textLabel.text = _titles[(NSUInteger)indexPath.row];'),
    # Options controller
    ('                sectionTitles:(NSArray<NSString *> *)sectionTitles {\n    self = [super initWithStyle:UITableViewStylePlain];',
     '                sectionTitles:(NSArray<NSString *> *)sectionTitles {\n    self = [super initWithStyle:UITableViewStyleInsetGrouped];'),
    ('    self.tableView.cellLayoutMarginsFollowReadableWidth = NO;\n    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;\n'
     '    self.tableView.rowHeight = 50.0;\n    if (@available(iOS 15.0, *)) {\n        self.tableView.sectionHeaderTopPadding = 0.0;\n    }\n}',
     '    self.tableView.estimatedRowHeight = 52.0;\n    MarufYTStyleSettingsTable(self.tableView);\n}'),
    ('    return title.length == 0 ? 18.0 : 38.0;', '    return title.length == 0 ? 12.0 : UITableViewAutomaticDimension;'),
    ('    if ([type isEqualToString:@"text"]) {\n        return 92.0;\n    }\n    if ([type isEqualToString:@"slider"]) {\n'
     '        return [item[@"stacked"] boolValue] ? 78.0 : 58.0;\n    }\n'
     '    if ([type isEqualToString:@"segmented"] && [item[@"stacked"] boolValue]) {\n        return 74.0;\n    }\n'
     '    return [item[@"subtitle"] length] == 0 ? 40.0 : 56.0;',
     '    // Fixed-layout rows scale with Dynamic Type; standard rows self-size.\n'
     '    if ([type isEqualToString:@"slider"]) {\n'
     '        return MarufYTScaledHeight([item[@"stacked"] boolValue] ? 92.0 : 60.0);\n    }\n'
     '    if ([type isEqualToString:@"segmented"] && [item[@"stacked"] boolValue]) {\n'
     '        return MarufYTScaledHeight(84.0);\n    }\n'
     '    return UITableViewAutomaticDimension;'),
    ('        UITableViewHeaderFooterView *header = (UITableViewHeaderFooterView *)view;\n'
     '        header.textLabel.font = [UIFont systemFontOfSize:11.0 weight:UIFontWeightRegular];\n'
     '        header.textLabel.textColor = UIColor.secondaryLabelColor;',
     '        MarufYTStyleSectionHeader(view);'),
    ('    cell.textLabel.text = item[@"title"];\n    cell.detailTextLabel.text = item[@"subtitle"];\n'
     '    cell.textLabel.font = [UIFont systemFontOfSize:17.0];\n    cell.detailTextLabel.font = [UIFont systemFontOfSize:12.0];\n'
     '    cell.textLabel.numberOfLines = 1;\n    cell.detailTextLabel.numberOfLines = 2;\n'
     '    cell.textLabel.textColor = UIColor.labelColor;\n    cell.detailTextLabel.textColor = UIColor.secondaryLabelColor;\n'
     '    cell.backgroundColor = YTKACESettingsCellBackground();',
     '    MarufYTStyleCell(cell);\n    cell.textLabel.text = item[@"title"];\n    cell.detailTextLabel.text = item[@"subtitle"];\n'
     '    cell.textLabel.numberOfLines = 0;\n    cell.detailTextLabel.numberOfLines = 0;'),
    ('    cell.accessoryView = nil;\n    cell.imageView.image = nil;\n\n    if ([type isEqualToString:@"toggle"]) {',
     '    cell.accessoryView = nil;\n    cell.imageView.image = YTKACEItemDotImage(item);\n\n    if ([type isEqualToString:@"toggle"]) {'),
    ('        toggle.transform = CGAffineTransformMakeScale(0.95, 0.95);\n        toggle.onTintColor = YTKACEAccentColor();',
     '        MarufYTStyleSwitch(toggle);'),
    ('            caption.text = item[@"title"];\n            caption.font = [UIFont systemFontOfSize:16.0];',
     '            caption.text = item[@"title"];\n            caption.font = MarufYTTitleFont();\n            caption.adjustsFontForContentSizeCategory = YES;'),
    ('        caption.text = item[@"title"];\n        caption.font = [UIFont systemFontOfSize:16.0];',
     '        caption.text = item[@"title"];\n        caption.font = MarufYTTitleFont();\n        caption.adjustsFontForContentSizeCategory = YES;'),
    ('        readout.font = [UIFont monospacedDigitSystemFontOfSize:15.0\n                                                        weight:UIFontWeightSemibold];\n'
     '        readout.textColor = YTKACEAccentColor();',
     '        readout.font = MarufYTReadoutFont();\n        readout.textColor = MarufYTValueColor();'),
    ('        UISlider *slider = [UISlider new];\n        slider.minimumTrackTintColor = YTKACEAccentColor();',
     '        UISlider *slider = [UISlider new];\n        MarufYTStyleSlider(slider);'),
    ('        UISlider *slider = [[UISlider alloc] initWithFrame:CGRectMake(0.0, 0.0, 158.0, 30.0)];\n'
     '        slider.minimumTrackTintColor = YTKACEAccentColor();',
     '        UISlider *slider = [[UISlider alloc] initWithFrame:CGRectMake(0.0, 0.0, 158.0, 30.0)];\n'
     '        MarufYTStyleSlider(slider);'),
    ('        valueLabel.font = [UIFont systemFontOfSize:10.0];\n        valueLabel.textColor = UIColor.tertiaryLabelColor;',
     '        valueLabel.font = [UIFont preferredFontForTextStyle:UIFontTextStyleCaption1];\n        valueLabel.textColor = MarufYTValueColor();'),
    ('        if ([item[@"subtitle"] length] == 0) {\n            cell.detailTextLabel.text = summary;\n'
     '            cell.detailTextLabel.textColor = YTKACEAccentColor();\n        } else {\n            UILabel *value = [UILabel new];\n'
     '            value.text = summary;\n            value.font = [UIFont systemFontOfSize:15.0];\n            value.textColor = YTKACEAccentColor();\n'
     '            value.textAlignment = NSTextAlignmentRight;\n            [value sizeToFit];\n            cell.accessoryView = value;\n        }',
     '        // Current value in secondary grey with a menu chevron (was accent red).\n'
     '        cell.detailTextLabel.text = [item[@"subtitle"] length] == 0 ? nil : item[@"subtitle"];\n'
     '        cell.accessoryView = MarufYTMenuValueView(summary, 170.0);'),
    ('        value.font = [UIFont systemFontOfSize:15.0];\n        value.textColor = YTKACEAccentColor();',
     '        value.font = MarufYTValueFont();\n        value.textColor = MarufYTValueColor();'),
    ('        UIView *dot = [[UIView alloc] initWithFrame:CGRectMake(0.0, 0.0, 28.0, 28.0)];\n        dot.backgroundColor = color;\n'
     '        dot.layer.cornerRadius = 14.0;\n        dot.layer.borderWidth = 2.0;\n        dot.layer.borderColor = UIColor.secondaryLabelColor.CGColor;',
     '        UIView *dot = [[UIView alloc] initWithFrame:CGRectMake(0.0, 0.0, 26.0, 26.0)];\n        dot.backgroundColor = color;\n'
     '        dot.layer.cornerRadius = 13.0;\n        dot.layer.borderWidth = 1.0;\n'
     '        dot.layer.borderColor = [UIColor.separatorColor resolvedColorWithTraitCollection:cell.traitCollection].CGColor;'),
    ('        cell.textLabel.font = [UIFont systemFontOfSize:10.0];\n        cell.textLabel.textColor = UIColor.secondaryLabelColor;',
     '        cell.textLabel.font = MarufYTFootnoteFont();\n        cell.textLabel.textColor = UIColor.secondaryLabelColor;'),
    # Liquid Glass page: depth toggle
    ('            YTKACEToggleDetail(@"Shrink Tab Bar When Scrolling", @"Needs the Liquid Glass tab bar.",',
     '            YTKACEToggleDetail(@"Floating Tab Bar Depth", @"Soft shadow under the floating glass tab bar.",\n'
     '                               @"YTKACE.Preference.Glass.DepthShadow"),\n'
     '            YTKACEToggleDetail(@"Shrink Tab Bar When Scrolling", @"Needs the Liquid Glass tab bar.",'),
    # Branded literals
    ('@[@"ytkace", @"YTKACE", @"YTKACE.Preference.Tabs.Hidden.YTKACETab"]',
     '@[@"ytkace", MarufYTProductName, @"YTKACE.Preference.Tabs.Hidden.YTKACETab"]'),
], [B, T])

pages = pending[ROOT / 'Tweak/Settings/YTKACESettingsPages.mm']
# Backup dialog title (first argument of the confirmation after "_backupRunning) return;").
anchor = '    BOOL shown = YTKACEShowYouTubeConfirmation(\n        @"YTKACE",'
if pages.count(anchor) != 1:
    sys.exit('backup dialog anchor not found')
pages = pages.replace(anchor, '    BOOL shown = YTKACEShowYouTubeConfirmation(\n        MarufYTProductName,')
# AiSList default reporter name shown in settings.
pages = pages.replace('@"YTKACE.Preference.Feed.AIReportName", @"YTKACE")',
                      '@"YTKACE.Preference.Feed.AIReportName", MarufYTProductName)')
# Tab-bar glass mode option "YTKACE" (the floating capsule) is the MarufYT capsule.
pages = pages.replace('@[@"Default", @"YTKACE", @"YouTube", @"Off"], @[@0, @1, @2, @3],',
                      '@[@"Default", MarufYTProductName, @"YouTube", @"Off"], @[@0, @1, @2, @3],')

# Coloured dot for rows that carry a "dotKey" (SponsorBlock categories).
helper = '''
// MarufYT: small colour dot for rows that carry a "dotKey" (SponsorBlock
// categories), so behaviour rows show the segment colour they use.
static UIImage *YTKACEItemDotImage(NSDictionary *item) {
    NSString *key = item[@"dotKey"];
    if (key.length == 0) return nil;
    NSString *stored = YTKACEPreferenceObject(key);
    UIColor *color = YTKACEColorFromHex([stored isKindOfClass:NSString.class] ? stored : item[@"dotFallback"]);
    CGFloat side = 12.0;
    UIGraphicsImageRenderer *renderer = [[UIGraphicsImageRenderer alloc] initWithSize:CGSizeMake(side, side)];
    return [[renderer imageWithActions:^(__unused UIGraphicsImageRendererContext *context) {
        [color setFill];
        [[UIBezierPath bezierPathWithOvalInRect:CGRectMake(0, 0, side, side)] fill];
    }] imageWithRenderingMode:UIImageRenderingModeAlwaysOriginal];
}
'''
anchor = 'static NSDictionary *YTKACEActionDetail(NSString *title,'
if pages.count(anchor) != 1:
    sys.exit('dot helper anchor not found')
pages = pages.replace(anchor, helper.lstrip('\n') + '\n' + anchor)

# SponsorBlock: MAIN / ALERTS / DEARROW / SKIPPING / SEGMENT COLORS.
old_sb_head = '''        YTKACEToggleDetail(@"Player Button",
                           @"Adds a shield to the player to whitelist channels, vote on segments and submit new ones.",
                           @"YTKACE.Preference.SponsorBlock.OverlayButton"),
        YTKACEPickerDetail(@"Skip Notice", @"Shown after a segment is skipped.",'''
new_sb_head = '''        YTKACEToggleDetail(@"Player Button",
                           @"Adds a shield to the player to whitelist channels, vote on segments and submit new ones.",
                           @"YTKACE.Preference.SponsorBlock.OverlayButton")
    ]];
    NSMutableArray<NSString *> *titles = [NSMutableArray arrayWithObject:YTKACELocalized(@"MAIN")];

    [sections addObject:@[
        YTKACEPickerDetail(@"Skip Notice", @"Shown after a segment is skipped.",'''
old_sb_mid = '''                     1.0, 10.0, 1.0, 4.0)
    ]];
    NSMutableArray<NSString *> *titles = [NSMutableArray arrayWithObject:YTKACELocalized(@"MAIN")];
'''
new_sb_mid = '''                     1.0, 10.0, 1.0, 4.0)
    ]];
    [titles addObject:YTKACELocalized(@"ALERTS")];
'''
old_sb_loop = '''    for (NSDictionary<NSString *, NSString *> *definition in
         YTKACESponsorCategoryDefinitions()) {
        NSString *category = definition[@"id"];
        BOOL highlight = [category isEqualToString:@"poi_highlight"];
        [sections addObject:@[
            highlight
                ? YTKACEPicker(@"Behavior", YTKACESponsorBehaviorKey(category),
                               @[@"Show Marker", @"Disabled"], @[@3, @2], 1, @"", @"")
                : YTKACEPicker(@"Behavior", YTKACESponsorBehaviorKey(category),
                               @[@"Auto-skip", @"Ask", @"Show Marker", @"Disabled"],
                               @[@0, @1, @3, @2],
                               [category isEqualToString:@"sponsor"] ? 0 : 3,
                               @"", @""),
            YTKACEColor(@"Segment Color", YTKACESponsorColorKey(category),
                        definition[@"color"])
        ]];
        [titles addObject:YTKACELocalized([definition[@"title"] uppercaseString])];
    }
'''
new_sb_loop = '''    // MarufYT: one compact row per category instead of one section each.
    // Same keys, options and defaults as before.
    NSMutableArray *behaviours = [NSMutableArray array];
    NSMutableArray *colours = [NSMutableArray array];
    for (NSDictionary<NSString *, NSString *> *definition in
         YTKACESponsorCategoryDefinitions()) {
        NSString *category = definition[@"id"];
        BOOL highlight = [category isEqualToString:@"poi_highlight"];
        NSMutableDictionary *behaviour = [(highlight
            ? YTKACEPicker(definition[@"title"], YTKACESponsorBehaviorKey(category),
                           @[@"Show Marker", @"Disabled"], @[@3, @2], 1, @"", @"")
            : YTKACEPicker(definition[@"title"], YTKACESponsorBehaviorKey(category),
                           @[@"Auto-skip", @"Ask", @"Show Marker", @"Disabled"],
                           @[@0, @1, @3, @2],
                           [category isEqualToString:@"sponsor"] ? 0 : 3,
                           @"", @"")) mutableCopy];
        behaviour[@"dotKey"] = YTKACESponsorColorKey(category);
        behaviour[@"dotFallback"] = definition[@"color"];
        [behaviours addObject:behaviour];
        [colours addObject:YTKACEColor(definition[@"title"], YTKACESponsorColorKey(category),
                                       definition[@"color"])];
    }
    [sections addObject:behaviours];
    [titles addObject:YTKACELocalized(@"SKIPPING")];
    [sections addObject:colours];
    [titles addObject:YTKACELocalized(@"SEGMENT COLORS")];
'''
for old, new in [(old_sb_head, new_sb_head), (old_sb_mid, new_sb_mid), (old_sb_loop, new_sb_loop)]:
    if pages.count(old) != 1:
        sys.exit(f'SponsorBlock anchor not found: {old[:60]!r}')
    pages = pages.replace(old, new)
pending[ROOT / 'Tweak/Settings/YTKACESettingsPages.mm'] = pages

for path, text in pending.items():
    path.write_text(text, encoding='utf-8', newline='\n')
    print('wrote', path.relative_to(ROOT).as_posix())
