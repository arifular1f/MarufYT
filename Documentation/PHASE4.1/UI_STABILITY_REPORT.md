# UI Stability Report (Phase 4.1)

**No UI code was changed in Phase 4.1.** The Simple tab bar default, motion helpers and layout math from Phase 3 stand. There is no device in this environment, so every statement about on-screen behaviour is static or inherited from Phase 3 and **requires physical iPhone testing**. The delayed-layout-shift issue is **not claimed fixed**.

## Review by area (static)

| Area | Finding |
| --- | --- |
| Home top bar, category chips | YouTube's own views; MarufYT moves neither in the default configuration (glass presets off). Chip row appearance depends on YouTube's Home layout, pinned to the normal layout by "Normal Home Layout" (default on) |
| Bottom tab bar | Default Simple = the host's docked bar, no MarufYT drawing, no overlap. Optional capsule geometry depends only on bar size and item height (tested pure function) |
| MarufYT icon and label | Laid out from the tab's own bounds and a native sibling by a fixed-point function (applying it twice gives the same result; tested). Label visibility follows the host |
| Settings navigation | Native inset-grouped tables; the only change this phase is one new toggle row (SponsorBlock → Private Lookup), a standard switch with a footer string |
| Player controls, Downloads library | Phase 3 replaced springs and bounce with short ease-out fades or slides that honour Reduce Motion. Phase 4.1 additionally removes main-thread artwork reads, which should reduce the chance of a hitch when a track changes (unmeasured) |
| Safe area | Capsule and tab math do not use the bottom safe-area inset; the download card positions from the window's safe area and relayouts on orientation or activation, not on a timer |
| View recreation / layout loops | No timer-driven layout. A one-shot layout snapshot (long-press About → Version) records frames on demand |

## Delayed layout changes, per version

| | YouTube 21.43.5 | YouTube 21.39.4 |
| --- | --- | --- |
| Host-specific factors found (static, Phase 3) | Native floating pivot bar, per-item label-hiding option, icon-only experiment, server-driven tabbed Home controlled by remote cold-config flags | Older floating-bar hooks; `UIDesignRequiresCompatibility` restored by the packager like 21.43.5 |
| Reproduced? | No. The supplied recording does not show drift over time | No |
| Evidence available | One recording of an older build; layout snapshot tool exists | Same |
| Status | **Unresolved / not tested.** Hypothesis: remote flags arriving after launch | **Not tested** |

To obtain evidence: install the build, open Settings → About, long-press Version for 3 seconds right after launch, then again after 10 minutes and after backgrounding; the log lines tagged `layout` list each relevant view's frame, `hidden`/`alpha`, the safe area and the stored preferences. Any difference between the two snapshots identifies what moved. Do this separately on each YouTube version.

## Screenshots

None are available for the current Simple look (the only images supplied are from before Phase 3 and show the old capsule), so none are published in the README.
