#import "DownloadLog.h"



static const NSUInteger YTKACEDownloadLogLimit = 512 * 1024;

static NSURL *YTKACEDownloadLogURL(void) {
    static NSURL *cached = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        // MarufYT security: Application Support first. Documents is exposed in
        // the Files app (UIFileSharingEnabled) and is included in backups.
        NSArray<NSNumber *> *candidates = @[@(NSApplicationSupportDirectory),
                                            @(NSCachesDirectory)];
        for (NSNumber *candidate in candidates) {
            NSURL *base = [NSFileManager.defaultManager
                URLsForDirectory:(NSSearchPathDirectory)candidate.unsignedIntegerValue
                       inDomains:NSUserDomainMask].firstObject;
            if (base == nil) continue;
            NSURL *directory = [[base URLByAppendingPathComponent:@"YTKACE" isDirectory:YES]
                URLByAppendingPathComponent:@"Logs" isDirectory:YES];
            NSError *error = nil;
            if (![NSFileManager.defaultManager createDirectoryAtURL:directory
                                       withIntermediateDirectories:YES
                                                        attributes:@{NSFileProtectionKey:
                                                            NSFileProtectionCompleteUntilFirstUserAuthentication}
                                                             error:&error]) {
                continue;
            }
            [directory setResourceValue:@YES forKey:NSURLIsExcludedFromBackupKey error:nil];
            NSURL *probe = [directory URLByAppendingPathComponent:@"downloads.log"];
            if (![NSFileManager.defaultManager fileExistsAtPath:probe.path] &&
                ![[NSData data] writeToURL:probe atomically:YES]) {
                continue;
            }
            cached = probe;
            break;
        }
        if (cached == nil) {
            cached = [NSURL fileURLWithPath:
                [NSTemporaryDirectory() stringByAppendingPathComponent:@"ytkace-downloads.log"]];
        }
        [NSUserDefaults.standardUserDefaults setObject:cached.path
                                                forKey:@"YTKACELogPath"];
        // Remove the diagnostics log older builds kept in Documents (visible in Files).
        // Only this log file is touched; downloads in Documents/YTKACE are not.
        NSURL *documents = [NSFileManager.defaultManager URLsForDirectory:NSDocumentDirectory
                                                                inDomains:NSUserDomainMask].firstObject;
        NSURL *legacy = [documents URLByAppendingPathComponent:@"YTKACE/Logs/downloads.log"];
        if (legacy != nil && ![legacy isEqual:cached]) {
            [NSFileManager.defaultManager removeItemAtURL:legacy error:nil];
        }
    });
    return cached;
}

static dispatch_queue_t YTKACEDownloadLogQueue(void) {
    static dispatch_queue_t queue;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        queue = dispatch_queue_create("com.ytkace.download-log", DISPATCH_QUEUE_SERIAL);
    });
    return queue;
}

static NSString * const YTKACEDebugLogsKey = @"YTKACE.Preference.Developer.DebugLogs";

BOOL YTKACEDebugLogsEnabled(void) {
    return [NSUserDefaults.standardUserDefaults boolForKey:YTKACEDebugLogsKey];
}

void YTKACESetDebugLogsEnabled(BOOL enabled) {
    [NSUserDefaults.standardUserDefaults setBool:enabled forKey:YTKACEDebugLogsKey];
}

static void YTKACEWriteLogLine(NSString *identifier, NSString *message);

void YTKACEDownloadLog(NSString *identifier, NSString *format, ...) {
    if (format.length == 0 || !YTKACEDebugLogsEnabled()) return;
    // Keep an event template, never interpolate opaque objects, raw payloads or C strings.
    if ([format containsString:@"%@"] || [format containsString:@"%s"] || [format containsString:@"%p"]) {
        YTKACEWriteLogLine(identifier, format);
        return;
    }
    va_list arguments;
    va_start(arguments, format);
    NSString *message = [[NSString alloc] initWithFormat:format arguments:arguments];
    va_end(arguments);
    YTKACEWriteLogLine(identifier, message);
}

void YTKACEDebugLog(NSString *identifier, NSString *format, ...) {
    if (format.length == 0 || !YTKACEDebugLogsEnabled()) return;
    // Keep an event template, never interpolate opaque objects, raw payloads or C strings.
    if ([format containsString:@"%@"] || [format containsString:@"%s"] || [format containsString:@"%p"]) {
        YTKACEWriteLogLine(identifier, format);
        return;
    }
    va_list arguments;
    va_start(arguments, format);
    NSString *message = [[NSString alloc] initWithFormat:format arguments:arguments];
    va_end(arguments);
    YTKACEWriteLogLine(identifier, message);
}

