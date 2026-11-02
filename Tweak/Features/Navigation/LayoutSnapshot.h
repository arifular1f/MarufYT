#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

// One-shot layout report written to the diagnostics log. It runs only when the
// user asks for it (long-press the About "Version" row); nothing observes or
// repairs layout in the background.
FOUNDATION_EXPORT void YTKACELogLayoutSnapshot(void);

NS_ASSUME_NONNULL_END
