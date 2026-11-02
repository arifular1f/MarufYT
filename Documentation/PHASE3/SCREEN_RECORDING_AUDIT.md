# Phase 3 — Screen recording audit (Stage 1 and 2 baseline)

Date: 2026-11-02. Branch: `phase3-ui-stability` (from `9a29724`).

## 1. Evidence actually inspected

| Item | How it was inspected |
| --- | --- |
| `reference/IMG_2949.MP4` | Opened and decoded (576×1280, 29.7 fps, 132.4 s, matches "2 min 12 s"). Frames were extracted at **4-second intervals over the whole clip** (33 frames). The 56–66 s section was also extracted at **1-second intervals**, and the tab-bar strip was **cropped and enlarged at 4, 20–26, 60, 62, 70, 76, 90 and 100 s**. The extractor ran in an isolated virtual environment; the video was never modified |
| `reference/photo_1_2026-11-02_17-31-57.jpg` | Viewed. Chips layout (compass, All, New to you, Music, Mixes, Apple…) with the red markings around the header and the bottom bar |
| `reference/photo_2_2026-11-02_17-31-57.jpg` | Viewed. Text-tab layout (Home, Subs, Music, Live, More) with the same markings |

**Build identification.** Settings → About in the clip shows `1.1.4+marufyt.4 (12)` on both builds: YouTube **21.39.4** (0:36–0:48) and **21.43.5** (1:20). The home screen at 0:00 shows two separately installed YouTube apps, so each build has its **own preferences sandbox**.

**What the clip does not show.**

- It never captures a layout *changing by itself over time*. In the 21.43.5 Home segment (1:00–1:16) the header, tab row and tab bar are identical across frames. The "becomes misaligned after some time" report is therefore **not reproduced by this clip**; the clip shows the misaligned state, not the transition.
- Per-frame animation timing cannot be measured at 4-second sampling.

**Privacy.** From 1:36 the recording leaves YouTube and shows WhatsApp and Facebook (chat lists, phone numbers, names). Those frames are the user's *design references* (see V-13). They were looked at only to understand the target look. **No frame of the recording is stored in this repository.**

## 2. Timeline

