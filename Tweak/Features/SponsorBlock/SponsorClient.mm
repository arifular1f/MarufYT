#import "../../Runtime/URLPolicy.h"
#import "SponsorClient.h"
#import "SponsorPreferences.h"
#import "../../MarufYT/Privacy/MarufYTSponsorHash.h"
#import "../../Runtime/Preferences.h"
#import <math.h>

// Opt-in. When on, only the first 4 hex characters of SHA-256(videoID) are sent
// (GET /api/skipSegments/<prefix>) and the matching video is picked from the
// response. Off by default: the response is larger and the path is not yet
// verified on a device.
static NSString * const YTKACESponsorPrivateLookupKey = @"YTKACE.Preference.SponsorBlock.PrivateLookup";

@interface YTKACESponsorClient ()
@property(nonatomic, strong) NSCache<NSString *, NSArray *> *cache;
@property(nonatomic, strong) NSURLSession *session;
@end

@implementation YTKACESponsorClient

+ (instancetype)sharedClient {
    static YTKACESponsorClient *client;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        client = [YTKACESponsorClient new];
    });
    return client;
}

- (instancetype)init {
    self = [super init];
    if (self) {
        _cache = [NSCache new];
        _cache.countLimit = 128;

        NSURLSessionConfiguration *configuration =
            NSURLSessionConfiguration.ephemeralSessionConfiguration;
        configuration.timeoutIntervalForRequest = 10.0;
        configuration.timeoutIntervalForResource = 15.0;
        configuration.requestCachePolicy = NSURLRequestReloadIgnoringLocalCacheData;
        _session = MarufYTMakeSecureSession(configuration);
    }
    return self;
}

- (void)segmentsForVideoID:(NSString *)videoID
                completion:(YTKACESponsorCompletion)completion {
    if (videoID.length == 0) {
        completion(@[]);
        return;
    }

    [self segmentsForVideoID:videoID categories:YTKACESponsorEnabledCategories()
                  completion:completion];
}

- (void)segmentsForVideoID:(NSString *)videoID
                categories:(NSArray<NSString *> *)categories
                completion:(YTKACESponsorCompletion)completion {
    if (videoID.length == 0 || categories.count == 0) {
        completion(@[]);
        return;
    }
    NSString *cacheKey = [NSString stringWithFormat:@"%@|%@", videoID,
                          [categories componentsJoinedByString:@","]];

    NSArray *cached = [self.cache objectForKey:cacheKey];
    if (cached != nil) {
        completion(cached);
        return;
    }

    BOOL privateLookup = YTKACEFeatureEnabled(YTKACESponsorPrivateLookupKey);
    NSString *endpoint = @"https://sponsor.ajay.app/api/skipSegments";
    if (privateLookup) {
        char prefix[MARUFYT_SPONSOR_PREFIX_LENGTH + 1];
        if (!MarufYTSponsorHashPrefix(videoID.UTF8String, MARUFYT_SPONSOR_PREFIX_LENGTH, prefix, sizeof prefix)) {
            // Not a well-formed video ID: send nothing rather than the full ID.
            completion(@[]);
            return;
        }
        endpoint = [endpoint stringByAppendingFormat:@"/%s", prefix];
    }
    NSURLComponents *components = [NSURLComponents componentsWithString:endpoint];
    NSData *categoryData = [NSJSONSerialization dataWithJSONObject:categories
                                                            options:0 error:nil];
    NSString *categoryJSON = categoryData == nil ? @"[]" :
        [[NSString alloc] initWithData:categoryData encoding:NSUTF8StringEncoding];
    NSURLQueryItem *categoryItem = [NSURLQueryItem queryItemWithName:@"categories" value:categoryJSON];
    components.queryItems = privateLookup
        ? @[categoryItem]
        : @[[NSURLQueryItem queryItemWithName:@"videoID" value:videoID], categoryItem];
    NSURL *url = components.URL;
    if (url == nil) {
        completion(@[]);
        return;
    }

    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url];
    request.HTTPMethod = @"GET";
    [request setValue:@"application/json" forHTTPHeaderField:@"Accept"];

    __weak YTKACESponsorClient *weakSelf = self;
    NSURLSessionDataTask *task =
        [self.session dataTaskWithRequest:request
                       completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        NSMutableArray<NSDictionary<NSString *, id> *> *segments =
            [NSMutableArray array];
        NSHTTPURLResponse *http =
            [response isKindOfClass:NSHTTPURLResponse.class]
                ? (NSHTTPURLResponse *)response
                : nil;

        if (error == nil && http.statusCode == 200 && data.length <= 1024 * 1024) {
            id json = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
            NSArray *entries = [json isKindOfClass:NSArray.class] ? json : nil;
            if (privateLookup) {
                // The reply lists every video sharing the prefix; keep only ours.
                entries = nil;
                for (id candidate in (NSArray *)([json isKindOfClass:NSArray.class] ? json : @[])) {
                    id candidateID = [candidate isKindOfClass:NSDictionary.class] ? candidate[@"videoID"] : nil;
                    id candidateSegments = [candidate isKindOfClass:NSDictionary.class] ? candidate[@"segments"] : nil;
                    if ([candidateID isKindOfClass:NSString.class] && [candidateSegments isKindOfClass:NSArray.class] &&
                        MarufYTSponsorEntryMatches(videoID.UTF8String, [candidateID UTF8String])) {
                        entries = candidateSegments;
                        break;
                    }
                }
            }
            if (entries != nil) {
                for (id item in entries) {
                    if (![item isKindOfClass:NSDictionary.class]) {
                        continue;
                    }
                    id category = item[@"category"];
                    id values = item[@"segment"];
                    id actionType = item[@"actionType"];
                    if (![category isKindOfClass:NSString.class] ||
                        ![categories containsObject:category] ||
                        ([actionType isKindOfClass:NSString.class] &&
                         ![actionType isEqualToString:@"skip"]) ||
                        ![values isKindOfClass:NSArray.class] ||
                        [values count] != 2) {
                        continue;
                    }
                    id startValue = values[0];
                    id endValue = values[1];
                    if (![startValue isKindOfClass:NSNumber.class] ||
                        ![endValue isKindOfClass:NSNumber.class]) {
                        continue;
                    }
                    double start = [startValue doubleValue];
                    double end = [endValue doubleValue];
                    if (!isfinite(start) || !isfinite(end) || start < 0.0 || end <= start) {
                        continue;
                    }
                    id uuid = item[@"UUID"];
                    [segments addObject:@{@"start": @(start), @"end": @(end),
                                          @"category": category,
                                          @"uuid": [uuid isKindOfClass:NSString.class] ? uuid : @""}];
                }
            }
        }

        NSArray *result = [segments sortedArrayUsingComparator:
            ^NSComparisonResult(NSDictionary *left, NSDictionary *right) {
                return [left[@"start"] compare:right[@"start"]];
            }];
        if (result.count != 0) {
            [weakSelf.cache setObject:result forKey:cacheKey];
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            completion(result);
        });
    }];
    [task resume];
}

@end
