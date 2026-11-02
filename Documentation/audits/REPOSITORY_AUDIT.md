# Repository audit: MarufYT

Date: 2026-11-02.

## Identity and ownership

| Item | Value |
| --- | --- |
| Repository | https://github.com/arifular1f/MarufYT (public, MIT) |
| Maintainer | `arifular1f`, the only collaborator (admin) |
| Description | "MarufYT — YouTube enhancement for iOS by arifular1f: ad blocking, SponsorBlock, downloads, background playback and a native Liquid Glass design. ROOTLESS. Based on YTKACE (MIT)." |
| Topics | ios, ios-tweak, liquid-glass, marufyt, objective-c, rootless, sponsorblock, theos, tweak, youtube |
| Commit identity (MarufYT commits) | `arifular1f <332575442+arifular1f@users.noreply.github.com>` with a `Co-Authored-By: Claude` trailer |

## Branches

| Branch | Head | Purpose |
| --- | --- | --- |
| `main` | `aac6947` | Previous release 1.1.1+marufyt.1 (unchanged; **not promoted**) |
| `stable-21.39.4` | `aac6947` | Frozen stable source |
| `phase2` | current | Phase 2 and security work (1.1.4+marufyt.3) |

All three are protected against deletion and force-push by the ruleset *Protect release branches*. There are no tags or GitHub releases. Artifacts are produced by Actions and assembled locally.

## History and attribution

- **Upstream authorship preserved:** the history contains the full upstream YTKACE history (170+ commits). There has been no rebase or rewrite of upstream commits, no change of author, and no force-push.
- **MarufYT commits:** made on top of the upstream history. Each is authored by `arifular1f`.
- **`LICENSE`:** keeps "Copyright (c) 2026 YTKACE contributors" and adds the MarufYT line.
- **`THIRD_PARTY_NOTICES.md`:** keeps every upstream notice. A header identifies MarufYT as a modified YTKACE.
- **Provenance:** `Documentation/SOURCE_PROVENANCE.md` separates new, modified and unchanged upstream files.
- **Removed:** `.github/FUNDING.yml` (a Sponsor button that funded the upstream author from this repository). Credit and donation links remain in `UPSTREAM_README.md`.

## Contents check

| Check | Result |
| --- | --- |
| Credentials, keys, certificates, provisioning profiles | None (full-history scan) |
| YouTube / Google binaries or IPAs | None in any commit (scan and `.gitignore`: `*.ipa`, `*.deb`, `*.zip`) |
| Large binaries | Only the vendored FFmpeg static libraries (5.6 MB total, LGPL) and upstream screenshots |
| Workflows | One: `build.yml` (tests, checks, secret scan, ROOTLESS build). Upstream's IPA-download and Pages workflows were removed |
| Community files | README, LICENSE, THIRD_PARTY_NOTICES, SECURITY, PRIVACY, CHANGELOG, issue templates (branded), dependabot.yml |
