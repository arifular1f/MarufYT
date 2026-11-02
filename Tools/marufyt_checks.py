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
check("Theos installer pinned and hash-verified",
      "THEOS_INSTALLER_SHA256" in workflows and "sha256sum -c" in workflows and "theos/master" not in workflows)
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

print(f"\n{'FAILED' if failures else 'OK'}: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
