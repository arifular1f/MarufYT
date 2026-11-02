# Runtime-security boundaries: static review

Date: 2026-11-02. Native implementation files are unchanged from the preserved `.3` release. This completes the requested static review of the outstanding boundaries; it does not certify iPhone behaviour or close every residual risk.

| Boundary | Static evidence | Disposition and limit |
| --- | --- | --- |
| Logging | `DownloadLog.mm` sends message text through three patterns before the serialized write: bearer strings, URL queries and selected `key=value` fields | Implemented coverage is narrower than arbitrary credential redaction. The Python approximation removes three synthetic values but leaves JSON token fields and cookie-header examples; log identifiers bypass the message redactor. No real credential leakage is claimed observed. Keep format coverage open for a future native fix and Foundation/device tests |
| Storage | Application Support preferred, Caches fallback, backup exclusion/file-protection attributes requested, size limit and legacy log cleanup present | File-system calls can fail and atomic replacement/protection inheritance are OS behaviours. Static intent is verified; effective permissions, backup exclusion and replacement behaviour are NOT TESTED |
| Authorized requests | Playlist code uses a fixed HTTPS Google browse endpoint, ephemeral session, disabled cookie storage and bounded pagination/timeouts | Initial destination and session configuration are verified in source. Default redirect handling is not an explicit destination allowlist. Actual cross-origin header handling and account/session lifetime are NOT TESTED |
| Sideload Keychain | Compatibility code queries/adds a non-secret marker under its own fixed account/service names, then uses the resulting access group | The reviewed marker is not a password/token store; no blanket deletion is used there. Other hooks adapt host identity/group access. Signing-dependent Google login and account switching remain NOT TESTED |
| Backup import | Stored ZIP entries only; short reads, ZIP64 fields and CRCs checked; normalized paths limited to SettingsBackup.plist or Downloads; chunked writes | The source rejects ordinary traversal and compressed entries; it is not a complete archive-parser proof. Large stored files can consume disk space; malformed input, races and resource exhaustion have not been fuzzed or tested on device |
| JavaScriptCore | Bundled solver evaluated in an app-process JSContext; reviewed code does not expose a native bridge | A JSContext is not a separate process security boundary. Parser/engine vulnerabilities and CPU/memory exhaustion are not excluded. No remote script or media was executed by this audit |
| Service privacy | SponsorBlock user identity/preferences and video-ID service requests remain as implemented; settings backups use their original key filtering | Pseudonymous identity and external-service disclosure remain documented design/privacy tradeoffs, not secretly removed features. No service request was sent in this review |
| Native media parsers | Vendored FFmpeg hashes remain unchanged; source/configuration evidence recorded separately | Dependency alerts do not determine configuration-specific CVE reachability. No vulnerability-free claim, media fuzzing or silent library upgrade |

`Tools/runtime_security_review.py` records source hashes and synthetic regex-model results. That model is explicitly not NSRegularExpression/ICU execution and is not a physical-device test. It supplements the source inspection rather than validating the whole runtime.

## Device and remediation gates

Use synthetic values to test every log input format and identifier on Foundation/iOS, inspect resulting file attributes/backup state, capture redirect behaviour without real credentials in shared logs, verify Keychain/session continuity under the actual signing identity, and fuzz malformed backup/media/protocol inputs. Google login, account switching and every player/download/customization feature remain **NOT TESTED** here.

No native feature implementation was changed in this pass because preserved packages must remain unchanged and this task calls for static review. Confirmed model gaps are recorded for a separately versioned, tested remediation; audit completion does not mean those gaps have been patched in existing binaries.
