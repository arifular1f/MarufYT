// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
// macOS executes the shipped Foundation URL, redirect, cleanup and redaction code.
// It does not run UIKit, YouTube, Google sign-in or a physical iPhone.
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import "URLPolicy.h"
#import "NetworkRules.h"
#import "SecurityLifecycle.h"
#import "Hooking.h"
#import "DownloadLog.h"
#include <stdio.h>
#include <initializer_list>
static unsigned checks, failures, cleared, signedOut;
#define CHECK(expr) do { ++checks; if (!(expr)) { ++failures; fprintf(stderr, "FAIL line %d\n", __LINE__); } } while (0)
void YTKACEClearCapturedRequests(void) { ++cleared; }
void YTKACESABRClearRequestState(void) { ++cleared; }
void YTKACEClearPlaylistAuthorization(void) { ++cleared; }
BOOL YTKACEInstallInstanceHook(NSString *className, NSString *selectorName, IMP replacement, IMP *storage) {
    Class cls = NSClassFromString(className); SEL sel = NSSelectorFromString(selectorName);
    Method m = class_getInstanceMethod(cls, sel); if (!m) return NO;
    if (storage) *storage = method_getImplementation(m);
    class_replaceMethod(cls, sel, replacement, method_getTypeEncoding(m)); return YES;
}
@interface SSOSecurityFixture : NSObject
- (void)signOut;
- (void)removeAccount:(id)account completion:(void (^)(void))completion;
- (void)setSelectedIdentity:(id)identity;
@end
@implementation SSOSecurityFixture
- (void)signOut { ++signedOut; }
- (void)removeAccount:(id)account completion:(void (^)(void))completion { (void)account; ++signedOut; if (completion) completion(); }
- (void)setSelectedIdentity:(id)identity { (void)identity; }
@end
static NSMutableURLRequest *Request(NSString *url) {
    return [NSMutableURLRequest requestWithURL:[NSURL URLWithString:url]];
}
int main(void) { @autoreleasepool {
    for (NSString *url in @[@"https://example.invalid/a", @"HTTPS://example.invalid:443/a"]) CHECK(MarufYTIsSecureURL([NSURL URLWithString:url]));
    for (NSString *url in @[@"http://example.invalid", @"file:///tmp/test", @"https://u:p@example.invalid", @"https://example.invalid:444"]) CHECK(!MarufYTIsSecureURL([NSURL URLWithString:url]));
    CHECK(!MarufYTIsSecureURL(nil));
    CHECK(MarufYTIsTrustedMediaURL([NSURL URLWithString:@"https://rr1.googlevideo.com/videoplayback"]));
    for (const char *host : {"evilgooglevideo.com", "googlevideo.com.attacker.invalid", "googlevideo.com.", "localhost", "127.0.0.1"}) CHECK(!MarufYTMediaHostAllowed(host));
    CHECK(MarufYTMediaHostAllowed("RR1.GOOGLEVIDEO.COM"));
    CHECK(!MarufYTMediaHostAllowed(NULL));
    for (const char *header : {"Authorization", "Cookie", "Proxy-Authorization", "X-Unknown-Token", "Host"}) CHECK(!MarufYTReplayHeaderAllowed(header));
    CHECK(MarufYTReplayHeaderAllowed("Range"));
    CHECK(!MarufYTRequestStateExpired(100, 1000)); CHECK(MarufYTRequestStateExpired(100, 1001));
    CHECK(MarufYTRequestStateExpired(100, 99)); CHECK(!MarufYTRequestStateExpired(0, 10000));
    NSMutableURLRequest *source = Request(@"https://example.invalid/a"), *next = Request(@"https://cdn.invalid/b");
    [next setValue:@"fixture" forHTTPHeaderField:@"Authorization"];
    [next setValue:@"fixture" forHTTPHeaderField:@"Cookie"];
    [next setValue:@"fixture" forHTTPHeaderField:@"X-Goog-Visitor-Id"];
    [next setValue:@"bytes=0-1" forHTTPHeaderField:@"Range"];
    NSURLRequest *clean = MarufYTRedirectRequest(source, next, NO);
    CHECK(clean && ![clean valueForHTTPHeaderField:@"Authorization"] && ![clean valueForHTTPHeaderField:@"Cookie"]);
    CHECK([[clean valueForHTTPHeaderField:@"Range"] isEqual:@"bytes=0-1"]);
    CHECK(![clean valueForHTTPHeaderField:@"X-Goog-Visitor-Id"]);
    source.HTTPMethod = @"POST"; source.HTTPBody = [@"fixture" dataUsingEncoding:NSUTF8StringEncoding];
    CHECK(!MarufYTRedirectRequest(source, next, NO));
    CHECK(!MarufYTRedirectRequest(source, Request(@"http://example.invalid/a"), NO));
    source = Request(@"https://rr1.googlevideo.com/a"); source.HTTPMethod = @"POST"; source.HTTPBody = [NSData data];
    next = Request(@"https://rr2.googlevideo.com/b"); [next setValue:@"fixture" forHTTPHeaderField:@"Authorization"];
    CHECK(MarufYTRedirectRequest(source, next, YES) && ![MarufYTRedirectRequest(source, next, YES) valueForHTTPHeaderField:@"Authorization"]);
    CHECK(!MarufYTRedirectRequest(source, Request(@"https://googlevideo.com.attacker.invalid"), YES));
    CHECK(MarufYTRedirectRequest(source, source, NO));
    for (NSString *message in @[@"Bearer fixture-value", @"Cookie: session=fixture-value", @"{\"access_token\":\"fixture-value\"}", @"APIKEY=fixture-value", @"response=fixture-value"]) CHECK(![YTKACERedactLogMessage(message) containsString:@"fixture-value"]);
    CHECK(![YTKACERedactLogMessage(@"video=dQw4w9WgXcQ") containsString:@"dQw4w9WgXcQ"]);
    CHECK(![YTKACERedactLogMessage(@"mail=fixture@example.invalid") containsString:@"fixture@example.invalid"]);
    CHECK(![YTKACERedactLogMessage(@"https://example.invalid/private/path") containsString:@"/private/path"]);
    CHECK(![YTKACERedactLogMessage(@"event\r\nforged line") containsString:@"\n"]);
    // F-01: deletion is limited to the legacy seed names, never downloads/settings.
    NSURL *root = [NSURL fileURLWithPath:[NSTemporaryDirectory() stringByAppendingPathComponent:NSUUID.UUID.UUIDString] isDirectory:YES];
    [NSFileManager.defaultManager createDirectoryAtURL:root withIntermediateDirectories:YES attributes:nil error:nil];
    for (NSString *name in @[@"sabr-seed.plist", @"player-request.pb", @"SettingsBackup.plist", @"keep.mp4"]) [[NSData data] writeToURL:[root URLByAppendingPathComponent:name] atomically:YES];
    MarufYTPurgeLegacyRequestFiles(root);
    CHECK(![NSFileManager.defaultManager fileExistsAtPath:[root URLByAppendingPathComponent:@"sabr-seed.plist"].path]);
    CHECK(![NSFileManager.defaultManager fileExistsAtPath:[root URLByAppendingPathComponent:@"player-request.pb"].path]);
    CHECK([NSFileManager.defaultManager fileExistsAtPath:[root URLByAppendingPathComponent:@"SettingsBackup.plist"].path]);
    CHECK([NSFileManager.defaultManager fileExistsAtPath:[root URLByAppendingPathComponent:@"keep.mp4"].path]);
    [NSFileManager.defaultManager removeItemAtURL:root error:nil];
    MarufYTInstallSecurityLifecycle();
    MarufYTInstallAccountBoundaryHook(SSOSecurityFixture.class, @"signOut");
    MarufYTInstallAccountBoundaryHook(SSOSecurityFixture.class, @"removeAccount:completion:");
    MarufYTInstallAccountBoundaryHook(SSOSecurityFixture.class, @"setSelectedIdentity:");
    unsigned before = cleared; NSUInteger prior = MarufYTSecurityGeneration();
    [[SSOSecurityFixture new] signOut];
    CHECK(signedOut == 1 && cleared >= before + 3 && MarufYTSecurityGeneration() > prior);
    __block BOOL completed = NO;
    [[SSOSecurityFixture new] removeAccount:@"fixture" completion:^{ completed = YES; }];
    CHECK(signedOut == 2 && completed);
    SSOSecurityFixture *picker = [SSOSecurityFixture new];
    NSObject *first = [NSObject new], *second = [NSObject new]; before = cleared;
    [picker setSelectedIdentity:first]; [picker setSelectedIdentity:first];
    CHECK(cleared == before);
    [picker setSelectedIdentity:second]; CHECK(cleared >= before + 3);
    dispatch_semaphore_t done = dispatch_semaphore_create(0); __block BOOL rejected = NO;
    NSURLSessionDataTask *task = [MarufYTNetwork.sharedClient dataTaskWithURL:[NSURL URLWithString:@"http://example.invalid"] completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        rejected = data == nil && response == nil && error.code == NSURLErrorUnsupportedURL; dispatch_semaphore_signal(done);
    }];
    CHECK(task == nil); CHECK(dispatch_semaphore_wait(done, dispatch_time(DISPATCH_TIME_NOW, 5 * NSEC_PER_SEC)) == 0 && rejected);
    printf("Foundation security: %u checks, %u failures\n", checks, failures);
    return failures ? 1 : 0;
} }
