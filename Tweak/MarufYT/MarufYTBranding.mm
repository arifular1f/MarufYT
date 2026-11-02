// MarufYT — project branding.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

#import "MarufYTBranding.h"

#import <UIKit/UIKit.h>

NSString *const MarufYTProductName = @"MarufYT";
NSString *const MarufYTDeveloperName = @"arifular1f";
NSString *const MarufYTRepositoryURLString = @"https://github.com/arifular1f/MarufYT";
NSString *const MarufYTDeveloperURLString = @"https://github.com/arifular1f";
NSString *const MarufYTUpstreamName = @"YTKACE";
NSString *const MarufYTUpstreamAuthor = @"itzzace";
NSString *const MarufYTUpstreamURLString = @"https://github.com/itzzace/ytkace";

NSString *MarufYTBrandedString(NSString *text) {
    if (text.length == 0) return text;
    if ([text rangeOfString:MarufYTUpstreamName].location == NSNotFound) return text;
    return [text stringByReplacingOccurrencesOfString:MarufYTUpstreamName
                                           withString:MarufYTProductName];
}

BOOL MarufYTIsOwnAccessibilityText(NSString *text) {
    return [text hasPrefix:MarufYTUpstreamName] || [text hasPrefix:MarufYTProductName];
}

void MarufYTOpenURLString(NSString *string) {
    NSURL *URL = [NSURL URLWithString:string];
    if (URL == nil) return;
    [UIApplication.sharedApplication openURL:URL options:@{} completionHandler:nil];
}
