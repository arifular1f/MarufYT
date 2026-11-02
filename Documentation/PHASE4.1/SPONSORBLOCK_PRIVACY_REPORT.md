# SponsorBlock Privacy Report (Phase 4.1)

## Outcome

**Implemented as an opt-in setting, default OFF.** The default request is byte-for-byte the same as before (`GET /api/skipSegments?videoID=<full id>&categories=…`). Settings → SponsorBlock → **Private Lookup** switches to the hash-prefix endpoint.

## API contract (verified against the server source and the live service)

Source: `ajayyy/SponsorBlockServer` `src/routes/getSkipSegmentsByHash.ts`, `getSkipSegments.ts`, `utils/hashPrefixTester.ts`, `utils/getHash.ts`. Live checks were made with `curl` on 2026-11-02.

| Point | Finding |
| --- | --- |
| Route | `GET /api/skipSegments/:prefix` |
| Prefix | `^[0-9a-f]{3,32}$` (case-insensitive); anything else is HTTP 400. MarufYT sends 4 characters |
| What is hashed | The video's `hashedVideoID` is stored with `getHash(videoID, 1)`: **one** round of SHA-256 of the 11-character ID, lowercase hex. (`getHash`'s default of 5000 rounds is used for user IDs, not video IDs) |
| Query | `categories` (JSON array) and `actionTypes`/`service` work as on the plain route; defaults are `["sponsor"]` and `["skip"]`, and MarufYT always sends `categories` |
| Response | `200` with an array `[{ "videoID": "…", "segments": [{ "category", "actionType", "segment", "UUID", "videoDuration", "locked", "votes", "description" }] }]`, one entry per **video that shares the prefix** and has matching segments. `404` with an empty body if none. There is **no `hash` field** |
| Filtering | The server already filters by `categories` and `actionTypes`. The client must choose its own video by exact `videoID` equality |

Live comparison: prefix `5f6b` (the first 4 hex characters of SHA-256 of `dQw4w9WgXcQ`) returned 79 videos in about 24 KB. For `eXjGWlJOhWg`, which has segments, the plain endpoint returned 1 segment and the prefix endpoint returned the identical segment (UUID, category, times, action type) inside its entry. All 79 entries hashed to the requested prefix.

## Upstream

YTKACE (the base of MarufYT) uses the plain `videoID` form; no hash-prefix lookup exists upstream, so there was nothing to compare or merge.

## Implementation

- `Tweak/MarufYT/Privacy/MarufYTSponsorHash.h`: pure C (SHA-256, ID validation, prefix extraction, exact-match test). The shipped code is the tested code.
- `SponsorClient.mm`: when enabled and the ID is well formed, request only the 4-character prefix plus `categories`; pick the entry whose `videoID` equals ours; reuse the existing segment validation (category membership, `skip` only, finite and ordered times). A malformed ID sends **nothing** (no fallback to the full ID, which would leak it). Network failure, non-200, oversize (> 1 MiB) or malformed JSON yield an empty result, as before.
- Cache key unchanged (video + categories).

## Tests

- Native (`Tests/native/test_sponsor_hash.c`, CI with a real C compiler, passes): SHA-256 known answers for "", "abc", 55/56/63/64/1000-byte inputs; prefixes for four video IDs including the real collision `dQw4w9WgXcQ`/`eXjGWlJOhWg`; odd lengths; rejection of lengths 3 and 33, short buffers, bad characters, wrong lengths, NULL; exact, case-sensitive entry matching.
- Static (Python, CI): private branch sends only `categories`, bad IDs return before any request, the key is not defaulted on.
- **Not covered by an automated test:** JSON response handling in Objective-C (malformed array entries, missing `segments`, non-string IDs, 404/5xx). It is written to ignore anything unexpected, but no test executes it. **Requires physical iPhone testing.**

## Privacy trade-offs (what is and is not claimed)

- With Private Lookup on, the SponsorBlock server receives 16 bits of the video's hash instead of the ID. Many videos share a 4-character prefix (79 with segments for `5f6b`), so the server cannot tell which one was watched **from the request alone**.
- The server still sees your IP address, timing, and any other request you make (including votes and DeArrow, which are separate and unchanged). Over time, correlation is still possible. This is reduced exposure, not anonymity.
- Cost: replies of tens of KB instead of a few hundred bytes, more parsing, more data.
- Not verified: behaviour of the setting on a device, and whether the public server rate-limits the prefix route differently.
- `PRIVACY.md` is updated to describe the option.
