# Windows downstream HLS test results

Executed 2026-11-03 10:46:02 local PC time. Commit `743f307b816d275fef88d34a36ba546415015753`.

**These are Windows mock-server and source checks, not MarufYT/iPhone runtime results.**

Result: **80 PASS, 0 FAIL**. Both mock servers were started, exercised and stopped.

## Prerequisites and exact files

- Python 3.15.1; OpenSSL 3.5.9 29 Sep 2026 (Library: OpenSSL 3.5.9 29 Sep 2026). Required Python modules are standard-library modules.
- `mock_hls_server.py`: existing HTTP/HTTPS fixture server.
- `self_test_mock.py`: existing standalone fixture self-test.
- `run_windows_walkthrough.py`: this per-case Windows launcher/report writer.
- `inject_fixture_response.py`: optional phone/proxy addon; not executed.
- FFmpeg/mitmweb are optional for later playback/device work; neither is needed for these transport checks.

## What was executed

1. Verified Python, OpenSSL and Python SSL/HTTP libraries.
2. Generated a temporary CA/server certificate, trusted only by the test Python client.
3. Started loopback HTTP and HTTPS listeners on temporary ports 3568 and 3569.
4. Executed P00–P10 and R01–R09 (redirects 301/302/303/307/308), controlled target requests and synthetic header controls.
5. Ran all five existing security source-contract tests and checked source/release preservation.
6. Closed both servers and deleted temporary certificate/key/media files. No user clicks were required.

## How to read PASS

**Mock PASS means the test server returned the intended fixture and/or the Windows client could reach its controlled target.**
An HTTP downgrade fixture PASS does not mean MarufYT rejected that downgrade. Some controlled HTTP destinations were deliberately requested by this Windows client to confirm the sink works.
Headers on redirect controls were deliberately sent/omitted by the test client, not automatically forwarded by MarufYT.

