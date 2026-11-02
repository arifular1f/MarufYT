// MarufYT — project branding and identity.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

#import "MarufYTBranding.h"
#import "../../YTKACE.h"

#import <UIKit/UIKit.h>

#ifndef MARUFYT_BUILD_NUMBER
#define MARUFYT_BUILD_NUMBER "local"
#endif

NSString *const MarufYTProductName = @"MarufYT";
NSString *const MarufYTDeveloperName = @"arifular1f";
NSString *const MarufYTRepositoryURLString = @"https://github.com/arifular1f/MarufYT";
NSString *const MarufYTRepositoryDisplay = @"arifular1f/MarufYT";
NSString *const MarufYTDeveloperURLString = @"https://github.com/arifular1f";
NSString *const MarufYTPackageDescription = @"ROOTLESS · arm64";
NSString *const MarufYTUpstreamName = @"YTKACE";

NSString *MarufYTVersionString(void) {
    return YTKACEVersion;
}

NSString *MarufYTBuildNumber(void) {
    return @MARUFYT_BUILD_NUMBER;
}

NSString *MarufYTHostVersion(void) {
    NSString *version = [NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"];
    return [version isKindOfClass:NSString.class] && version.length != 0 ? version : @"—";
}

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
