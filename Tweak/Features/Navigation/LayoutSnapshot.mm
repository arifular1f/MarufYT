#import "LayoutSnapshot.h"
#import "../Downloads/DownloadLog.h"
#import "../../Runtime/Preferences.h"

#import <UIKit/UIKit.h>

// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

static const NSUInteger kSnapshotViewLimit = 40;
static const NSInteger kSnapshotDepthLimit = 14;

static BOOL SnapshotWanted(UIView *view) {
    NSString *name = NSStringFromClass(view.class);
    static NSArray<NSString *> *needles;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        needles = @[@"YTPivotBar", @"YTChipCloud", @"YTFilterChipBar", @"YTHeaderView",
                    @"YTNavigationBar", @"YTRightNavigationButtons", @"YTFloatingPivot",
                    @"YTTabsView", @"YTMainAppControlsOverlay"];
    });
    for (NSString *needle in needles) {
        if ([name containsString:needle]) return YES;
    }
    return NO;
}

static void SnapshotWalk(UIView *view, UIView *root, NSInteger depth, NSUInteger *count) {
    if (*count >= kSnapshotViewLimit || depth > kSnapshotDepthLimit) return;
    if (SnapshotWanted(view)) {
        CGRect frame = [view convertRect:view.bounds toView:root];
        YTKACEDownloadLog(@"layout", @"%@ frame=(%.1f,%.1f,%.1f,%.1f) hidden=%d alpha=%.2f",
                          NSStringFromClass(view.class), frame.origin.x, frame.origin.y,
                          frame.size.width, frame.size.height, view.hidden, view.alpha);
        (*count)++;
    }
    for (UIView *child in view.subviews) SnapshotWalk(child, root, depth + 1, count);
}

static id StoredPreference(NSString *key) {
    return [[NSUserDefaults standardUserDefaults] objectForKey:key];
}

void YTKACELogLayoutSnapshot(void) {
    UIWindow *window = nil;
    for (UIScene *scene in UIApplication.sharedApplication.connectedScenes) {
        if (![scene isKindOfClass:UIWindowScene.class]) continue;
        for (UIWindow *candidate in ((UIWindowScene *)scene).windows) {
            if (candidate.isKeyWindow) window = candidate;
        }
    }
    NSString *version = [NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"];
    YTKACEDownloadLog(@"layout", @"snapshot host=%@ ios=%@ window=%@", version ?: @"?",
                      UIDevice.currentDevice.systemVersion,
                      window ? NSStringFromCGRect(window.bounds) : @"none");
    YTKACEDownloadLog(@"layout", @"prefs glassMode=%@ labelsHidden=%@ homeTabsHidden=%@ reduceMotion=%d reduceTransparency=%d",
                      StoredPreference(@"YTKACE.Preference.Tabs.GlassMode") ?: @"unset",
                      StoredPreference(@"YTKACE.Preference.Tabs.LabelsHidden") ?: @"unset",
                      StoredPreference(@"YTKACE.Preference.Feed.HomeTabsHidden") ?: @"unset",
                      UIAccessibilityIsReduceMotionEnabled(),
                      UIAccessibilityIsReduceTransparencyEnabled());
    if (!window) return;
    YTKACEDownloadLog(@"layout", @"safeArea=%@", NSStringFromUIEdgeInsets(window.safeAreaInsets));
    NSUInteger count = 0;
    SnapshotWalk(window, window, 0, &count);
}
