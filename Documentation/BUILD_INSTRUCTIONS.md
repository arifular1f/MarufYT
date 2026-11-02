# Build instructions

## 1. Tweak (ROOTLESS .deb and MarufYT.dylib)

### On GitHub Actions (recommended)

Push to `phase2` or `main` (or run **Actions → Build → Run workflow**). The workflow:

1. **Tests:** runs the upstream unit tests, `Tools/marufyt_checks.py` (static and CI-hardening checks) and `Tools/marufyt_secret_scan.py` (full history).
2. **Theos:** installs the roothide fork, which upstream also uses.
   - The installer is downloaded from the commit in `THEOS_COMMIT` and must match `THEOS_INSTALLER_SHA256`.
   - Theos is then checked out at that commit.
   - The SDK and toolchain versions are written to `provenance.txt`.
3. **Build:** runs `make package FINALPACKAGE=1 THEOS_PACKAGE_SCHEME=rootless MARUFYT_BUILD=<run number>`. Any compiler error fails the step.
4. **Artifact:** uploads `MarufYT-rootless` with `com.arifular1f.marufyt_<version>_rootless.deb`, `MarufYT.dylib`, `build.log`, `provenance.txt` and `SHA256SUMS.txt`.

**Updating pins:** Dependabot proposes action updates. To move Theos, update both `THEOS_COMMIT` and `THEOS_INSTALLER_SHA256` (the hash of `bin/install-theos` at that commit), then review the CI log.

**Verifying an artifact:** run `sha256sum -c SHA256SUMS.txt` inside the extracted artifact.

### Locally (macOS or Linux with Theos)

```sh
export THEOS=~/theos   # https://theos.dev/docs/installation
python3 -m unittest discover -s Tests
python3 Tools/marufyt_checks.py
python3 Tools/marufyt_secret_scan.py
make package FINALPACKAGE=1 THEOS_PACKAGE_SCHEME=rootless
```

## 2. IPA (local only)

You supply a decrypted YouTube IPA; this repository never stores or downloads one. Branch `phase2` targets YouTube **21.43.5** (and still supports 21.39.4). Before adopting any other YouTube version, run `Tools/marufyt_host_audit.py CURRENT.ipa NEW.ipa report.md`.

```sh
python3 Tools/marufyt_package.py \
  --youtube com.google.ios.youtube_v21.43.5-decrypted.ipa \
  --deb com.arifular1f.marufyt_1.1.4+marufyt.2_rootless.deb \
  --output MarufYT-21.43.5.ipa
```

The script:

1. Removes other injected tweak load commands and files, if any (use `--remove` to name them). It also removes `AppMigrationExtension.appex`, which blocks sideloaded installs; upstream's own sideload script does the same.
2. Adds `LC_LOAD_DYLIB @rpath/MarufYT.dylib` before `LC_CODE_SIGNATURE`.
3. Copies `MarufYT.dylib` and `YTKACE.bundle` into the app.
4. Applies the upstream Info.plist changes: file sharing, open-in-place and the `audio` background mode.
5. Verifies the result.

Afterwards, sign the IPA with your own certificate.

## 3. Regenerating the vendored FFmpeg libraries (optional)

`Vendor/FFmpeg/lib/*.a` are prebuilt LGPL static libraries from upstream (FFmpeg 8.1.2, built without `--enable-gpl` or `--enable-nonfree`). CI does not rebuild them. Their SHA-256 values are recorded in `Documentation/audits/DEPENDENCY_AUDIT.md`.

To rebuild them, `Scripts/build-ffmpeg.sh` requires a verified source archive:

```sh
curl -LO https://ffmpeg.org/releases/ffmpeg-8.1.2.tar.xz
curl -LO https://ffmpeg.org/releases/ffmpeg-8.1.2.tar.xz.asc
gpg --verify ffmpeg-8.1.2.tar.xz.asc ffmpeg-8.1.2.tar.xz   # FFmpeg release signing key
FFMPEG_SHA256=$(sha256sum ffmpeg-8.1.2.tar.xz | cut -d' ' -f1) bash Scripts/build-ffmpeg.sh
```

Before running the script, place the verified archive in its build directory, or let the script download it. The script stops if the SHA-256 does not match.
