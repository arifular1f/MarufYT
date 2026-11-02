# Automation within the no-main-change constraint

Reviewed 2026-11-02. The default branch remains `main`; no main commit or default-branch setting is changed.

## Implemented and usable on phase2

- Existing repository security-alert/push-protection settings remain enabled. Those service settings are separate from a version-update schedule.
- The existing `build.yml` is already registered on the default branch with `workflow_dispatch`. Its `phase2` version adds an `audit_only` boolean input. A supported branch selection runs that version:

```sh
gh workflow run build.yml --repo arifular1f/MarufYT --ref phase2 -f audit_only=true
```

- Audit-only mode runs unit/source/credential checks, fresh pinned-toolchain installation and an isolated static-library relink demonstration. The release `make package` and package collection/upload steps are skipped. Diagnostic evidence is uploaded even on audit failure.
- Normal push/pull-request behaviour on the configured branches is retained. A deliberate audit/documentation commit can use `[skip ci]`; the explicit audit-only dispatch is separately tested and does not imply a native release build.

## Not enabled under the current constraint

Dependabot's weekly configuration must be stored on the default branch. The `phase2` file cannot activate that schedule by itself. GitHub scheduled workflows likewise do not run a branch-only schedule as a substitute. No external scheduler, new token, task running on this PC, default-branch change, or undocumented API is introduced to disguise that limitation.

The frozen main workflow still has its older contents. A branch-dispatched audit validates Phase 2 tooling; it is not a claim that main has received the hardening or that the old main workflow satisfies SHA-pin policy. Activating default-branch configuration requires a separately authorized change compatible with the owner's instructions.

Primary references: [Dependabot configuration placement](https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file), [manual workflow branch selection](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow), and [scheduled workflow behaviour](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
