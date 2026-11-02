# Device and host compatibility

Target supplied by user: iPhone 15 Pro Max / iPhone16,2, iOS 27.2. Those identity
and OS details are user-reported, not independently queried from a connected device.

| Environment | Static/build evidence | Physical result |
| --- | --- | --- |
| YouTube 21.43.5 Latest | Separate source host audit, package verification and original-section comparison | NOT TESTED after optimization |
| YouTube 21.39.4 Stable | Separate source host audit, package verification and original-section comparison | NOT TESTED after optimization |
| iPhone 15 Pro Max / Dynamic Island | Host bounds/safe-area layout; no device-specific coordinates introduced | NOT TESTED |
| Smaller and standard iPhones | Native icon/label anchors and intrinsic fallback | NOT TESTED |
| Landscape, asymmetric safe area, window sizes | Capsule width/center now derive from host bar safe area, not screen short side | NOT TESTED |
| Dynamic Type | Existing host fonts/native label bounds retained, intrinsic line-height fallback | NOT TESTED |
| Glass-capable OS | Runtime class guards retained, lightweight accessibility path | NOT TESTED |
| Earlier supported OS | Existing runtime availability guards and deployment target retained | NOT TESTED |

The static host comparison finds one selector lost in Latest:
`YTPivotBarView liquidGlassEffectForPageStyle:`; and one gained:
`YTFloatingPivotBarView setRenderer:`. Existing hook installation checks for
class/method existence, and the page-style effect hook additionally checks method
types. This is evidence of a real host difference, not proof of visual regression
or proof that every fallback works. Eleven listed targets are missing in both
host static inventories (including optional/system-framework fallbacks).
The audit reports global selector/class-name presence, not method ownership or
dynamic execution. Its NEEDS UPDATE label remains a runtime investigation item.

Both hosts retain their own Info.plist configuration: Latest has scene-related
metadata that Stable does not. No app-scene or Google session configuration was
rewritten. Top-left logo, top-right controls, settings/About/library alignment,
label clipping, hit targets and selected states need recording/device validation.
The missing recording is `ScreenRecording_11-02-2026 4-14-02 PM_1.mp4`; user authorized
continuing the source audit without it. No visual findings have been invented.
