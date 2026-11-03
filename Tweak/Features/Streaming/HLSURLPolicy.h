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
    NSString *host = url.host;
    // NSURL can retain encoded/otherwise malformed DNS hosts. Reject ambiguous
    // encodings and validate DNS labels; IPv6 literals use their actual grammar.
    if ([host hasPrefix:@"["] && [host hasSuffix:@"]"]) {
        host = [host substringWithRange:NSMakeRange(1, host.length - 2)];
        struct in6_addr address;
        return inet_pton(AF_INET6, host.UTF8String, &address) == 1;
    }
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
