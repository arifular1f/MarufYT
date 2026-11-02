// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
#import "URLPolicy.h"
#import "NetworkRules.h"

BOOL MarufYTIsTrustedMediaURL(NSURL *url) {
    return MarufYTIsSecureURL(url) && MarufYTMediaHostAllowed(url.host.UTF8String);
}

NSURLRequest *MarufYTRedirectRequest(NSURLRequest *previous, NSURLRequest *next, BOOL media) {
    if (!MarufYTIsSecureURL(previous.URL) || !MarufYTIsSecureURL(next.URL)) return nil;
    if (media && (!MarufYTIsTrustedMediaURL(previous.URL) || !MarufYTIsTrustedMediaURL(next.URL))) return nil;
    BOOL sameOrigin = [previous.URL.host.lowercaseString isEqual:next.URL.host.lowercaseString];
    // Cross-origin POST/body replay is refused for generic API clients. SABR
    // has its separate strict media-host boundary and may follow CDN redirects.
    if (!sameOrigin && !media && (previous.HTTPBody.length || previous.HTTPBodyStream ||
        next.HTTPBody.length || next.HTTPBodyStream)) return nil;
    NSMutableURLRequest *result = [next mutableCopy];
    if (!sameOrigin || media) {
        for (NSString *key in result.allHTTPHeaderFields.allKeys) {
            if (!MarufYTReplayHeaderAllowed(key.UTF8String)) [result setValue:nil forHTTPHeaderField:key];
        }
    }
    return result;
}

@interface MarufYTRedirectDelegate : NSObject <NSURLSessionTaskDelegate>
@end
@implementation MarufYTRedirectDelegate
- (void)URLSession:(NSURLSession *)session task:(NSURLSessionTask *)task
    willPerformHTTPRedirection:(NSHTTPURLResponse *)response newRequest:(NSURLRequest *)request
    completionHandler:(void (^)(NSURLRequest *))completionHandler {
    (void)session; (void)response;
    completionHandler(MarufYTRedirectRequest(task.currentRequest ?: task.originalRequest, request, NO));
}
@end

NSURLSession *MarufYTMakeSecureSession(NSURLSessionConfiguration *configuration) {
    static MarufYTRedirectDelegate *delegate;
    static dispatch_once_t once;
    dispatch_once(&once, ^{ delegate = [MarufYTRedirectDelegate new]; });
    return [NSURLSession sessionWithConfiguration:configuration delegate:delegate delegateQueue:nil];
}

@interface MarufYTNetwork ()
@property(nonatomic, strong) NSURLSession *session;
@end
@implementation MarufYTNetwork
+ (instancetype)sharedClient {
    static MarufYTNetwork *client;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        client = [MarufYTNetwork new];
        client.session = MarufYTMakeSecureSession(NSURLSessionConfiguration.defaultSessionConfiguration);
    });
    return client;
}
- (NSURLSessionDataTask *)dataTaskWithRequest:(NSURLRequest *)request completionHandler:(void (^)(NSData *, NSURLResponse *, NSError *))completion {
    if (!MarufYTIsSecureURL(request.URL)) {
        if (completion) dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            completion(nil, nil, [NSError errorWithDomain:NSURLErrorDomain code:NSURLErrorUnsupportedURL userInfo:nil]);
        });
        return nil;
    }
    return [self.session dataTaskWithRequest:request completionHandler:completion];
}
- (NSURLSessionDataTask *)dataTaskWithURL:(NSURL *)url completionHandler:(void (^)(NSData *, NSURLResponse *, NSError *))completion {
    // NSURLRequest cannot be constructed with a nil URL.
    if (!url) return [self dataTaskWithRequest:nil completionHandler:completion];
    return [self dataTaskWithRequest:[NSURLRequest requestWithURL:url] completionHandler:completion];
}
- (NSURLSessionDataTask *)dataTaskWithRequest:(NSURLRequest *)request {
    return MarufYTIsSecureURL(request.URL) ? [self.session dataTaskWithRequest:request] : nil;
}
@end
