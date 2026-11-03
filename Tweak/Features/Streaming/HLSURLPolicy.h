// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
#pragma once
#import "../../Runtime/URLPolicy.h"
#include <arpa/inet.h>

// Only validates URLs MarufYT caches/injects. Does not hook the host's network
// stack or claim to validate redirects or URLs inside a manifest.
static inline BOOL MarufYTIsValidHLSManifestURL(id value) {
    if (![value isKindOfClass:NSString.class] || [value length] == 0) return NO;
    NSURL *url = [NSURL URLWithString:value];
    if (!MarufYTIsSecureURL(url)) return NO;
    // Validate the original authority too: Foundation may normalize malformed
    // bracketed hosts into a valid-looking DNS name before exposing URL.host.
    NSRange separator = [value rangeOfString:@"://"];
    if (separator.location == NSNotFound) return NO;
    NSUInteger start = NSMaxRange(separator);
    NSRange end = [value rangeOfCharacterFromSet:[NSCharacterSet characterSetWithCharactersInString:@"/?#"]
                                       options:0 range:NSMakeRange(start, [value length] - start)];
    NSString *authority = [value substringWithRange:NSMakeRange(start,
        (end.location == NSNotFound ? [value length] : end.location) - start)];
    if ([authority containsString:@"%"] || [authority containsString:@"@"]) return NO;
    NSString *host = authority;
    NSString *port = nil;
    if ([host hasPrefix:@"["]) {
        NSRange close = [host rangeOfString:@"]"];
        if (close.location == NSNotFound) return NO;
        NSString *tail = [host substringFromIndex:NSMaxRange(close)];
        if (tail.length != 0) {
            if (![tail hasPrefix:@":"]) return NO;
            port = [tail substringFromIndex:1];
        }
        host = [host substringWithRange:NSMakeRange(1, close.location - 1)];
        struct in6_addr address;
        if (inet_pton(AF_INET6, host.UTF8String, &address) != 1) return NO;
    } else {
        NSArray<NSString *> *parts = [host componentsSeparatedByString:@":"];
        if (parts.count > 2) return NO;
        host = parts.firstObject;
        if (parts.count == 2) port = parts.lastObject;
    }
    if (port != nil && (port.length == 0 || port.integerValue != 443 || [port rangeOfCharacterFromSet:
        [[NSCharacterSet characterSetWithCharactersInString:@"0123456789"] invertedSet]].location != NSNotFound)) return NO;
    if ([host containsString:@":"]) {
        struct in6_addr address;
        return inet_pton(AF_INET6, host.UTF8String, &address) == 1;
    }
    if ([host hasSuffix:@"."]) host = [host substringToIndex:host.length - 1];
    if (host.length == 0 || host.length > 253) return NO;
    if ([host containsString:@"."] && [host rangeOfCharacterFromSet:
        [[NSCharacterSet characterSetWithCharactersInString:@"0123456789."] invertedSet]].location == NSNotFound) {
        struct in_addr address;
        return inet_pton(AF_INET, host.UTF8String, &address) == 1;
    }
    NSCharacterSet *invalid = [[NSCharacterSet characterSetWithCharactersInString:
        @"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"] invertedSet];
    for (NSString *label in [host componentsSeparatedByString:@"."]) {
        if (label.length == 0 || label.length > 63 || [label hasPrefix:@"-"] ||
            [label hasSuffix:@"-"] || [label rangeOfCharacterFromSet:invalid].location != NSNotFound)
            return NO;
    }
    return YES;
}

static inline NSString *MarufYTSelectHLSManifestURL(id preferred, id native) {
    if (MarufYTIsValidHLSManifestURL(preferred)) return preferred;
    return MarufYTIsValidHLSManifestURL(native) ? native : nil;
}
