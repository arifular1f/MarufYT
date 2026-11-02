# Before / after evidence

Baseline source: phase2 `6d079b17cdd30685b5480a2e373c357356ed28ae`.
Optimization source: `2d5318a` (including `4d3c6c1`), package 1.1.4+marufyt.4.
Hosts: YouTube 21.43.5 and 21.39.4; target device/OS user-reported as
iPhone16,2 / iOS 27.2. No device or Apple profiling connection is available.

| Scenario / metric | Method | Before | After | Improvement |
| --- | --- | --- | --- | --- |
| Held-button custom tab drag selection scheduling | Source diff | 0.2 s dispatch delay | Same-event selection after ending native tracking | Scheduled delay removed; actual latency NOT TESTED |
| DeArrow image cache budget | Source inspection | 160 entries, no cost limit | 160 entries + 24 MiB decoded cost budget | Process memory improvement NOT TESTED |
| Library metadata/image cache budget | Source inspection | No count/cost limit | 64 entries + 32 MiB decoded cost budget | Process memory improvement NOT TESTED |
| Progress-card positioning timer | Source inspection | Recreate on attach/render | Reuse, 0.5 s tolerance, skip inactive layout | Energy savings NOT TESTED |
| Lightweight glass | Source inspection | No dedicated lightweight option | Plain selection pill, no lens gesture/depth, persistent setting | GPU/FPS improvement NOT TESTED |
| Cold startup, each host | Instruments launch trace | NOT TESTED | NOT TESTED | NOT TESTED |
| Warm startup, each host | Repeated timed foreground transitions | NOT TESTED | NOT TESTED | NOT TESTED |
| Touch-to-display latency, each host | High-frame-rate capture and event trace | NOT TESTED | NOT TESTED | NOT TESTED |
| Settings/About/library navigation | Signposts + time profiler | NOT TESTED | NOT TESTED | NOT TESTED |
| Scroll FPS/frame stability | Core Animation / hitch trace | NOT TESTED | NOT TESTED | NOT TESTED |
| Peak/steady memory | Allocations / VM Tracker | NOT TESTED | NOT TESTED | NOT TESTED |
| CPU utilization | Time Profiler | NOT TESTED | NOT TESTED | NOT TESTED |
| GPU/offscreen rendering | Metal/Core Animation trace | NOT TESTED | NOT TESTED | NOT TESTED |
| Energy/battery/thermals | Energy Log, matched device conditions | NOT TESTED | NOT TESTED | NOT TESTED |
| Background work / audio | Background activity trace | NOT TESTED | NOT TESTED | NOT TESTED |

For a valid device comparison use the preserved .3 IPA and new .4 IPA for the
same host, identical preferences, account/network/feed and display conditions.
Record at least five cold/warm launches, repeated rapid tab taps and drag/cancel
gestures, settings/library navigation, a long scroll, 30-minute playback/download
and foreground/background cycles. Repeat normal/lightweight/accessibility modes
and multiple text sizes. Report raw distributions, not just a best sample.
No percentage savings, target FPS, RAM or battery numbers are inferred from code.
