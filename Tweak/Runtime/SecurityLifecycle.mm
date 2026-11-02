// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
#import "SecurityLifecycle.h"
#import "Hooking.h"
#import "NetworkRules.h"
#import "../Features/Downloads/DownloadLog.h"
#import <objc/runtime.h>
#include <stdlib.h>

static NSTimeInterval lastActivity;
static NSUInteger generation;
static NSObject *StateLock(void) {
    static NSObject *lock; static dispatch_once_t once;
    dispatch_once(&once, ^{ lock = [NSObject new]; }); return lock;
}
void MarufYTPurgeLegacyRequestFiles(NSURL *root) {
    if (!root.isFileURL) return;
    for (NSString *name in @[@"sabr-seed.plist", @"player-request.pb"]) {
        NSURL *file = [root URLByAppendingPathComponent:name];
        NSNumber *regular = nil, *symlink = nil;
        [file getResourceValue:&regular forKey:NSURLIsRegularFileKey error:nil];
        [file getResourceValue:&symlink forKey:NSURLIsSymbolicLinkKey error:nil];
        if (regular.boolValue || symlink.boolValue) [NSFileManager.defaultManager removeItemAtURL:file error:nil];
    }
}
static void PurgeLegacyFiles(void) {
    NSFileManager *manager = NSFileManager.defaultManager;
    for (NSNumber *kind in @[@(NSDocumentDirectory), @(NSApplicationSupportDirectory), @(NSCachesDirectory)]) {
        NSURL *base = [manager URLsForDirectory:(NSSearchPathDirectory)kind.integerValue inDomains:NSUserDomainMask].firstObject;
        if (!base) continue;
        NSURL *root = [base URLByAppendingPathComponent:@"YTKACE" isDirectory:YES];
        MarufYTPurgeLegacyRequestFiles(root);
    }
    [manager removeItemAtPath:[NSTemporaryDirectory() stringByAppendingPathComponent:@"ytkace-outgoing.pb"] error:nil];
}
void MarufYTClearRequestState(void) {
    @synchronized (StateLock()) { ++generation; lastActivity = 0; }
    // No host credentials, account database, settings or media are deleted.
    YTKACEClearCapturedRequests();
    YTKACESABRClearRequestState();
    YTKACEClearPlaylistAuthorization();
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{ PurgeLegacyFiles(); });
}
NSUInteger MarufYTSecurityGeneration(void) {
    @synchronized (StateLock()) { return generation; }
}
void MarufYTNoteRequestActivity(void) {
    @synchronized (StateLock()) { lastActivity = NSProcessInfo.processInfo.systemUptime; }
}
void MarufYTExpireRequestStateIfNeeded(void) {
    BOOL expired;
    @synchronized (StateLock()) {
        expired = MarufYTRequestStateExpired(lastActivity, NSProcessInfo.processInfo.systemUptime);
    }
    if (expired) MarufYTClearRequestState();
}

static const void *AccountBoundaryKey = &AccountBoundaryKey;
static BOOL BoundaryChanged(id receiver, NSString *name, id value) {
    if (![name hasPrefix:@"set"]) return YES;
    // Avoid repeatedly purging a live download when the host reassigns the same
    // identity object. Only its address is retained, not an account or credential.
    unsigned long long identity = (unsigned long long)(uintptr_t)(__bridge void *)value;
    @synchronized (receiver) {
        NSNumber *previous = objc_getAssociatedObject(receiver, AccountBoundaryKey);
        objc_setAssociatedObject(receiver, AccountBoundaryKey, @(identity), OBJC_ASSOCIATION_RETAIN_NONATOMIC);
        // First assignment initializes a picker; it is not an account change.
        return previous != nil && previous.unsignedLongLongValue != identity;
    }
}
void MarufYTInstallAccountBoundaryHook(Class cls, NSString *selectorName) {
    SEL selector = NSSelectorFromString(selectorName);
    Method method = class_getInstanceMethod(cls, selector);
    if (!method) return;
    // Only hook a method actually declared by this class, once, with exactly the
    // verified void/object ABI. Inherited copies must not stack wrappers.
    unsigned count = 0; Method *methods = class_copyMethodList(cls, &count); BOOL own = NO;
    for (unsigned i = 0; i < count; ++i) if (method_getName(methods[i]) == selector) own = YES;
    free(methods); if (!own) return;
    NSMethodSignature *sig = [NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(method)];
    if (strcmp(sig.methodReturnType, @encode(void)) != 0 || sig.numberOfArguments > 4) return;
    for (NSUInteger i = 2; i < sig.numberOfArguments; ++i) if ([sig getArgumentTypeAtIndex:i][0] != '@') return;
    IMP original = method_getImplementation(method), replacement = NULL;
    if (sig.numberOfArguments == 2) {
        replacement = imp_implementationWithBlock(^(id receiver) {
            MarufYTClearRequestState(); ((void (*)(id, SEL))original)(receiver, selector);
        });
    } else if (sig.numberOfArguments == 3) {
        replacement = imp_implementationWithBlock(^(id receiver, id value) {
            if (BoundaryChanged(receiver, selectorName, value)) MarufYTClearRequestState();
            ((void (*)(id, SEL, id))original)(receiver, selector, value);
        });
    } else if (sig.numberOfArguments == 4) {
        replacement = imp_implementationWithBlock(^(id receiver, id value, id callback) {
            MarufYTClearRequestState(); ((void (*)(id, SEL, id, id))original)(receiver, selector, value, callback);
        });
    }
    if (replacement && !YTKACEInstallInstanceHook(NSStringFromClass(cls), selectorName, replacement, NULL)) imp_removeBlock(replacement);
}
void MarufYTInstallSecurityLifecycle(void) {
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            PurgeLegacyFiles();
            if ([NSUserDefaults.standardUserDefaults integerForKey:@"YTKACE.Security.LogFormatVersion"] < 2) {
                YTKACEClearDownloadLog();
                [NSUserDefaults.standardUserDefaults setInteger:2 forKey:@"YTKACE.Security.LogFormatVersion"];
            }
        });
        // Exact sign-out/picker owners are present in both supplied host binaries.
        // Optional removal variants are ABI/existence guarded. No class-list scan.
        for (NSArray<NSString *> *target in @[
            @[@"YTIdentityControllerImpl", @"signOut"],
            @[@"SSODefaultAccountListViewController", @"setSelectedIdentity:"],
            @[@"SSOService", @"removeAccount:completion:"],
            @[@"SSOServiceInternal", @"removeAccount:completion:"],
            @[@"SSOAccountServiceBase", @"removeAccountWithID:"]]) {
            Class cls = NSClassFromString(target[0]);
            if (cls) MarufYTInstallAccountBoundaryHook(cls, target[1]);
        }
    });
}
