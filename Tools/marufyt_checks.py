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


# 1. Branding identity is exact and verified.
branding = read("Tweak/MarufYT/MarufYTBranding.mm")
for literal in ['@"MarufYT"', '@"arifular1f"', '@"https://github.com/arifular1f/MarufYT"',
                '@"https://github.com/arifular1f"', '@"https://github.com/itzzace/ytkace"']:
    check(f"branding constant {literal}", literal in branding)

# 2. Every Tweak source is compiled, and every compiled file exists.
makefile = read("Makefile")
listed = set(re.findall(r"^\t(Tweak/\S+\.mm)", makefile, re.M))
present = {p.relative_to(ROOT).as_posix() for p in TWEAK.rglob("*.mm")}
check("Makefile lists every Tweak/*.mm", present <= listed, ", ".join(sorted(present - listed)))
check("Makefile entries exist", listed <= present, ", ".join(sorted(listed - present)))
check("library renamed to MarufYT", "LIBRARY_NAME = MarufYT" in makefile and "@rpath/MarufYT.dylib" in makefile)

# 3. No user-facing upstream product literal left in UI code.
# Allowed: internal identifiers (keys, reuse ids, notifications, file prefixes, bundle name).
ui_literal = re.compile(r'@"YTKACE"')
internal_uses = ("pathForResource", "URLByAppendingPathComponent", "stringByAppendingPathComponent",
                 "hasPrefix:@\"YTKACE\"", "MarufYTUpstreamName = ")
offenders = []
for path in TWEAK.rglob("*.mm"):
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if ui_literal.search(line) and not any(use in line for use in internal_uses):
            offenders.append(f"{path.relative_to(ROOT).as_posix()}:{number}")
check('no bare @"YTKACE" UI literals', not offenders, ", ".join(offenders))
check("no upstream repository button", "github.com/itzzace/ytkace" not in
      "".join(p.read_text(encoding="utf-8") for p in (TWEAK / "Settings").rglob("*.mm")))

# 4. Settings persistence: preference namespace unchanged.
keys = set()
for path in TWEAK.rglob("*.mm"):
    keys.update(re.findall(r'"(YTKACE\.Preference\.[A-Za-z0-9.]+)"', path.read_text(encoding="utf-8")))
check("preference keys keep YTKACE.Preference namespace", len(keys) > 100, f"{len(keys)} keys")
check("no MarufYT.Preference keys (backups only export YTKACE.Preference.*)",
      not any('"MarufYT.Preference.' in p.read_text(encoding="utf-8") for p in TWEAK.rglob("*.mm")))

# 5. Own-view detection accepts both prefixes.
nav = read("Tweak/Features/Interface/NavigationVisibility.mm")
check("navigation own-view check uses MarufYTIsOwnAccessibilityText",
      "MarufYTIsOwnAccessibilityText(view.accessibilityLabel)" in nav)

# 6. Glass integration hooks are wired.
tab = read("Tweak/Features/Navigation/TabBarHooks.mm")
check("capsule depth attached", "MarufYTDecorateTabCapsule(receiver, glass);" in tab)
check("capsule depth excluded from fade loop", "MarufYTIsDecorationView(sibling)" in tab)
check("capsule depth removed with glass", "MarufYTRemoveTabCapsuleDecoration(receiver);" in tab)
check("glass constructor honours preset", "MarufYTGlassPreferenceEnabled(key)" in tab)
check("preset merged into defaults", "registerDefaults:MarufYTPreferenceDefaults()" in read("Tweak/Runtime/Preferences.mm"))

# 7. New module code: balanced @interface/@implementation/@end and no direct swizzling.
for path in (TWEAK / "MarufYT").glob("*.mm"):
    text = path.read_text(encoding="utf-8")
    opens = len(re.findall(r"^@(interface|implementation)\b", text, re.M))
    ends = len(re.findall(r"^@end\b", text, re.M))
    check(f"{path.name}: @interface/@implementation balanced", opens == ends, f"{opens} vs {ends}")
    check(f"{path.name}: no direct method swizzling",
          "method_setImplementation" not in text and "method_exchangeImplementations" not in text)
    check(f"{path.name}: MIT header", "Copyright (c) 2026 arifular1f" in text)

# 8. Licences and workflows.
license_text = read("LICENSE")
check("LICENSE keeps upstream copyright", "Copyright (c) 2026 YTKACE contributors" in license_text)
check("LICENSE adds MarufYT copyright", "arifular1f" in license_text)
notices = read("THIRD_PARTY_NOTICES.md")
check("THIRD_PARTY_NOTICES credits YTKACE and FFmpeg", "YTKACE" in notices and "FFmpeg" in notices)
workflows = "".join(p.read_text(encoding="utf-8") for p in (ROOT / ".github/workflows").glob("*.yml"))
check("workflows never download or publish a YouTube IPA",
      "dropbox" not in workflows.lower() and ".ipa" not in workflows.lower())

# 9. Package metadata.
control = read("control")
check("control identity", "Package: com.arifular1f.marufyt" in control and "Author: arifular1f" in control)
check("control conflicts with upstream package", "Conflicts: com.itzzace.ytkace" in control)
check("filter plist targets YouTube only", read("MarufYT.plist").count("com.google.ios.youtube") == 1)

print(f"\n{'FAILED' if failures else 'OK'}: {len(failures)} failure(s)")
sys.exit(1 if failures else 0)
