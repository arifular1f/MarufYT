# CPU, network and battery review

Confirmed changes for both hosts:

- DownloadProgressView.mm reuses its existing 2-second positioning timer rather
  than invalidating/recreating it for each progress render. A 0.5-second tolerance
  allows coalescing. Detached cards terminate the timer; inactive applications
  skip card layout. Existing hide/reset invalidation remains. The timer may still
  wake while an active download's card exists in the background: it was not
  replaced with an unverified lifecycle subsystem.
- TabBarHooks.mm stops transient lens display-link work off-window/inactive;
  lightweight appearance avoids custom lens tracking and depth decoration.
- Download library queue cancellation and cache budgets bound pending/cached work.

Network review (behavior retained): SponsorClient.mm has a 128-entry segment cache
keyed by video/category configuration, ephemeral sessions and finite timeouts.
Concurrent cold misses can still produce duplicate requests; request coalescing
was not added without completion-order and cancellation tests. DeArrow already
has separate in-flight ID sets, pending weak UI nodes/cells, bounded request
concurrency and a persistent bounded branding store. AiSList refresh is serialized
by its loading flag, loads files on a utility queue and uses a four-hour freshness
interval. Its semaphore waits are on that worker queue, not the caller/main queue.
Stale-network failure retry behavior is a remaining review item; no accuracy,
TTL, categories or service responses were changed for benchmark appearances.

No new timer, background thread, network service, dependency or unconditional log
was added. Existing release diagnostic logging is preference guarded/redacted.
Repeated hierarchy traversals in normal glass mode remain a profiling candidate;
blind hierarchy caches would risk stale views after host navigation changes.

No device Instruments, Energy Log, CPU, GPU, thermal or battery trace is available.
These are source-level reductions in scheduled/allocation work, not measured
battery improvements. Startup/warm navigation changes are incidental and unmeasured;
Google authentication initialization was not touched.
