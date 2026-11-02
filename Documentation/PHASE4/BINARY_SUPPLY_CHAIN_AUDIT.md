# Binary and Supply-Chain Audit (Phase 4)

Subject: CI run `41432137516` on `236102f` (package `1.1.4+marufyt.6`) and the IPAs in `release/MarufYT-Phase4/`.

## Artifacts

| File | SHA-256 |
| --- | --- |
| `MarufYT.dylib` | `59ba874c7ede7e45fc2ed8b4f67f35f4b11b9a98acf0f014104eb77597966b5d` |
| `com.arifular1f.marufyt_1.1.4+marufyt.6_rootless.deb` | `8c87fd0e3bb5c9852783151d20e077b0b2b4c1a116c659bbcfd4f9dede0a74e6` |
| IPA, YouTube 21.43.5 | `b924d05f891164ad6868784fe1613ecfe75fe2230d619cef906546f7fdb75dec` |
| IPA, YouTube 21.39.4 | `f5a18804a56678843fc3c8cc1770af986b11cb02411e49fb1428d1311a586747` |

## Verified (automated, `FreeBuild/tools/verify_release.py`, 40/40 per IPA)

- ZIP CRC; arm64 `MH_DYLIB`; install name `@rpath/MarufYT.dylib`; dependencies are system libraries only (no Substrate).
- DEB layout is ROOTLESS (`/var/jb/...`); DEB dylib equals CI dylib; dylib in each IPA equals the DEB dylib.
- Host executable: all sections byte-identical to the input, length unchanged, `MarufYT.dylib` the only non-system load command, `LC_CODE_SIGNATURE` last.
- Bundle ID `com.google.ios.youtube`, correct host version, Google SSO URL scheme present.
- Every class, selector and preference key of YTKACE 1.1.4 is still present except documented removals.
- No other tweak is loaded; no executable scripts in the IPAs; all other files byte-identical to the input apart from documented removals.
- The four `ipa file/` inputs still match the pre-Phase-2 checksums.

## Build provenance

CI build log has **0 compiler warnings** (warnings are errors). `provenance.txt` and `toolchain-provenance.json` record Theos commit `3ac89c9…`, SDK `iPhoneOS16.5`, and the LLVM 11.1.0 toolchain. The Phase 2.1 dependency audit (`Documentation/audits/DEPENDENCY_AUDIT.md`, `TRANSITIVE_TOOLCHAIN_LOCK.md`) pins the installer by SHA-256. Workflow: `permissions: contents: read`, every action pinned to a full commit SHA (`checkout` v6.1.0, `cache` v4.3.0, `upload-artifact` v7.0.2), credentials not persisted, no secrets used, no Python packages.

## Dependencies

| Component | Status |
| --- | --- |
| FFmpeg 8.1.2 static libraries (LGPL, no GPL/nonfree flags) | Hashes recorded in `DEPENDENCY_AUDIT.md`; source and relink evidence kept in `FFMPEG_SOURCE_AND_RELINK.md`. Not rebuilt or re-hashed in Phase 4 |
| yt-dlp EJS solver 0.8.0 | Pinned hashes in `DEPENDENCY_AUDIT.md`. Not re-audited |
| Debug functionality | None beyond the local diagnostics log. No debug symbols check was run (**Not tested**) |
| Duplicate / unused libraries | Not found in the IPAs; the Phase 3 packager already drops `CydiaSubstrate` and the other bundled tweaks |

## Not done / limits

- Code signatures: the IPAs are unsigned by design; the host's stale `_CodeSignature` is replaced when you sign. **Not tested.**
- No independent reproducible-build check (a second CI build is not byte-compared).
- Runner image and Theos installer are pinned but come from third parties (`roothide/theos`, GitHub-hosted runners).
- No secrets, certificates or provisioning profiles are in the repository or releases (full-history scan: 0 findings). YouTube IPAs are never committed (`.gitignore` blocks `*.ipa`).
