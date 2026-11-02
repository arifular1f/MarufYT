#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

FOUNDATION_EXPORT NSData * _Nullable YTKACEMediaArtworkData(NSURL *URL);
FOUNDATION_EXPORT UIImage * _Nullable YTKACEMediaArtworkImage(NSURL *URL);
// Cache lookup only; never touches the disk. Returns nil when not loaded yet.
FOUNDATION_EXPORT UIImage * _Nullable YTKACEMediaArtworkCachedImage(NSURL *URL);
// Loads off the main thread (bounded cache) and calls back on the main thread.
FOUNDATION_EXPORT void YTKACEMediaArtworkImageAsync(NSURL *URL, void (^completion)(UIImage * _Nullable image));

NS_ASSUME_NONNULL_END
