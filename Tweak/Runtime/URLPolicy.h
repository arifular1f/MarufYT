// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// URLs for images and captions come from YouTube's own objects. Before
// MarufYT fetches one itself it requires HTTPS, so a malformed or downgraded
// URL is never requested in the clear.

#import <Foundation/Foundation.h>

static inline BOOL MarufYTIsSecureURL(NSURL *url) {
    return url != nil && [url.scheme caseInsensitiveCompare:@"https"] == NSOrderedSame &&
        url.host.length != 0;
}
