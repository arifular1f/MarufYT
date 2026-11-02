# Final Implementation Report: Phase 3

Package `com.arifular1f.marufyt` **1.1.4+marufyt.5**, branch `phase3-ui-stability` (base `9a29724`). CI run `41426058345` on `dfd1729`: tests and build succeeded.

**Completion statement.** The code, tests, CI build and packaging are complete. **On-device behaviour is NOT TESTED**, so the Phase 3 acceptance criteria about how the UI looks and feels are not confirmed. This report does not claim 100% completion.

## Stages

| Stage | Result | Commit |
| --- | --- | --- |
| 1–2 Evidence, issues, root causes | Done; `SCREEN_RECORDING_AUDIT.md` | `62c0111` |
| 3 Home, top bar, chips | "Normal Home Layout" default ON; glass presets off; tested layout math | `4588044` |
| 4 Tab bar and overlap | Default "Simple" docked bar; capsule opt-in with safe-area-independent geometry | `0fd1c91` |
| 5 Layout shifts | Idempotent, tested replacement-tab layout; no polling; on-demand snapshot | `0fd1c91`, `ee3daa9` |
| 6 Settings/effects | Only the tab picker was reworked (4 clear choices); glass defaults removed; no per-row decoration added. No broader settings redesign was done | `0fd1c91` |
| 7 Animation | `MarufYTAnimate`, Reduce Motion honoured; springs removed from four overlays. Springs remain in opt-in glass code and player screens | `ee3daa9` |
| 8 Performance | Layout timer removed, append-only log; caches reviewed. **No measurements** | `ee3daa9` |
| 9 Two hosts | Static host audit 21.39.4 → 21.43.5: 7 of 9 areas statically compatible; the two "needs update" areas (Navigation, Liquid Glass) differ by one selector each, affecting only opt-in glass modes. No version adapter needed | `dfd1729` |
| 10 Build, validate, report | Two IPAs built and verified (below) | this commit |

## Default changes you should know about

All three change what a fresh or unconfigured install looks like. Stored choices always win; nothing is rewritten.

1. Tab Bar default: **Simple** (was the MarufYT capsule). Revert: Settings → Tab Bar → MarufYT.
2. **Normal Home Layout** default ON (was off). Revert in Settings; needs a restart.
3. Glass presets (top bar, menus, notices, player) default **off**. The Liquid Glass options remain available.

You asked that Simple become the default only after compatibility and persistence were validated. Persistence and mode resolution are covered by tests; compatibility is validated **statically only**. Please confirm on device, and tell me if you want these defaults reverted.

## Release

`release/MarufYT-Phase3/` (new; earlier releases untouched). Each host folder holds the IPA, DEB, dylib, provenance, `SHA256SUMS.txt`, `VERIFICATION.txt/json`.

| Build | IPA SHA-256 | Verification |
| --- | --- | --- |
| Latest, YouTube 21.43.5 | `f64b1096d105ebbc5053757ce27465a1e5dc5b1690c48a8c65e5da8d39f10304` | 40/40 |
| Stable, YouTube 21.39.4 | `3322e10aa01b92ca06a64e391b8dcdfed24080848e2398212593cee8204621ef` | 40/40 |

- DEB `67736ff2ffbdd3f2975cf1bc7a2729ad145a69d041329e0c6a0166195faa1c65`, dylib `bec57086a9aa81d42df14bd7f19977d097d9e9a1e1ae30f00b3d214e7b0fcb96` (identical in both).
- The verifier checks: ZIP CRC, arm64 `MH_DYLIB`, install name `@rpath/MarufYT.dylib`, system-only dependencies, ROOTLESS `/var/jb` layout, bundle id and host version, Google SSO URL scheme, host sections byte-identical to the input, `LC_CODE_SIGNATURE` last, no other tweak loaded, dylib in IPA equals DEB, and every YTKACE 1.1.4 class/selector/preference still present (except documented removals).
- The IPAs are **unsigned** ("signing-required"); sign with your own certificate. The decrypted YouTube IPAs are not committed anywhere.
- The `ipa file\` inputs verified unchanged against the pre-Phase-3 checksums.

## Preserved

All MarufYT features, Google sign-in/account switching URL scheme, upstream attribution and licenses. No dependency added. `main`, `phase2`, `stable-21.39.4` and `optimization/phase2-performance` were not modified or promoted.

## Open items

- Device test of both builds (`DEVICE_TEST_RESULTS.md`).
- The delayed shift on 21.43.5 is unproven and unreproduced; use the layout snapshot to capture it.
- Remaining springs in opt-in glass and player code; mini-player 0.35 s tick.
- Translations of the two new strings are machine-assisted, not native-reviewed.
- No performance or battery numbers exist.
