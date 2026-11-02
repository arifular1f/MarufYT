// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
#import <Foundation/Foundation.h>
FOUNDATION_EXPORT void MarufYTInstallSecurityLifecycle(void);
FOUNDATION_EXPORT void MarufYTClearRequestState(void);
FOUNDATION_EXPORT void MarufYTExpireRequestStateIfNeeded(void);
FOUNDATION_EXPORT void MarufYTNoteRequestActivity(void);
FOUNDATION_EXPORT NSUInteger MarufYTSecurityGeneration(void);
FOUNDATION_EXPORT void YTKACEClearCapturedRequests(void);
FOUNDATION_EXPORT void YTKACESABRClearRequestState(void);
FOUNDATION_EXPORT void YTKACEClearPlaylistAuthorization(void);
FOUNDATION_EXPORT void MarufYTPurgeLegacyRequestFiles(NSURL *root);