| Case | Windows result | Simple explanation | Scope |
| --- | --- | --- | --- |
| P00-HTTP | PASS | HTTP test server answers the master request | Mock server only |
| P00-HTTPS | PASS | HTTPS master works with certificate validation | Mock server only |
| P00-CHILD | PASS | Relative child playlist is served | Mock server only |
| P00-SEGMENT | PASS | Synthetic segment bytes are served (not video decoding) | Mock server only |
| TLS-UNTRUSTED | PASS | Client refuses the temporary CA when it is not explicitly trusted | Mock server only |
| P01 | PASS | Master contains an HTTP child test URL | Mock server only |
| P01-SINK | PASS | Controlled target is reachable with no copied credentials | Mock server only |
| P02 | PASS | Child contains an HTTP segment test URL | Mock server only |
| P02-SINK | PASS | Controlled target is reachable with no copied credentials | Mock server only |
| P03 | PASS | Master contains a cross-domain HTTPS child URL | Mock server only |
| P03-SINK | PASS | Controlled target is reachable with no copied credentials | Mock server only |
| P04 | PASS | Child contains a cross-domain HTTPS segment URL | Mock server only |
| P04-SINK | PASS | Controlled target is reachable with no copied credentials | Mock server only |
| P05 | PASS | Child userinfo fixture is generated | Mock server only |
| P06 | PASS | Segment userinfo fixture is generated | Mock server only |
| P07 | PASS | Child unacceptable-port fixture is generated | Mock server only |
| P08 | PASS | Segment unacceptable-port fixture is generated | Mock server only |
| P09 | PASS | Invalid child-host fixture is generated | Mock server only |
| P10 | PASS | Invalid segment-host fixture is generated | Mock server only |
| R01-301 | PASS | same-domain HTTPS master returns 301 and correct controlled target | Mock server only |
| R01-302 | PASS | same-domain HTTPS master returns 302 and correct controlled target | Mock server only |
| R01-303 | PASS | same-domain HTTPS master returns 303 and correct controlled target | Mock server only |
| R01-307 | PASS | same-domain HTTPS master returns 307 and correct controlled target | Mock server only |
| R01-308 | PASS | same-domain HTTPS master returns 308 and correct controlled target | Mock server only |
| R02-301 | PASS | master downgrade to HTTP returns 301 and correct controlled target | Mock server only |
| R02-302 | PASS | master downgrade to HTTP returns 302 and correct controlled target | Mock server only |
| R02-303 | PASS | master downgrade to HTTP returns 303 and correct controlled target | Mock server only |
| R02-307 | PASS | master downgrade to HTTP returns 307 and correct controlled target | Mock server only |
| R02-308 | PASS | master downgrade to HTTP returns 308 and correct controlled target | Mock server only |
| R03-301 | PASS | cross-domain HTTPS master returns 301 and correct controlled target | Mock server only |
| R03-302 | PASS | cross-domain HTTPS master returns 302 and correct controlled target | Mock server only |
| R03-303 | PASS | cross-domain HTTPS master returns 303 and correct controlled target | Mock server only |
| R03-307 | PASS | cross-domain HTTPS master returns 307 and correct controlled target | Mock server only |
| R03-308 | PASS | cross-domain HTTPS master returns 308 and correct controlled target | Mock server only |
| R04-301 | PASS | child downgrade to HTTP returns 301 and correct controlled target | Mock server only |
| R04-302 | PASS | child downgrade to HTTP returns 302 and correct controlled target | Mock server only |
| R04-303 | PASS | child downgrade to HTTP returns 303 and correct controlled target | Mock server only |
| R04-307 | PASS | child downgrade to HTTP returns 307 and correct controlled target | Mock server only |
| R04-308 | PASS | child downgrade to HTTP returns 308 and correct controlled target | Mock server only |
| R05-301 | PASS | segment downgrade to HTTP returns 301 and correct controlled target | Mock server only |
| R05-302 | PASS | segment downgrade to HTTP returns 302 and correct controlled target | Mock server only |
| R05-303 | PASS | segment downgrade to HTTP returns 303 and correct controlled target | Mock server only |
| R05-307 | PASS | segment downgrade to HTTP returns 307 and correct controlled target | Mock server only |
| R05-308 | PASS | segment downgrade to HTTP returns 308 and correct controlled target | Mock server only |
| R06-301 | PASS | cross-domain HTTPS child returns 301 and correct controlled target | Mock server only |
| R06-302 | PASS | cross-domain HTTPS child returns 302 and correct controlled target | Mock server only |
| R06-303 | PASS | cross-domain HTTPS child returns 303 and correct controlled target | Mock server only |
| R06-307 | PASS | cross-domain HTTPS child returns 307 and correct controlled target | Mock server only |
| R06-308 | PASS | cross-domain HTTPS child returns 308 and correct controlled target | Mock server only |
| R07-301 | PASS | cross-domain HTTPS segment returns 301 and correct controlled target | Mock server only |
| R07-302 | PASS | cross-domain HTTPS segment returns 302 and correct controlled target | Mock server only |
| R07-303 | PASS | cross-domain HTTPS segment returns 303 and correct controlled target | Mock server only |
| R07-307 | PASS | cross-domain HTTPS segment returns 307 and correct controlled target | Mock server only |
| R07-308 | PASS | cross-domain HTTPS segment returns 308 and correct controlled target | Mock server only |
| R08-301 | PASS | cross-domain HTTP master returns 301 and correct controlled target | Mock server only |
| R08-302 | PASS | cross-domain HTTP master returns 302 and correct controlled target | Mock server only |
| R08-303 | PASS | cross-domain HTTP master returns 303 and correct controlled target | Mock server only |
| R08-307 | PASS | cross-domain HTTP master returns 307 and correct controlled target | Mock server only |
| R08-308 | PASS | cross-domain HTTP master returns 308 and correct controlled target | Mock server only |
| R09-301 | PASS | redirect-loop response returns 301 and correct controlled target | Mock server only |
| R09-302 | PASS | redirect-loop response returns 302 and correct controlled target | Mock server only |
| R09-303 | PASS | redirect-loop response returns 303 and correct controlled target | Mock server only |
| R09-307 | PASS | redirect-loop response returns 307 and correct controlled target | Mock server only |
| R09-308 | PASS | redirect-loop response returns 308 and correct controlled target | Mock server only |
| HDR-SETCOOKIE | PASS | A sets only the synthetic Secure host-only cookie | Mock server only |
| HDR-A | PASS | Origin A detects both synthetic markers | Mock server only |
| HDR-B-SAFE | PASS | B detects no markers when the test client sends none | Mock server only |
| HDR-B-UNSAFE | PASS | B detects both markers in deliberate unsafe control | Mock server only |
| LOG-QUERY | PASS | Unknown query canary does not break a valid fixture | Mock server only |
| LOG-REDACTION | PASS | Logs contain no marker values or query canary | Mock server only |
| PATH-SAFETY | PASS | Server refuses a path outside fixture routes | Mock server only |
| SC1 | PASS | F-04 sensitive logging source contract | Source inspection test, not runtime |
| SC2 | PASS | F-01 cleanup/expiry source contract | Source inspection test, not runtime |
| SC3 | PASS | U-01 cache/handoff source contract | Source inspection test, not runtime |
| SC4 | PASS | F-02/F-03 HTTPS and redirect source contracts | Source inspection test, not runtime |
| SC5 | PASS | F-01 no sensitive seed persistence source contract | Source inspection test, not runtime |
| SC-EXIT | PASS | Existing source-test command finishes successfully | Source inspection test, not runtime |
| PRESERVE-SOURCE | PASS | All tracked source files and branch refs are unchanged | Preservation |
| PRESERVE-142 | PASS | 142 existing release files still match their checksums | Preservation |
| PRESERVE-25 | PASS | 25 existing release files still match their checksums | Preservation |

