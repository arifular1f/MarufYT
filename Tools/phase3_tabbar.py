#!/usr/bin/env python3
"""Record of the Phase 3 tab-bar changes applied to TabBarHooks.mm. Each anchor
must match exactly once or nothing is written.

Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
path = ROOT / 'Tweak/Features/Navigation/TabBarHooks.mm'
s = path.read_text(encoding='utf-8')


def once(old, new):
    global s
    n = s.count(old)
    if n != 1:
        sys.exit(f'anchor found {n}x: {old[:100]!r}')
    s = s.replace(old, new)


# A. imports
once('#import "../../MarufYT/Design/MarufYTDesign.h"\n',
     '#import "../../MarufYT/Design/MarufYTDesign.h"\n#import "../../MarufYT/Design/MarufYTLayoutMath.h"\n')

# B. mode resolution: a stored choice wins; the default is decided in one tested place.
once('''NSInteger YTKACETabBarGlassMode(void) {
    NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
    id value = [defaults objectForKey:YTKACETabBarGlassModeKey];
    if ([value respondsToSelector:@selector(integerValue)]) return [value integerValue];
    id legacy = [defaults objectForKey:@"YTKACE.Preference.Tabs.Glass"];
    if (legacy != nil) return [legacy boolValue] ? 1 : 0;
    // MarufYT: no stored choice, use the design preset.
    return MarufYTPresetTabGlassMode();
}''', '''NSInteger YTKACETabBarGlassMode(void) {
    NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
    id stored = [defaults objectForKey:YTKACETabBarGlassModeKey];
    id legacy = [defaults objectForKey:@"YTKACE.Preference.Tabs.Glass"];
    BOOL hasStored = [stored respondsToSelector:@selector(integerValue)];
    // MarufYT: MarufYTResolveTabMode (tested in Tests/native) decides. A stored
    // choice always wins; with nothing stored the default is the simple bar.
    return (NSInteger)MarufYTResolveTabMode(hasStored, hasStored ? [stored integerValue] : 0,
                                            legacy != nil, [legacy boolValue],
                                            MarufYTPresetTabGlassMode());
}''')

# C. MarufYT tab layout: positions from the tab's own bounds and a native sibling.
start = s.index('static void YTKACELayoutReplacementTab(UIView *view, UIImageView *icon, UILabel *label,')
end = s.index('static BOOL YTKACEViewIsVisible(UIView *view) {')
new_layout = r'''static BOOL YTKACEIsPivotItemView(UIView *view) {
    return [NSStringFromClass(view.class) containsString:@"PivotBarItemView"];
}

static BOOL YTKACEIsReplacementItem(UIView *view) {
    return [view viewWithTag:YTKACEExtraLabelTag] != nil || [view viewWithTag:0x59414347] != nil;
}

static void YTKACECollectNativeSiblings(UIView *root, UIView *except, NSMutableArray<UIView *> *out) {
    for (UIView *child in root.subviews) {
        if (YTKACEIsPivotItemView(child)) {
            if (child != except && !child.hidden && CGRectGetWidth(child.bounds) > 0.0 &&
                !YTKACEIsReplacementItem(child)) {
                [out addObject:child];
            }
            continue;  // items do not nest
        }
        YTKACECollectNativeSiblings(child, except, out);
    }
}

static UIView *YTKACEPivotBarOfItem(UIView *item) {
    for (UIView *current = item.superview; current != nil; current = current.superview) {
        if ([NSStringFromClass(current.class) containsString:@"PivotBarView"]) return current;
    }
    return nil;
}

static BOOL YTKACEItemFlag(UIView *item, NSString *name) {
    SEL getter = NSSelectorFromString(name);
    return [item respondsToSelector:getter] && ((BOOL (*)(id, SEL))objc_msgSend)(item, getter);
}

// A native sibling's label and icon, measured in its own coordinates. Used as
// the reference for the MarufYT tab, and to decide whether the host shows
// labels at all. Siblings MarufYT replaced are skipped, so MarufYT never
// measures its own work.
typedef struct {
    int considered;
    int showingLabel;
    BOOL haveReference;
    CGFloat refHeight;
    CGFloat refIconCenterY;
    CGFloat refLabelMinY;
    CGFloat refLabelHeight;
} YTKACESiblingSurvey;

static YTKACESiblingSurvey YTKACESurveyNativeSiblings(UIView *item) {
    YTKACESiblingSurvey survey;
    memset(&survey, 0, sizeof survey);
    UIView *bar = YTKACEPivotBarOfItem(item);
    if (bar == nil) return survey;
    NSMutableArray<UIView *> *siblings = [NSMutableArray array];
    YTKACECollectNativeSiblings(bar, item, siblings);
    [siblings sortUsingComparator:^NSComparisonResult(UIView *left, UIView *right) {
        CGFloat a = CGRectGetMinX([left convertRect:left.bounds toView:bar]);
        CGFloat b = CGRectGetMinX([right convertRect:right.bounds toView:bar]);
        return a < b ? NSOrderedAscending : (a > b ? NSOrderedDescending : NSOrderedSame);
    }];
    for (UIView *sibling in siblings) {
        UILabel *nativeLabel = YTKACEFindNativeLabel(sibling);
        if (nativeLabel == nil) continue;
        survey.considered += 1;
        BOOL shows = nativeLabel.text.length != 0 && !nativeLabel.hidden && nativeLabel.alpha > 0.01 &&
            !YTKACEItemFlag(sibling, @"hideLabel");
        if (!shows) continue;
        survey.showingLabel += 1;
        if (survey.haveReference) continue;
        UIImageView *nativeIcon = YTKACEFindImageView(sibling);
        if (nativeIcon == nil || nativeIcon.hidden) continue;
        CGRect labelRect = [nativeLabel convertRect:nativeLabel.bounds toView:sibling];
        CGRect iconRect = [nativeIcon convertRect:nativeIcon.bounds toView:sibling];
        BOOL usable = !CGRectIsEmpty(labelRect) && !CGRectIsEmpty(iconRect) &&
            CGRectContainsRect(sibling.bounds, labelRect) && CGRectContainsRect(sibling.bounds, iconRect) &&
            CGRectGetMaxY(iconRect) <= CGRectGetMinY(labelRect) + 2.0;
        if (!usable) continue;
        survey.haveReference = YES;
        survey.refHeight = CGRectGetHeight(sibling.bounds);
        survey.refIconCenterY = CGRectGetMidY(iconRect);
        survey.refLabelMinY = CGRectGetMinY(labelRect);
        survey.refLabelHeight = CGRectGetHeight(labelRect);
    }
    return survey;
}

// The MarufYT tab follows the host: hidden when the user hides tab labels,
// when the host flags this item (YouTube 21.43.5 and later), or when no native
// tab shows a label (icon-only layouts delivered by remote config).
static BOOL YTKACEReplacementLabelHidden(UIView *item, BOOL preferenceHidesLabels) {
    YTKACESiblingSurvey survey = YTKACESurveyNativeSiblings(item);
    return MarufYTShouldHideReplacementLabel(preferenceHidesLabels, YTKACEItemFlag(item, @"hideLabel"),
                                             survey.considered, survey.showingLabel);
}

static void YTKACELayoutReplacementTab(UIView *view, UIImageView *icon, UILabel *label,
                                       __unused UIImageView *nativeIcon, __unused UILabel *nativeLabel,
                                       BOOL hideLabel) {
    CGRect bounds = view.bounds;
    if (CGRectIsEmpty(bounds)) return;
    YTKACESiblingSurvey survey = YTKACESurveyNativeSiblings(view);
    MarufYTReplacementInput input;
    memset(&input, 0, sizeof input);
    input.width = CGRectGetWidth(bounds);
    input.height = CGRectGetHeight(bounds);
    input.hideLabel = hideLabel;
    input.haveReference = survey.haveReference;
    input.refHeight = survey.refHeight;
    input.refIconCenterY = survey.refIconCenterY;
    input.refLabelMinY = survey.refLabelMinY;
    input.refLabelHeight = survey.refLabelHeight;
    input.labelLineHeight = label.font.lineHeight;
    MarufYTReplacementOutput output = MarufYTReplacementTabLayout(input);
    CGRect iconFrame = CGRectMake(output.iconCenterX - output.iconSize * 0.5,
                                  output.iconCenterY - output.iconSize * 0.5, output.iconSize, output.iconSize);
    if (!CGRectEqualToRect(icon.frame, iconFrame)) icon.frame = iconFrame;
    CGRect labelFrame = CGRectMake(CGRectGetMinX(bounds), output.labelMinY, CGRectGetWidth(bounds), output.labelHeight);
    if (!CGRectEqualToRect(label.frame, labelFrame)) label.frame = labelFrame;
    label.adjustsFontSizeToFitWidth = YES;
    label.minimumScaleFactor = 0.8;
}

'''
s = s[:start] + new_layout + s[end:]

# D. MarufYT tab label policy (download/"MarufYT" tab)
once('''    BOOL hideLabel = YTKACETabLabelsHidden(view);
    if (definiteOther) {
        YTKACERestorePivotItem(view, nativeLabel, hideLabel);
        return;
    }''', '''    BOOL preferenceHidesLabel = YTKACETabLabelsHidden(view);
    if (definiteOther) {
        YTKACERestorePivotItem(view, nativeLabel, preferenceHidesLabel);
        return;
    }
    BOOL hideLabel = YTKACEReplacementLabelHidden(view, preferenceHidesLabel);''')

# E. extra tabs use the same policy
once('''    BOOL hideLabel = YTKACETabLabelsHidden(view);
    UILabel *nativeLabel = YTKACEFindNativeLabel(view);
    UILabel *label = (UILabel *)[view viewWithTag:YTKACEExtraLabelTag];''',
     '''    BOOL hideLabel = YTKACEReplacementLabelHidden(view, YTKACETabLabelsHidden(view));
    UILabel *nativeLabel = YTKACEFindNativeLabel(view);
    UILabel *label = (UILabel *)[view viewWithTag:YTKACEExtraLabelTag];''')

# F. capsule frame: bar size and host item height only (no safe-area term)
once('''    CGFloat itemHeight = CGRectGetHeight(receiver.bounds) - receiver.safeAreaInsets.bottom;
    CGFloat extra = 7.0;
    CGFloat glassHeight = MAX(itemHeight, 44.0) + extra * 2.0;
    CGFloat glassTop = MIN(0.0, CGRectGetHeight(receiver.bounds) - glassHeight - 4.0);
    BOOL expanded = [objc_getAssociatedObject(receiver, YTKACEPivotBarExpandedAssociation) boolValue];
    NSUInteger tabs = 0;
    for (UIView *item in YTKACESortedPivotItems(receiver)) {
        if (!item.hidden && CGRectGetWidth(item.bounds) > 0.0) tabs += 1;
    }
    CGFloat barWidth = CGRectGetWidth(receiver.bounds);
    CGRect available = UIEdgeInsetsInsetRect(receiver.bounds, receiver.safeAreaInsets);
    CGFloat margin = expanded ? 14.0 : 21.0;
    CGFloat glassWidth = barWidth - margin * 2.0;
    // The host bar's safe area is authoritative in landscape and windowed layouts.
    // A screen's short side is unrelated to the actual host container width.
    if (CGRectGetWidth(available) > margin * 2.0) {
        glassWidth = MIN(glassWidth, CGRectGetWidth(available) - margin * 2.0);
    }
    if (tabs > 0 && tabs <= 4) {
        glassWidth = MIN(glassWidth, 86.0 * (CGFloat)tabs + 16.0);
    }
    CGFloat centerX = CGRectGetWidth(available) > 0.0 ? CGRectGetMidX(available) : CGRectGetMidX(receiver.bounds);
    CGRect frame = CGRectMake(centerX - glassWidth * 0.5, glassTop, glassWidth, glassHeight);''',
     '''    BOOL expanded = [objc_getAssociatedObject(receiver, YTKACEPivotBarExpandedAssociation) boolValue];
    NSUInteger tabs = 0;
    CGFloat hostItemHeight = 0.0;
    for (UIView *item in YTKACESortedPivotItems(receiver)) {
        if (item.hidden || CGRectGetWidth(item.bounds) <= 0.0) continue;
        tabs += 1;
        hostItemHeight = MAX(hostItemHeight, CGRectGetHeight(item.bounds));
    }
    // MarufYT: the capsule is a function of the bar's width and height and the
    // host's item height (MarufYTCapsuleFrame, tested). It no longer uses the
    // bottom safe-area inset, which is 0 while the host is still laying out and
    // made the capsule grow past the top of the bar and then jump.
    CGFloat margin = expanded ? 14.0 : 21.0;
    // The host bar's safe area is authoritative in landscape and windowed layouts.
    // A screen's short side is unrelated to the actual host container width.
    CGRect available = UIEdgeInsetsInsetRect(receiver.bounds, receiver.safeAreaInsets);
    BOOL useAvailable = CGRectGetWidth(available) > margin * 2.0;
    MarufYTRect capsule = MarufYTCapsuleFrame(useAvailable ? CGRectGetWidth(available) : CGRectGetWidth(receiver.bounds),
                                              CGRectGetHeight(receiver.bounds), hostItemHeight, (int)tabs, expanded);
    CGRect frame = CGRectMake((useAvailable ? CGRectGetMinX(available) : 0.0) + capsule.x, capsule.y,
                              capsule.width, capsule.height);
    CGFloat glassHeight = CGRectGetHeight(frame);''')

# G. slot geometry shares the tested math
once('''static void YTKACETabGeometry(CGRect glass, NSUInteger count, CGFloat *start, CGFloat *step, CGFloat *overlap) {
    CGFloat spill = count <= 4 ? 8.0 : 16.0;
    CGFloat pitch = count == 0 ? 0.0 : (CGRectGetWidth(glass) - 8.0 - spill) / (CGFloat)count;
    if (start) *start = CGRectGetMinX(glass) + 4.0;
    if (step) *step = pitch;
    if (overlap) *overlap = spill;
}''', '''static MarufYTRect YTKACEMathRect(CGRect rect) {
    MarufYTRect result;
    result.x = rect.origin.x;
    result.y = rect.origin.y;
    result.width = rect.size.width;
    result.height = rect.size.height;
    return result;
}

static void YTKACETabGeometry(CGRect glass, NSUInteger count, CGFloat *start, CGFloat *step, CGFloat *overlap) {
    MarufYTTabGeometry geometry = MarufYTTabSlots(YTKACEMathRect(glass), (int)count);
    if (start) *start = geometry.start;
    if (step) *step = geometry.pitch;
    if (overlap) *overlap = geometry.overlap;
}''')

once('''    CGFloat start = 0.0, slot = 0.0, overlap = 0.0;
    YTKACETabGeometry(glassFrame, visible.count, &start, &slot, &overlap);
    for (NSUInteger index = 0; index < visible.count; index++) {
        UIView *item = visible[index];
        if (item.superview == nil) continue;
        CGRect current = [item convertRect:item.bounds toView:bar];
        CGRect target = CGRectMake(start + overlap * 0.5 + slot * index,
                                   CGRectGetMidY(glassFrame) - CGRectGetHeight(current) * 0.5,
                                   slot, CGRectGetHeight(current));''',
     '''    MarufYTRect glass = YTKACEMathRect(glassFrame);
    MarufYTTabGeometry geometry = MarufYTTabSlots(glass, (int)visible.count);
    for (NSUInteger index = 0; index < visible.count; index++) {
        UIView *item = visible[index];
        if (item.superview == nil) continue;
        // Index-based: the target depends on the slot, never on where a previous pass left the item.
        MarufYTRect slot = MarufYTTabItemFrame(glass, geometry, (int)index, CGRectGetHeight(item.bounds));
        CGRect target = CGRectMake(slot.x, slot.y, slot.width, slot.height);''')

path.write_text(s, encoding='utf-8', newline='\n')
print('ok')
