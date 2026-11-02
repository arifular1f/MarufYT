# Transitive toolchain lock and residuals

Date: 2026-11-02. Reviewed lock: `Tools/toolchain.lock.json`.

The former verified installer still fetched compiler/SDK releases through moving selectors and initially cloned a moving Theos branch before checkout. The Phase 2 workflow now bypasses that installer entirely and runs `Tools/bootstrap_pinned.py`.

| Input | Pin / verification |
| --- | --- |
| Theos | `3ac89c984ec652fd16bcd91b33ae16de45ce76fa`, fetched directly, detached checkout |
| Eight direct submodules | Exact reviewed gitlinks and HTTPS URLs in the lock; recursive descendants use their pinned parent gitlinks, with status recorded |
| Linux x86_64 compiler | Publisher release `test-210562a`, archive SHA-256 `a72a7a577e2fbe2838b6b5e9c72034fa7d114af96f0e1d4b016f18730ce4056e`, 86,163,280 bytes |
| iPhoneOS 16.5 SDK | Publisher release `master-146e41f`, SHA-256 `5e0fd3f01266cce4ce012d4a99b38eb56578fca40d09edc81cd83dee958202fb`, 17,446,920 bytes |
| Actions | Existing full commit SHA pins retained |
| FFmpeg source | Signed release plus digest/fingerprint lock in `Tools/ffmpeg-source.lock.json`; no automatic upgrade of the vendored libraries |

Archives are size/hash checked before extraction or tool execution, including on cache hits. Only download archives are cached; executable Theos trees are installed fresh. Extraction enforces path/prefix/type bounds with Python's data filter and an expanded-size limit. No `latest` resolver or fetched installer executes during bootstrap. The previous release compiler identifies as clang 11.1.0; the selected publisher asset records that same compiler line. These are future build inputs, not a claim that historical releases were retrospectively built with this new bootstrap.

The compiler/SDK publishers did not provide a digest in the reviewed GitHub asset metadata. Their hashes were independently calculated from the versioned publisher URLs over HTTPS and then locked. That prevents silent future replacement but is not an independent publisher-signature attestation. The FFmpeg source has stronger, separately verified signature evidence.

## Remaining mutable platform components

- GitHub's hosted `ubuntu-24.04` image, kernel/runner agent and runner-provided Python/Git/Node versions receive platform updates.
- Required Ubuntu host packages are installed from signed repositories; exact installed versions are recorded with `dpkg-query`, not fixed to an unmaintained apt snapshot.
- GitHub Actions service/cache availability, HTTPS/CA trust and repository availability remain external dependencies.

These are residuals of the selected hosted-runner model, not universally impossible to pin. Stronger byte reproducibility would require an independently maintained image/digest and repository snapshot policy. No claim of fully reproducible binaries is made.

Bootstrap tests reject moving archive URLs, corrupted cache contents, traversal members and escaping symlinks. The audit-only CI execution verifies that the complete locked bootstrap actually works; source-pattern checks alone are not installation evidence.
