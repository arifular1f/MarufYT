#import "MediaArtwork.h"

#import <AVFoundation/AVFoundation.h>

NSData *YTKACEMediaArtworkData(NSURL *URL) {
    NSURL *base = URL.URLByDeletingPathExtension;
    for (NSString *extension in @[@"jpg", @"png"]) {
        NSData *data = [NSData dataWithContentsOfURL:
            [base URLByAppendingPathExtension:extension]];
        if (data.length != 0) return data;
    }
    AVURLAsset *asset = [AVURLAsset URLAssetWithURL:URL options:nil];
    NSArray<AVMetadataItem *> *items = [AVMetadataItem
        metadataItemsFromArray:asset.commonMetadata
        filteredByIdentifier:AVMetadataCommonIdentifierArtwork];
    id value = items.firstObject.value;
    if ([value isKindOfClass:NSData.class]) return value;
    if ([value respondsToSelector:@selector(dataValue)]) return [value dataValue];
    return nil;
}

// Bounded: at most 8 images and about 16 MB; a missing artwork is remembered
// too so tracks without art are not probed on every refresh.
static NSCache<NSString *, id> *YTKACEArtworkCache(void) {
    static NSCache *cache;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        cache = [NSCache new];
        cache.countLimit = 8;
        cache.totalCostLimit = 16 * 1024 * 1024;
    });
    return cache;
}

static NSString *YTKACEArtworkKey(NSURL *URL) {
    NSDate *modified = nil;
    [URL getResourceValue:&modified forKey:NSURLContentModificationDateKey error:nil];
    return [NSString stringWithFormat:@"%@|%.0f", URL.path, modified.timeIntervalSince1970];
}

UIImage *YTKACEMediaArtworkCachedImage(NSURL *URL) {
    if (URL == nil) return nil;
    id cached = [YTKACEArtworkCache() objectForKey:YTKACEArtworkKey(URL)];
    return [cached isKindOfClass:UIImage.class] ? cached : nil;
}

UIImage *YTKACEMediaArtworkImage(NSURL *URL) {
    if (URL == nil) return nil;
    NSString *key = YTKACEArtworkKey(URL);
    NSCache *cache = YTKACEArtworkCache();
    id cached = [cache objectForKey:key];
    if (cached != nil) return [cached isKindOfClass:UIImage.class] ? cached : nil;
    NSData *data = YTKACEMediaArtworkData(URL);
    UIImage *image = data.length == 0 ? nil : [UIImage imageWithData:data];
    NSUInteger cost = (NSUInteger)(image.size.width * image.size.height * image.scale * image.scale * 4.0);
    [cache setObject:image ?: (id)NSNull.null forKey:key cost:image == nil ? 0 : cost];
    return image;
}

void YTKACEMediaArtworkImageAsync(NSURL *URL, void (^completion)(UIImage *image)) {
    if (URL == nil || completion == nil) return;
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
        UIImage *image = YTKACEMediaArtworkImage(URL);
        dispatch_async(dispatch_get_main_queue(), ^{ completion(image); });
    });
}
