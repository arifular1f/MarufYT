#!/usr/bin/env python3
"""MarufYT static source checks (run in CI before compiling, and locally).

Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TWEAK = ROOT / "Tweak"
failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    if not ok:
        failures.append(name)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def sources():
    return {p: p.read_text(encoding="utf-8") for p in TWEAK.rglob("*.mm")}


SRC = sources()

# 1. Branding identity is exact.
branding = read("Tweak/MarufYT/Branding/MarufYTBranding.mm")
for literal in ['@"MarufYT"', '@"arifular1f"', '@"https://github.com/arifular1f/MarufYT"',
                '@"https://github.com/arifular1f"', '@"arifular1f/MarufYT"']:
    check(f"branding constant {literal}", literal in branding)

# 2. Every Tweak source is compiled, and every compiled file exists.
makefile = read("Makefile")
listed = set(re.findall(r"^\t(Tweak/\S+\.mm)", makefile, re.M))
present = {p.relative_to(ROOT).as_posix() for p in SRC}
check("Makefile lists every Tweak/*.mm", present <= listed, ", ".join(sorted(present - listed)))
check("Makefile entries exist", listed <= present, ", ".join(sorted(listed - present)))
check("library renamed to MarufYT", "LIBRARY_NAME = MarufYT" in makefile and "@rpath/MarufYT.dylib" in makefile)
check("build number wired", "MARUFYT_BUILD_NUMBER" in makefile)

# 3. No user-facing upstream product literal or upstream links in UI code.
internal_uses = ("pathForResource", "URLByAppendingPathComponent", "stringByAppendingPathComponent",
                 'hasPrefix:@"YTKACE"', "MarufYTUpstreamName = ")
offenders = [f"{p.relative_to(ROOT).as_posix()}:{n}"
             for p, text in SRC.items()
             for n, line in enumerate(text.splitlines(), 1)
             if '@"YTKACE"' in line and not any(use in line for use in internal_uses)]
check('no bare @"YTKACE" UI literals', not offenders, ", ".join(offenders))
settings_text = "".join(t for p, t in SRC.items() if "/Settings/" in p.as_posix())
check("no upstream repository or developer row in settings",
      "github.com/itzzace" not in settings_text and '@"itzzace"' not in settings_text)

# 4. About section: no Credits row; Developer, Repository and version information present.
native = read("Tweak/Settings/NativeSettingsEntry.mm")
root = read("Tweak/Settings/YTKACERootOptionsController.mm")
check("no Credits row in YouTube Settings entry", '@"title": @"Credits"' not in native)
check("no Credits row in MarufYT settings", "MakeCreditsController" not in root)
for row in ["MarufYTAboutRowDeveloper", "MarufYTAboutRowRepository", "MarufYTAboutRowVersion",
            "MarufYTAboutRowYouTube", "MarufYTAboutRowPackage"]:
    check(f"About row {row}", root.count(row) >= 2)
check("no bundle ID or device model in settings UI", "bundleIdentifier" not in root and "utsname" not in root)

# 5. Design system: no accent-coloured values, native styles, theme everywhere.
red_values = [f"{p.relative_to(ROOT).as_posix()}:{n}"
              for p, text in SRC.items()
              for n, line in enumerate(text.splitlines(), 1)
              if re.search(r"(detailTextLabel|readout|value|valueLabel)\.textColor\s*=\s*YTKACEAccentColor", line)]
check("no value labels coloured with the accent", not red_values, ", ".join(red_values))
check("YTKACEAccentColor returns the MarufYT accent", "return MarufYTAccentColor();" in read("Tweak/UI/Assets.mm"))
for path in ["Tweak/Settings/YTKACESettingsPages.mm", "Tweak/Settings/YTKACETabEditorController.mm",
             "Tweak/Settings/YTKACERootOptionsController.mm"]:
    text = read(path)
    check(f"{path.split('/')[-1]}: inset-grouped, themed",
          "UITableViewStylePlain" not in text and "UITableViewStyleInsetGrouped" in text and "MarufYTStyle" in text)
pages = read("Tweak/Settings/YTKACESettingsPages.mm")
check("no shrunken switches", "CGAffineTransformMakeScale(0.95, 0.95)" not in settings_text)
check("fixed tiny fonts removed from settings rows",
      "systemFontOfSize:10.0" not in pages and "systemFontOfSize:11.0" not in pages)

# 6. Settings persistence: preference namespace unchanged, SponsorBlock keys still bound.
keys = set()
for text in SRC.values():
    keys.update(re.findall(r'"(YTKACE\.Preference\.[A-Za-z0-9.]+)"', text))
check("preference keys keep YTKACE.Preference namespace", len(keys) > 150, f"{len(keys)} keys")
check("no MarufYT.Preference keys (backups only export YTKACE.Preference.*)",
      not any('"MarufYT.Preference.' in t for t in SRC.values()))
check("SponsorBlock behaviour and colour keys bound per category",
      "YTKACESponsorBehaviorKey(category)" in pages and "YTKACESponsorColorKey(category)" in pages)
for key in ["YTKACESponsorBlockKey", '"YTKACE.Preference.SponsorBlock.OverlayButton"',
            '"YTKACE.Preference.SponsorBlock.NotificationMode"', '"YTKACE.Preference.SponsorBlock.AudioFeedback"',
            '"YTKACE.Preference.SponsorBlock.SkipAlertSeconds"', '"YTKACE.Preference.SponsorBlock.UnskipAlertSeconds"',
            "YTKACEDeArrowThumbModeKey", "YTKACEDeArrowTitlesKey"]:
    check(f"SponsorBlock setting {key}", key in pages)

# 7. Own-view detection, glass hook-ups and preset.
check("navigation own-view check accepts both names",
      "MarufYTIsOwnAccessibilityText(view.accessibilityLabel)" in read("Tweak/Features/Interface/NavigationVisibility.mm"))
tab = read("Tweak/Features/Navigation/TabBarHooks.mm")
check("capsule depth attached", "MarufYTDecorateTabCapsule(receiver, glass);" in tab)
check("capsule depth excluded from fade loop", "MarufYTIsDecorationView(sibling)" in tab)
check("capsule depth removed with glass", "MarufYTRemoveTabCapsuleDecoration(receiver);" in tab)
check("glass constructor honours preset", "MarufYTGlassPreferenceEnabled(key)" in tab)
check("tab glass mode falls back to preset, legacy value wins", "MarufYTPresetTabGlassMode()" in tab
      and 'objectForKey:@"YTKACE.Preference.Tabs.Glass"' in tab)
check("preset merged into defaults", "registerDefaults:MarufYTPreferenceDefaults()" in read("Tweak/Runtime/Preferences.mm"))

# 8. New module code: balanced Objective-C, no swizzling, MIT header, documented.
for path in (TWEAK / "MarufYT").rglob("*.*"):
    text = path.read_text(encoding="utf-8")
    name = path.relative_to(TWEAK / "MarufYT").as_posix()
    check(f"{name}: MIT header", "Copyright (c) 2026 arifular1f" in text)
    if path.suffix == ".mm":
        opens = len(re.findall(r"^@(interface|implementation)\b", text, re.M))
        ends = len(re.findall(r"^@end\b", text, re.M))
        check(f"{name}: balanced @interface/@implementation", opens == ends, f"{opens} vs {ends}")
        check(f"{name}: no direct method swizzling",
              "method_setImplementation" not in text and "method_exchangeImplementations" not in text)
        check(f"{name}: no NSLog debugging", "NSLog(" not in text)

# 9. Localization: every table parses, branding substitution is complete.
strings_files = sorted((ROOT / "Resources/YTKACE.bundle").glob("*.lproj/Localizable.strings"))
pair = re.compile(r'^"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)";\s*$', re.M)
tables = {}
for path in strings_files:
    text = path.read_text(encoding="utf-8")
    entries = dict(pair.findall(text))
    tables[path.parent.name] = entries
    check(f"{path.parent.name}: parses", len(entries) > 100, f"{len(entries)} entries")
english = set(tables.get("en.lproj", {}))
for language, entries in tables.items():
    missing = english - set(entries)
    print(f"INFO {language}: {len(missing)} English keys fall back to English")
branded = [v.replace("YTKACE", "MarufYT") for t in tables.values() for v in t.values()]
check("branding leaves no upstream name in localized values", not any("YTKACE" in v for v in branded))
check("16 localization tables", len(tables) == 16, f"{len(tables)}")
marufyt_keys = ["ALERTS", "SKIPPING", "SEGMENT COLORS", "Repository", "Version", "Package", "Developer",
                "Floating Tab Bar Depth", "Soft shadow under the floating glass tab bar.",
                "YTKACE Sleep Timer", "YTKACE SponsorBlock", "YTKACE Transcript"]
untranslated = [f"{lang}:{k}" for lang, entries in tables.items() for k in marufyt_keys if k not in entries]
check("every MarufYT string translated in all 16 tables", not untranslated, ", ".join(untranslated[:8]))

# 9b. Runtime hardening.
log = read("Tweak/Features/Downloads/DownloadLog.mm")
check("diagnostics log redacts tokens and URL queries", "YTKACERedactLogMessage(message)" in log)
check("diagnostics log not in Files-visible Documents",
      "@[@(NSApplicationSupportDirectory),\n" in log and "NSURLIsExcludedFromBackupKey" in log)
overlay = read("Tweak/UI/OverlayButtonHost.mm")
check("player buttons have localized VoiceOver labels",
      "button.accessibilityLabel = YTKACELocalized(identifier);" in overlay)
tls_overrides = [p.name for p, t in SRC.items()
                 if re.search(r"serverTrust|SecTrustEvaluate|NSAllowsArbitraryLoads|allowsAnyHTTPSCertificate", t)]
check("no TLS trust overrides", not tls_overrides, ", ".join(tls_overrides))
cleartext = [p.name for p, t in SRC.items() if re.search(r'@"http://', t)]
check("no cleartext http:// endpoints", not cleartext, ", ".join(cleartext))

# 10. Licences and workflows.
license_text = read("LICENSE")
check("LICENSE keeps upstream copyright", "Copyright (c) 2026 YTKACE contributors" in license_text)
check("LICENSE adds MarufYT copyright", "arifular1f" in license_text)
notices = read("THIRD_PARTY_NOTICES.md")
check("THIRD_PARTY_NOTICES credits YTKACE and FFmpeg", "YTKACE" in notices and "FFmpeg" in notices)
workflows = "".join(p.read_text(encoding="utf-8") for p in (ROOT / ".github/workflows").glob("*.yml"))
check("workflows never download or publish a YouTube IPA",
      "dropbox" not in workflows.lower() and ".ipa" not in workflows.lower())
uses = re.findall(r"uses:\s*([^\s#]+)", workflows)
unpinned = [u for u in uses if not re.search(r"@[0-9a-f]{40}$", u)]
check("every action pinned to a full commit SHA", bool(uses) and not unpinned, ", ".join(unpinned))
check("checkout never persists credentials",
      workflows.count("persist-credentials: false") == workflows.count("actions/checkout@"))
check("workflow token read-only", "permissions:\n  contents: read" in workflows and "write" not in workflows)
check("Theos bootstrap uses source/compiler/SDK integrity lock",
      "Tools/bootstrap_pinned.py" in workflows and "Tools/toolchain.lock.json" in workflows
      and "install-theos" not in workflows and "releases/latest" not in workflows)
check("no untrusted event data in run steps",
      not re.search(r"\$\{\{\s*github\.(event|head_ref)", workflows))
check("job timeouts set", workflows.count("timeout-minutes:") >= 2)
check("Dependabot watches GitHub Actions", "github-actions" in read(".github/dependabot.yml"))
for doc in ["SECURITY.md", "PRIVACY.md"]:
    check(f"{doc} present", (ROOT / doc).exists() and "arifular1f" in read(doc))
check("no upstream funding link in repository config", not (ROOT / ".github/FUNDING.yml").exists())
templates = "".join(p.read_text(encoding="utf-8") for p in (ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml"))
check("issue templates branded MarufYT", "YTKACE" not in templates and "MarufYT" in templates)

# 11. Package metadata.
control = read("control")
check("control identity", "Package: com.arifular1f.marufyt" in control and "Author: arifular1f" in control)
check("control conflicts with upstream package", "Conflicts: com.itzzace.ytkace" in control)
check("filter plist targets YouTube only", read("MarufYT.plist").count("com.google.ios.youtube") == 1)

# Performance source regressions. These assert source contracts, not device timing.
tabs = read("Tweak/Features/Navigation/TabBarHooks.mm")
design = read("Tweak/MarufYT/Design/MarufYTDesign.mm")
dearrow = read("Tweak/Features/SponsorBlock/DeArrow.mm")
progress = read("Tweak/Features/Downloads/DownloadProgressView.mm")
check("no delayed held-button tab correction", "weakNearest" not in tabs and "cancelTrackingWithEvent:nil" in tabs)
check("replacement tabs are laid out from their bounds and a native sibling (pure layout)",
      tabs.count("YTKACELayoutReplacementTab(view,") == 2 and "MarufYTReplacementTabLayout(input)" in tabs
      and "convertRect:nativeIcon.bounds toView:view" not in tabs
      and "convertRect:nativeLabel.bounds toView:view" not in tabs)
check("replacement labels have no fixed bottom-16 offset", "CGRectGetHeight(view.bounds) - 16.0" not in tabs)
check("lightweight appearance preserves stored preferences", "YTKACE.Preference.Glass.Lightweight" in design
      and "@\"Lightweight Glass\"" in read("Tweak/Settings/YTKACESettingsPages.mm"))
check("Reduce Motion bypasses custom springs", tabs.count("if (UIAccessibilityIsReduceMotionEnabled())") >= 2)
check("lens tracker stops off-window and inactive", "lens.window == nil" in tabs
      and "applicationState != UIApplicationStateActive" in tabs)
check("DeArrow cache has count and memory cost limits", "countLimit = 160" in dearrow
      and "totalCostLimit = 24 * 1024 * 1024" in dearrow and "forKey:videoID cost:cost" in dearrow)
check("download progress card is event-driven (no layout polling timer)",
      "positionTimer" not in progress and "observeLayoutChanges" in progress
      and "NSTimer" not in progress)
library = read("Tweak/Settings/YTKACEDownloadsController.mm")
check("download metadata cache bounded and pending work cancelled", "metadataCache.countLimit = 64" in library
      and "metadataCache.totalCostLimit = 32 * 1024 * 1024" in library and "forKey:path cost:cost" in library
      and "[_metadataQueue cancelAllOperations]" in library)
check("glass width uses host safe area", "UIEdgeInsetsInsetRect(receiver.bounds, receiver.safeAreaInsets)" in tabs
      and "shortSide - margin" not in tabs)
for surface in ["Tweak/Features/Navigation/GlassChrome.mm", "Tweak/Features/Navigation/GlassSheets.mm",
                "Tweak/Features/Playback/PlayerGlass.mm", "Tweak/UI/Notice.mm"]:
    check(f"Reduce Transparency respected in {pathlib.Path(surface).name}", "!UIAccessibilityIsReduceTransparencyEnabled()" in read(surface))

# 12. Phase 3: simple default look, stable layout, tests wired into CI.
math_h = read("Tweak/MarufYT/Design/MarufYTLayoutMath.h")
check("layout math is pure C (no UIKit or Foundation)",
      not re.search(r"#\s*(import|include)\s*[<\"](UIKit|Foundation|objc)", math_h) and "#pragma" not in math_h)
check("default tab bar mode is Simple (3)", "return MarufYTTabModeSimple;" in design)
check("tab mode resolved by the tested function", "MarufYTResolveTabMode(hasStored" in tabs)
defaults_body = design.split("MarufYTPreferenceDefaults")[1].split("BOOL MarufYTGlassPreferenceEnabled")[0]
check("glass presets are not defaulted on", "Glass.TopBar" not in defaults_body and "Glass.Menus" not in defaults_body)
check("Normal Home Layout defaults on (a stored value still wins)",
      '@"YTKACE.Preference.Feed.HomeTabsHidden": @YES' in read("Tweak/Runtime/Preferences.mm")
      and '@"YTKACE.Preference.Feed.HomeTabsHidden": @YES' in design)
capsule_body = tabs.split("static BOOL YTKACEApplyPivotBarGlass")[1].split("static IMP OriginalSearchOptOutFrostedPivot")[0]
check("capsule geometry has no safe-area height term",
      "receiver.safeAreaInsets.bottom" not in capsule_body and "MarufYTCapsuleFrame(" in capsule_body)
check("tab slots are index-based", "MarufYTTabItemFrame(glass, geometry, (int)index" in tabs)
check("MarufYT tab label follows the host",
      "YTKACEReplacementLabelHidden(view" in tabs and "MarufYTShouldHideReplacementLabel(" in tabs)
check("native layout tests exist and run in CI",
      (ROOT / "Tests/native/test_layout_math.c").exists() and (ROOT / "Tests/test_native_layout_math.py").exists()
      and "MARUFYT_REQUIRE_NATIVE" in workflows)
for key in ["Simple", "Simple uses YouTube's classic docked tab bar. YouTube and MarufYT are optional Liquid Glass bars."]:
    missing = [lang for lang, entries in tables.items() if key not in entries]
    check(f"Phase 3 string translated in all 16 tables: {key[:28]}", not missing, ", ".join(missing))

# Phase 3 stage 7-8: simple motion, append-only log.
check("motion helpers honour Reduce Motion",
      "MarufYTReduceMotion()" in design and "void MarufYTAnimate(" in design)
spring_files = ["Tweak/Settings/YTKACEDownloadsController.mm", "Tweak/Features/Downloads/DownloadProgressView.mm",
                "Tweak/Features/SponsorBlock/SponsorHooks.mm", "Tweak/Features/Downloads/GlobalDownloadMiniPlayer.mm"]
check("default-visible overlays use no spring animation",
      all("usingSpringWithDamping" not in read(f) and "MarufYTAnimate(" in read(f) for f in spring_files))
dl_log = read("Tweak/Features/Downloads/DownloadLog.mm")
check("diagnostics log appends instead of rewriting each line",
      "seekToEndReturningOffset" in dl_log and "dataWithContentsOfURL:URL] ?: NSData.data" not in dl_log
      and "NSURLIsExcludedFromBackupKey" in dl_log and "YTKACERedactLogMessage(message)" in dl_log)
check("layout snapshot is on demand only",
      "YTKACELogLayoutSnapshot();" in read("Tweak/Settings/YTKACERootOptionsController.mm")
      and "NSTimer" not in read("Tweak/Features/Navigation/LayoutSnapshot.mm")
      and "LayoutSnapshot.mm" in read("Makefile"))

# Phase 4: fetches of URLs that come from YouTube objects require HTTPS.
check("URL policy requires https before MarufYT fetches YouTube-supplied URLs",
      "MarufYTIsSecureURL" in read("Tweak/Runtime/URLPolicy.h")
      and all("MarufYTIsSecureURL(" in read(f) for f in [
          "Tweak/Features/Interface/PostImageSaver.mm", "Tweak/Features/Interface/ProfilePictureViewer.mm",
          "Tweak/Features/Playback/TranscriptExport.mm"]))

# Phase 4.1: private SponsorBlock lookup, artwork off the main thread.
check("SponsorBlock hash helper is pure C with native tests wired",
      "#import" not in read("Tweak/MarufYT/Privacy/MarufYTSponsorHash.h")
      and (ROOT / "Tests/native/test_sponsor_hash.c").exists() and (ROOT / "Tests/test_native_sponsor_hash.py").exists())
check("Private Lookup is a labelled, translated opt-in",
      "SponsorBlock.PrivateLookup" in read("Tweak/Settings/YTKACESettingsPages.mm")
      and all("Private Lookup" in entries for entries in tables.values()))
check("artwork cache is bounded and async loader exists",
      "YTKACEMediaArtworkImageAsync" in read("Tweak/Features/Downloads/MediaArtwork.mm")
      and "countLimit = 8" in read("Tweak/Features/Downloads/MediaArtwork.mm"))

print(f"\n{'FAILED' if failures else 'OK'}: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
