# Compatibility

Current update: `1.1.4+marufyt.8`, branch `final-update-security`, based on Phase 4.1 `657aed1`. See [release evidence](../Documentation/FINAL_UPDATE/FINAL_UPDATE_REPORT.md).

## Supported YouTube versions

| YouTube | Role | Minimum iOS (host) | Notes |
| --- | --- | --- | --- |
| 21.43.5 | Latest | 17.0 | Has the native floating tab bar (`YTFloatingPivotBarView`) and a per-item label-hiding option |
| 21.39.4 | Stable | 17.0 | Older floating-bar hooks; no `YTFloatingPivotBarView` |

Both are checked statically by `Tools/marufyt_host_audit.py` (class and selector names for every hook target) and assembled and verified by the release tooling. The static audit of 21.39.4 → 21.43.5 found 7 of 9 hook areas unchanged; the Navigation and Liquid Glass areas differ by one selector each and affect only the optional glass tab bars. Name presence is not proof of runtime behaviour; the tweak also checks method type encodings at runtime.

## The tweak

- ROOTLESS, arm64, deployment target iOS 15.0. The injected library is `@rpath/MarufYT.dylib`.
- Liquid Glass options need iOS 26 or later; the default Simple tab bar works on every supported iOS.
- No runtime injection environment is needed: the library is added to the IPA, which you sign yourself.

## YouTube updates

YouTube's internal classes are private and change without notice. Hooks resolve classes and selectors at runtime and skip missing names; this is not a guarantee of runtime stability or correct private API behavior. Other YouTube versions are untested; run the host audit before trying one.

## Architectures

arm64 only. The supported YouTube executables are thin arm64.

## Install paths

The unsigned IPA can be signed and installed with any sideloading approach that re-signs the app with your own certificate. Signing and installation results on a device are not covered by this repository's automated tests.

## Security compatibility boundaries

Remote tasks created by MarufYT require HTTPS with a host, no URL userinfo and the standard TLS port. Generic cross-origin redirects omit sensitive/unrecognized headers and reject body replay; SABR POST redirects remain within `googlevideo.com` / its subdomains and use an explicit header allowlist. Google/YouTube sessions belonging to the original host are not globally hooked. Local media import/playback is separate from remote fetch policy and remains supported.

Authenticated seeds are no longer restored across launches. Native playback must refresh in-memory stream state when needed; a download after account change/expiry can require retry. Download-button preferences do not control all native capture hooks. Account-boundary methods are wrapped only when their runtime ABI matches; login/account switching, actual logout coverage and downloads after migration require device testing on EACH host. No target iPhone runtime pass is claimed.
