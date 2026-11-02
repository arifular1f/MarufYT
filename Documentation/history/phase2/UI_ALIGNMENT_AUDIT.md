# Pre-change UI and performance audit

Baseline: phase2 `6d079b17cdd30685b5480a2e373c357356ed28ae`, inspected
2026-11-02 before native edits. Work branch: `optimization/phase2-performance`.
Original IPA/DEB SHA256 baseline is retained outside Git in the new release directory.

The user reports both 21.43.5 and 21.39.4 launch and their features work.
This is user-reported baseline evidence, not our runtime regression result.
The referenced 47-second recording was not present in the accessible attachments;
its path has been requested. No frame-by-frame observations are claimed.

| Finding | Source evidence | Host scope | Proposed change / confidence |
| --- | --- | --- | --- |
| Delayed tab activation | TabBarHooks.mm, handleSystemLens:gesture:bar:glass: dispatches selection 0.2 seconds later for heldButton | Both hosts when this gesture path runs | Select on release independently of lens settling; source-confirmed delay, duplicate host event behavior needs device testing |
| Replacement tab icon/label geometry ignores native anchors | Downloads and extra tabs use y=4, bottom-16 and 14pt label height | Both; newer hierarchy may expose it more | Use converted native icon/label bounds, bounded intrinsic fallback; exact 21.43.5 visual correction NOT VERIFIED |
| Glass gesture/effects lack accessibility fast path | Custom zero-duration long press, springs and display-link mask tracking | Both on supported glass systems | Opt-in lightweight glass, Reduce Motion/Transparency guards; preserve normal glass default |
| Thumbnail memory budget is count-only | DeArrow.mm: NSCache countLimit=160, no costLimit or per-image cost | Both | Add decoded pixel cost and a 24 MiB advisory NSCache budget |
| Transient lens work can survive view removal until timeout | YTKACELensTracker tick checks lens existence and deadline only | Both | End tracking off-window/inactive; release pending completion safely, retain original bounded timeout |
| Download positioning timer recreated on every attach | DownloadProgressView.mm: renderItem calls attach, which invalidates/creates timer | Both | Reuse timer, add tolerance, skip layout while inactive; preserve active downloads |
| Top logo/search/notification hierarchy is modified by native glass wrapping | GlassChrome.mm reparents native children and recenters their frames | Host-dependent, exact affected version unproven | Audit only; no speculative reparenting rewrite without recording/device evidence |
| Settings/About/library alignment | Existing grouped tables, icon tiles and Dynamic Type helpers | Both | No measured defect yet; retain existing working screens |

No source inspection proves FPS, input-to-display latency, RAM savings, energy
savings or visual alignment on an iPhone. The two host binaries must be packaged
and structurally checked independently. Host runtime selectors, safe areas,
orientation, large text, selected states and rapid taps require physical testing.
Google sessions, licensing, playback, media pipelines and network response
semantics are outside these targeted changes. No network/polling subsystem rewrite
is justified by a measured regression in the available evidence.
