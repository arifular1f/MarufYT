# MarufYT 1.1.4+marufyt.8

Coordinated security/application/repository update, 2026-11-03. Based on Phase 4.1.

- Removed authenticated request seed persistence and raw outgoing protobuf dumps;
  old files are queued for cleanup, with memory expiry/account-boundary clearing.
- Added trusted media destination/header rules, HTTPS task construction and
  HTTP/custom redirect validation without globally changing YouTube networking.
- Made diagnostics opt-in, omitted object payloads and strengthened redaction.
- Kept existing UI, settings, integrations, host bundle ID and original resources.
- Updated installation/build/compatibility/security/privacy and repository docs;
  preserved old releases, history and attribution. No fabricated screenshots.

Successful source CI: [41541646237](https://github.com/arifular1f/MarufYT/actions/runs/41541646237).
Independent Latest 21.43.5 and Stable 21.39.4 signing-required IPAs: 40/40 structural
checks each; 30 CI tests, 136 source checks, 55 Foundation fixture checks and 14
additional package checks passed. See the [full report](FINAL_UPDATE_REPORT.md)
for paths, hashes, exact source revision and test limitations.

Migration does not erase existing external copies/backups or revoke Google's
tokens. Restart/expiry/account changes can require a download retry because native
authenticated templates are no longer restored from disk. Use compatible local
signing and verify hashes first. Device login, account switching, feature behavior,
actual redirects, cleanup/protection and performance remain **NOT TESTED**.

Source changes are on `final-update-security`. Nothing is merged into `main` or
published as a replacement for an existing release artifact.