## Actual MarufYT status — both versions

| Requirement | Latest 21.43.5 | Stable 21.39.4 |
| --- | --- | --- |
| Native master URL validation / invalid URL fallback | NOT TESTED on device | NOT TESTED on device |
| Child/segment URI rejection and redirect security | NOT TESTED | NOT TESTED |
| Native Authorization/Cookie forwarding | NOT EXERCISED | NOT EXERCISED |
| Video playback and decoder behavior | NOT TESTED | NOT TESTED |

Windows cannot execute these iOS IPAs or Apple Foundation policy code. The source-contract tests inspect code order/content only. No mirrored Python URL validator is being claimed as the app policy.
The served segment is intentionally nonplayable synthetic bytes; FFmpeg media generation and video decoding were not performed.
Temporary high ports are suitable for this harness but U-01 accepts only absent/443 HTTPS ports for app master URLs.
TLS checks use the two certificate DNS names routed explicitly to loopback; no operating-system DNS/hosts-file changes were made.

## Preservation and evidence

- All tracked source hashes and branch refs remain unchanged; no merge, push, version change or rebuild.
- All 142 previous .8 release files and all 25 U01-HLS release files match their checksum manifests, including both IPAs and DEBs.
- No real account credentials, passwords, cookies or tokens were used. Synthetic marker values were not logged.
- No system certificate, firewall rule, DNS change or extra software was installed.
- Detailed evidence: [WINDOWS-20261103-104554-677900](Evidence/WINDOWS-20261103-104554-677900/RESULTS.json), [case CSV](Evidence/WINDOWS-20261103-104554-677900/RESULTS.csv), [request metadata](Evidence/WINDOWS-20261103-104554-677900/MOCK_REQUESTS.jsonl), [source-test log](Evidence/WINDOWS-20261103-104554-677900/SOURCE_CONTRACTS.txt).

## Repeat with one command

Run from `C:\Users\oriyan\Desktop\ios App\MarufYT`:

```powershell
python -B Documentation/FINAL_VERIFICATION/DOWNSTREAM_HLS/run_windows_walkthrough.py
```

Each run creates a new evidence folder, uses fresh temporary keys and stops its own servers automatically.
Do not interpret these results as physical iPhone security verification. Follow TEST_PLAN.md only when an owned test phone and controlled fixture routing are available.
