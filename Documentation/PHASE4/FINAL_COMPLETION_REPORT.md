# Final Completion Report (Phase 4)

Branch `phase4-security-privacy` (base `0cebe48`, the verified Phase 3 head). Package `1.1.4+marufyt.6`. Protected branches (`main`, `phase2`, `stable-21.39.4`, `optimization/phase2-performance`, `phase3-ui-stability`) were not modified. Earlier releases and the `ipa file/` inputs are unchanged (checksums re-verified).

You reported that the latest build installed and works. That is recorded as your report; this project has no logs or captures from the device for it.

## Outcome by objective

| Objective | Status |
| --- | --- |
| 1 Security audit | **Done (static)**: `SECURITY_AUDIT.md`. 1 low finding fixed, 1 privacy item awaiting your decision, 2 items need investigation, memory safety not tested |
| 2 Privacy / data flow | **Done (static)**: `PRIVACY_DATA_FLOW_AUDIT.md`. Dynamic network capture **not done**, so "zero data" is not claimed |
| 3 Binary / dependency audit | **Done**: `BINARY_SUPPLY_CHAIN_AUDIT.md`; 40/40 checks per IPA. Signing and reproducibility not tested |
| 4 Permissions | **Done**: `IOS_PERMISSION_AUDIT.md`. No unnecessary permission added by MarufYT; entitlements not testable on unsigned IPAs |
| 5 Performance | **Reviewed only**: `PERFORMANCE_REPORT.md`. No measurements; no new tuning |
| 6 UI / settings polish | **Not done in Phase 4.** The simple native look from Phase 3 stands; no new UI work was made without a device to check it |
| 7 GitHub redesign | **Done on the branch**: README, compatibility doc, docs layout, changelog. Becomes visible on `main` only after a merge you approve |
| 8 Cleanup | **Done conservatively**: `REPOSITORY_CLEANUP_REPORT.md`. No secrets or binaries found; nine historical reports moved; unreferenced-source review not completed |
| 9 Release | `release/MarufYT-Phase4/` (Latest 21.43.5 and Stable 21.39.4), 40/40 each |

## Fixed

- S-01: YouTube-supplied image/caption URLs are only fetched over HTTPS.

## Needs your decision or more work

1. **SponsorBlock hash-prefix lookup** (S-02): more private, but changes the request/response handling and needs a device test.
2. **Dynamic network capture** with a test account (proxy such as mitmproxy on a test device).
3. **Main-thread blocking** in four network helpers (S-10) and **observer duplication** (30 add vs 6 remove): trace callers.
4. **Merge to `main`**: needed for GitHub's folder dates and default README.
5. **Screenshots**: take MarufYT screenshots (Simple look) for the README.
6. `docs/FEATURE_MATRIX.md` and `web/index.html` still carry upstream wording.

## Release

| Build | IPA SHA-256 |
| --- | --- |
| Latest, YouTube 21.43.5 | `b924d05f891164ad6868784fe1613ecfe75fe2230d619cef906546f7fdb75dec` |
| Stable, YouTube 21.39.4 | `f5a18804a56678843fc3c8cc1770af986b11cb02411e49fb1428d1311a586747` |

DEB `8c87fd0e…0a74e6`, dylib `59ba874c…966b5d` (full values in `BINARY_SUPPLY_CHAIN_AUDIT.md`). IPAs are unsigned and local only; they are not in the repository.

## What this does not claim

That the app is completely secure, that it collects zero data, that any measured performance improved, or that any feature was re-tested on a device.