// MarufYT security: never persist bearer tokens, URL query strings (stream
// signatures, keys, client IPs) or token-like parameters, even in debug logs.
NSString *YTKACERedactLogMessage(NSString *message) {
    // Do not try to extract arbitrary secrets out of server JSON/headers.
    NSString *lower = message.lowercaseString;
    for (NSString *marker in @[@"authorization", @"bearer", @"cookie", @"token", @"password", @"secret", @"api_key", @"api-key", @"apikey", @"signature", @"session=", @"key=", @"pot=", @"{", @"}", @"response=", @"body=", @"/var/", @"/private/", @"/users/"]) {
        if ([lower containsString:marker]) return @"[sensitive diagnostic omitted]";
    }
    static NSArray<NSRegularExpression *> *patterns;
    static NSArray<NSString *> *templates;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        patterns = @[
            [NSRegularExpression regularExpressionWithPattern:@"https?://[^\\s]+" options:NSRegularExpressionCaseInsensitive error:nil],
            [NSRegularExpression regularExpressionWithPattern:@"[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}" options:NSRegularExpressionCaseInsensitive error:nil],
            [NSRegularExpression regularExpressionWithPattern:@"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{11}(?![A-Za-z0-9_-])" options:0 error:nil]
        ];
        templates = @[@"[URL omitted]", @"[email omitted]", @"[identifier omitted]"];
    });
    NSMutableString *redacted = [message mutableCopy];
    for (NSUInteger i = 0; i < patterns.count; ++i) {
        [patterns[i] replaceMatchesInString:redacted options:0 range:NSMakeRange(0, redacted.length) withTemplate:templates[i]];
    }
    [redacted replaceOccurrencesOfString:@"\n" withString:@" " options:0 range:NSMakeRange(0, redacted.length)];
    [redacted replaceOccurrencesOfString:@"\r" withString:@" " options:0 range:NSMakeRange(0, redacted.length)];
    return redacted;
}

static void YTKACEWriteLogLine(NSString *identifier, NSString *message) {
    message = YTKACERedactLogMessage(message);
    if (message.length > 4096) message = [message substringToIndex:4096];
    if (identifier.length == 0 || [identifier rangeOfCharacterFromSet:NSCharacterSet.lowercaseLetterCharacterSet.invertedSet].location != NSNotFound) identifier = @"download";
    NSString *line = [NSString stringWithFormat:@"%@ [%@] %@\n",
        NSDate.date, identifier.length == 0 ? @"download" : identifier, message];
    dispatch_async(YTKACEDownloadLogQueue(), ^{
        if (!YTKACEDebugLogsEnabled()) return;
        NSURL *URL = YTKACEDownloadLogURL();
        // Append only; the file is rewritten (trimmed) once it passes the limit.
        NSData *bytes = [line dataUsingEncoding:NSUTF8StringEncoding];
        NSFileHandle *handle = [NSFileHandle fileHandleForWritingToURL:URL error:nil];
        if (handle == nil) {
            [bytes writeToURL:URL atomically:YES];
            return;
        }
        unsigned long long size = 0;
        [handle seekToEndReturningOffset:&size error:nil];
        [handle writeData:bytes error:nil];
        [handle closeAndReturnError:nil];
        if (size + bytes.length > YTKACEDownloadLogLimit) {
            NSMutableData *data = [[NSData dataWithContentsOfURL:URL] mutableCopy];
            NSUInteger keep = YTKACEDownloadLogLimit * 3 / 4;
            if (data.length > keep) {
                [[data subdataWithRange:NSMakeRange(data.length - keep, keep)]
                    writeToURL:URL atomically:YES];
            }
        }
    });
}

NSString *YTKACEDownloadLogContents(void) {
    __block NSString *contents = @"No download activity yet.";
    dispatch_sync(YTKACEDownloadLogQueue(), ^{
        NSString *value = [NSString stringWithContentsOfURL:YTKACEDownloadLogURL()
            encoding:NSUTF8StringEncoding error:nil];
        if (value.length != 0) contents = value;
    });
    return contents;
}

void YTKACEClearDownloadLog(void) {
    dispatch_sync(YTKACEDownloadLogQueue(), ^{
        [NSFileManager.defaultManager removeItemAtURL:YTKACEDownloadLogURL() error:nil];
    });
}
