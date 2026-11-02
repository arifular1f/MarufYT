// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// URLs for images and captions come from YouTube's own objects. Before
// MarufYT fetches one itself it requires HTTPS, so a malformed or downgraded
// URL is never requested in the clear.

#import <Foundation/Foundation.h>

static inline BOOL MarufYTIsSecureURL(NSURL *url) {
    return url != nil && [url.scheme caseInsensitiveCompare:@"https"] == NSOrderedSame &&
        url.host.length != 0 && url.user == nil && url.password == nil &&
        (url.port == nil || url.port.integerValue == 443);
}

FOUNDATION_EXPORT BOOL MarufYTIsTrustedMediaURL(NSURL *url);
FOUNDATION_EXPORT NSURLRequest *MarufYTRedirectRequest(NSURLRequest *previous, NSURLRequest *next, BOOL media);
FOUNDATION_EXPORT NSURLSession *MarufYTMakeSecureSession(NSURLSessionConfiguration *configuration);

// A small client around a standard session, not a host-wide NSURLSession hook.
// Invalid initial URLs fail asynchronously, so completion-based callers never hang.
@interface MarufYTNetwork : NSObject
+ (instancetype)sharedClient;
- (NSURLSessionDataTask *)dataTaskWithURL:(NSURL *)url completionHandler:(void (^)(NSData *, NSURLResponse *, NSError *))completion;
- (NSURLSessionDataTask *)dataTaskWithRequest:(NSURLRequest *)request completionHandler:(void (^)(NSData *, NSURLResponse *, NSError *))completion;
- (NSURLSessionDataTask *)dataTaskWithRequest:(NSURLRequest *)request;
@end
