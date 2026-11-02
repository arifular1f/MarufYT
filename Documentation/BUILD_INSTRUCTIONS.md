# Build instructions

## 1. Tweak (ROOTLESS .deb and MarufYT.dylib)

### On GitHub Actions (recommended)

Push to `main`, or run **Actions → Build → Run workflow**. The workflow:

1. Runs the upstream unit tests and `Tools/marufyt_checks.py`.
2. Installs Theos (the roothide fork, as upstream uses).
3. Runs `make package FINALPACKAGE=1 THEOS_PACKAGE_SCHEME=rootless`.
4. Uploads the artifact `MarufYT-rootless`. It contains `com.arifular1f.marufyt_<version>_rootless.deb`, `MarufYT.dylib`, `build.log` and `SHA256SUMS.txt`.

### Locally (macOS or Linux with Theos)

```sh
export THEOS=~/theos   # https://theos.dev/docs/installation
python3 -m unittest discover -s Tests
python3 Tools/marufyt_checks.py
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