| Time | Build | Screen |
| --- | --- | --- |
| 0:00 | — | iPhone home screen with two YouTube apps |
| 0:04–0:06, 0:16–0:26 | 21.39.4 | Home feed (chips, large thumbnail, Shorts shelf) |
| 0:08–0:12 | 21.39.4 | Shorts opened from the **Shorts tab** (Shorts selected) |
| 0:28–0:34, 0:52 | 21.39.4 | A Short opened from the **Home shelf** (Home stays selected, correct) |
| 0:36 | 21.39.4 | MarufYT settings (own controller) |
| 0:40 | 21.39.4 | MarufYT tab: download library, empty state |
| 0:44–0:48 | 21.39.4 | MarufYT entry in YouTube Settings (YouTube's own row style); YouTube About |
| 0:56–0:58 | 21.43.5 | App launch transition, then You page loading |
| 0:59 | 21.43.5 | Library list |
| 1:00–1:16 | 21.43.5 | Home feed (text-tab row), scrolling |
| 1:08–1:12 | 21.43.5 | MarufYT tab, empty state |
| 1:20 | 21.43.5 | MarufYT settings → About (shows 21.43.5) |
| 1:24 | 21.43.5 | YouTube Settings |
| 1:28 | 21.43.5 | You page |
| 1:32 | 21.43.5 | Shorts |
| 1:36–2:12 | other apps | WhatsApp, Facebook, home screen (design references) |

## 3. Part A: what is visible (observations only)

| ID | Time (build) | Screen | Visible problem | Component | Status |
| --- | --- | --- | --- | --- | --- |
| V-01 | 0:04, 0:20–0:26 (21.39.4); 1:00–1:16 (21.43.5); photo 1, photo 2 | Home | The floating tab bar is almost fully transparent. Feed content (Shorts cards, channel/like row, text such as "Shahbandar Beach", "HONOR X9D") shows **sharp** through it, behind the icons and labels, so labels are hard to read. In photo 1 the bar covers the channel row and its action buttons. The bar's colour also takes on the colour behind it (red at 0:20–0:24) | Bottom tab bar | **Confirmed** (visual) |
| V-02 | 0:20–0:25 (21.39.4); 70 s (21.43.5) | Tab bar, switching tabs | The moving selection "lens" has a refraction edge with rainbow fringes (strong at 22 s and 24 s) and passes through several intermediate shapes. At 24.0 s the Subscriptions icon is already filled while the pill is still over Shorts | Tab selection indicator | **Confirmed** (visual) |
| V-03 | 4 s, 20–26 s (21.39.4) | Tab bar | The **MarufYT tab's label sits about 10 px higher than the other labels and overlaps its own icon** in every frame. Home, Shorts, Subscriptions and You share one baseline | MarufYT tab item | **Confirmed** (visual) |
| V-04 | 60, 62, 76 s, photo 2 (21.43.5) | Tab bar | The **native labels (Home, Shorts, Subscriptions, You) are not shown, but the MarufYT label is.** Home, Shorts and You icons are vertically centred, while the **Subscriptions and MarufYT icons are about 25 px higher**. The red badge dot also sits off the Subscriptions icon. This differs from 21.39.4, where all five labels show on one baseline | Tab bar items | **Confirmed** (visual). Cause: see S-03, S-04 |
| V-05 | 1:00–1:16, photo 2 (21.43.5) | Home top | Instead of filter chips, Home shows a **text tab row** ("Home, Subs, Music, Live, More"). On 21.39.4 the same account shows chips with a compass icon (photo 1, 0:04). The two builds present different category navigation | Home header | **Confirmed** (visual). Cause: see S-05 |
| V-06 | 0:04, 0:24 (21.39.4); 1:00 (21.43.5); photos 1 and 2 | Home | The first video thumbnail starts directly against the bottom edge of the chip row or text-tab row, with no gap. At 1:03 (scrolled) the card title sits immediately under the pinned tab row | Home feed spacing | Seen; **needs device investigation** (host layout or MarufYT) |
| V-07 | All frames of both builds | Top bar | The bell and search buttons sit inside one rounded **glass pill** | Top bar | **Confirmed** (visual). Cause: see S-02 |
| V-08 | photo 2; 1:00 (21.43.5) | Home | In photo 2 the first "Mix" thumbnail is black (image not loaded yet or failed). In the clip, thumbnails that load do so without moving the layout | Home feed | No layout shift from image loading seen |
| V-09 | 0:36 vs 0:44 (21.39.4) | MarufYT settings | The same menu appears in two styles: inset-grouped cards with coloured tiles (own controller) and flat YouTube-style rows (YouTube Settings entry). This is two entry points with two renderers | Settings | Expected, by design |
| V-10 | 0:36 (21.39.4) | MarufYT settings root | The search field is a glass pill; rows have different heights because descriptions wrap onto two lines | Settings | Seen |
| V-11 | 1:28 (21.43.5) | You page | "View channel" and "Get Premium" are cut off under the header, because the page is scrolled under the translucent header | Host page | Normal host behaviour |
| V-12 | 0:56–0:58 (21.43.5) | App launch | The app window has rounded corners and scales | iOS app-open animation | Normal iOS behaviour |
| V-13 | 1:36–2:12 | WhatsApp, Facebook | **The user's design reference.** WhatsApp's tab bar: icons **and labels on one baseline**, a **solid dark capsule**, a **solid** selected pill. Facebook's: icon-only, a solid dark capsule, a solid pill. Neither shows content through the bar, and there is no lens or refraction | Reference | Target look |
| V-14 | 1:32 (21.43.5) | Shorts | The tab bar here is a solid dark capsule, and Shorts content ends above it. Home (0:04) is the only place content passes behind a see-through bar | Shorts | No overlap |

## 4. Part B: what the source shows (for build 9a29724)

| ID | Finding | Location | Status |
| --- | --- | --- | --- |
| S-01 | The MarufYT capsule **hides YouTube's own blur** (`blur.hidden = YES`) and draws a clear `UIGlassEffect`. There is no opaque or blurred base, so the feed shows through | `TabBarHooks.mm` `YTKACEApplyPivotBarGlass` (~3393) | Confirmed by reading |
| S-02 | When any glass preference is on, a load-time constructor removes **`UIDesignRequiresCompatibility`** from the app's Info dictionary. YouTube is then rendered in the **full iOS 26 Liquid Glass design** (system glass bar buttons, the pill in V-07). The Phase 2 preset turned four glass preferences on by default for everybody on iOS 26+ | `TabBarHooks.mm:1565`; `MarufYTDesign.mm` preset | Confirmed by reading |
| S-03 | The MarufYT tab (and any "extra" tab) is laid out by `YTKACELayoutReplacementTab`, which positions MarufYT's icon and label from the frames of the **native** label and icon *after MarufYT has blanked and hidden them*. The host re-lays those views out, so the anchors move. The result depends on the order and timing of host layout passes: not idempotent | `TabBarHooks.mm:913`, `YTKACEApplyDownloadIcon` (~995), `YTKACEApplyExtraTabIcon` (~1156) | Confirmed by reading. It matches V-03; the run-time effect is not observed |
| S-04 | MarufYT's replacement label hides only when **its own** `Tabs.LabelsHidden` preference is on. 21.43.5 adds a native **`hideLabel` item property** and an **icon-only tab-item** experiment (`iosEnableIconOnlyPivotBarItemTapEvents`, `enableFoxPivotBarSpacing`; none of these names exist in 21.39.4). When the host hides labels, MarufYT's label still shows. `YTKACETabLabelsHidden` syncs `hideLabel` only for items inside `YTFloatingPivotBarView` | `TabBarHooks.mm:718`; host name diff | Plausible and consistent with V-04. **Whether the 21.43.5 install had the preference on, or the host hid the labels, needs a device check** (each install has its own preferences) |
| S-05 | The Home text-tab row is YouTube's server-driven **"tabbed Home redesign" (Fox)**. MarufYT already has the setting **Normal Home Layout** (`Feed.HomeTabsHidden`), which forces the experiment flags off. Its targets exist in **both** hosts: `YTColdConfig …ScrollableTabsInFox`, `…CollapsingTabsAfterDwellInFox`, `YTTabsViewController`. **The default is off** | `HomeTabs.mm`; `Preferences.mm:123`; `YTKACESettingsPages.mm` | Confirmed by reading and host audit |
| S-06 | Remote-config flags (`YTColdConfig`, "cold" config) are applied at **launch**. A flag delivered after the first runs changes the layout on a later launch. This is consistent with "looks right after installing, changes after a while", but **no run-time evidence yet** | Host behaviour; S-04, S-05 | Hypothesis; needs device confirmation |
| S-07 | The selection indicator uses `_UILiquidLensView` plus a chain of 9 `dispatch_after` blocks, one `CADisplayLink` and 9 spring animations in the tab-bar file. These run on every tab switch | `TabBarHooks.mm` (~2281–2918, 3274, 3821) | Confirmed by reading |
| S-08 | The settings root search field adds a `UIGlassEffect` pill | `YTKACERootOptionsController.mm` `makeSettingsHeader` | Confirmed by reading. Applies only in MarufYT capsule mode (`YTKACEMakeSettingsGlass()` returns nil otherwise) |
| S-09 | The diagnostics log is appended by **re-reading and re-writing the whole file for every line** (up to 512 KB), synchronously on a utility queue | `DownloadLog.mm` `YTKACEWriteLogLine` | Confirmed by reading |
| S-10 | `YTKACELocalized` re-resolves the preferred language on **every call** (a preference read, and the system language list in System mode) | `Localization.mm` | Confirmed by reading |
| S-11 | Capsule geometry is computed from the bar's bounds, safe-area bottom and item frames that MarufYT itself rewrites on each pass, with magic constants (`extra = 7`, `4`, `margin 21/14`). Safe-area values of 0 during early layout and 34 later change the result | `TabBarHooks.mm` `YTKACEApplyPivotBarGlass` | Partly confirmed. The effect over time is unobserved |
| S-12 | **No instrumentation exists** to see the real view tree, frames and insets on the device. Without it, S-03, S-04 and S-11 cannot be proven | — | Gap |

## 5. Stage 2: issue register and root causes

| # | Issue (your numbering in brackets) | Root cause | Evidence level |
| --- | --- | --- | --- |
| P3-01 | Bottom bar covers/obscures content (your item 5) | S-01 | Visual + source |
| P3-02 | MarufYT tab label/icon misaligned, icons uneven (your item 2) | S-03, S-04 | Visual + source reading |
| P3-03 | Category navigation differs between builds (your items 4, 1) | S-05 | Visual + source |
| P3-04 | Layout "changes after some time" on 21.43.5 (your item 3) | S-06 (hypothesis) with S-04, S-05 | **Hypothesis. Not seen in the clip** |
| P3-05 | Too many visual effects, heavy tab animation (your items 7, 8, 10) | S-02, S-07, S-08 | Visual + source |
| P3-06 | Delayed taps, heavy animation chain (your item 6) | S-07; S-09/S-10 add main-thread and disk work | Source only; not measured |
| P3-07 | Home inconsistent / spacing (your items 1, 2) | S-05; V-06 unexplained | Partly |

## 6. Decisions this baseline leads to

1. **Default to the simple, host-native look.** For anyone who has not chosen otherwise: the classic docked tab bar, no capsule, no glass preset, no depth layer, no compatibility-key removal. Stored choices are never overwritten.
2. **Pin the Home layout** by defaulting **Normal Home Layout** on. It is a documented, reversible setting and a stored value always wins.
3. **Make the MarufYT tab follow the host:** label visibility from the host's own tabs, and geometry from sibling native tabs. Neither depends on frames MarufYT has already altered.
4. **Remove the animation chain from the default path.** Standard short fades only, honouring Reduce Motion and Reduce Transparency.
5. **Add an on-demand layout snapshot** (no polling) so the next device test can show the real view tree if anything still shifts.
6. Test the geometry in a pure C unit test run in CI, and mark everything that needs the iPhone as **NOT TESTED**.
