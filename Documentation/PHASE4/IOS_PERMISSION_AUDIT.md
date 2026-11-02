# iOS Permission Audit (Phase 4)

Inspected the real `Info.plist` of both Phase 3 IPAs and of the original input IPAs. The IPAs are unsigned, so there is **no embedded provisioning profile or entitlement blob to inspect**; entitlements are decided by whoever signs the IPA. **Entitlements: Not tested.**

## What MarufYT changes in the host Info.plist (`Tools/marufyt_package.py`)

| Key | Original (21.43.5 / 21.39.4) | Phase 3 IPA | Why | Necessary? |
| --- | --- | --- | --- | --- |
| `UIFileSharingEnabled` | absent | true | Downloads in `Documents/YTKACE` visible in Files | Yes for the library; privacy trade-off documented |
| `LSSupportsOpeningDocumentsInPlace` | absent | true | Same | Yes |
| `UIBackgroundModes` includes `audio` | already present | unchanged | Background audio | Yes (host already has it) |
| `UIDesignRequiresCompatibility` | true / absent | true in both | The 21.39.4 input lacked it because YTLite removed it; the packager restores the stock value. MarufYT removes it at runtime only if a glass mode is chosen | Yes |
| `NSFaceIDUsageDescription` | absent / present | removed when YTLite was present | Undoes YTLite's edit | n/a |

No usage description is added. The nine that exist (Camera, Contacts, Location, Microphone, Music, Photos, Bluetooth, LocalNetwork, UserTracking) belong to YouTube and are identical to the original IPA. MarufYT itself calls only `PHPhotoLibrary` (add-only, on a user save). It has no code for location, contacts, camera, microphone or tracking (symbols absent from the dylib).

## Other items

| Item | Finding |
| --- | --- |
| URL schemes | Identical to the original: Google SSO scheme, `youtube`, `vnd.youtube*`, `gsd-*`. MarufYT registers none |
| ATS | The host's own exceptions (several telecom domains allow insecure HTTP; `NSAllowsLocalNetworking`). Unchanged by MarufYT and not MarufYT's configuration |
| App extensions | Removed by the packager: 21.43.5 `AppMigrationExtension`; 21.39.4 `OpenYoutubeSafariExtension`. The other 21.43.5 extensions (Intents, NotificationContent, NotificationService, Share, WidgetKit) are YouTube's and are kept. Whether they work after signing with a free account is **Not tested** |
| Frameworks | `CydiaSubstrate.framework` removed from 21.39.4 (ROOTLESS). Only `widevine_cdm_secured_ios.framework` and `MarufYT.dylib` remain |
| Executable scripts | None in either IPA |
| Keychain / app groups | `SideloadCompatibility.mm` adapts the sign-in keychain group for sideloaded installs; nothing else is altered |
| Code signing | The IPAs keep the host's original `_CodeSignature` data, which is invalid after modification and must be replaced when signing. **Signing result: Not tested** |

## Conclusion

MarufYT added no unnecessary permission. The only privilege expansion is Files exposure of the downloads folder. Sign-in, account switching, downloads, background audio and PiP depend on the retained keys, so nothing further was removed.
