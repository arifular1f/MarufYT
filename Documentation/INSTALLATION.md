# Install the coordinated security update

Current package: **1.1.4+marufyt.8**. Source branch: `final-update-security`.
Host identity stays `com.google.ios.youtube`; tweak identity is
`com.arifular1f.marufyt`. Use the matching Latest 21.43.5 or Stable 21.39.4 host.
Both have separate local output folders listed in the final update report.

1. Keep the previous IPA and your media/settings backup. Never overwrite a previous
   release. An explicit settings/media backup is not a guarantee of Google-session
   restoration or a replacement for securing device backups.
2. Verify the provided pre-signing SHA256 manifest and the successful CI/source
   revision. Repository artifacts contain only the tweak DEB/dylib; YouTube IPAs
   are assembled locally from your own decrypted copy.
3. Sign the correct unsigned IPA using your existing GBox workflow or another
   compatible signer and your own credentials. Do not upload certificates,
   passwords, cookies or tokens to GitHub. Re-signing changes the IPA hash.
4. Preserve the bundle identifier and appropriate entitlements where your signer
   supports them. Both builds share the same identifier and are alternatives,
   not independent side-by-side installations. Signing capabilities can affect
   Keychain, Google sign-in, push, app groups and updates to an installed app.
5. Launch and test login, account switching, logout, normal playback, PiP and
   downloads before relying on the new build. Actual iPhone behavior is NOT TESTED
   by the automated pipeline.

## Migration and rollback

On initialization, the update queues deletion of the exact legacy seed files
`sabr-seed.plist` / `player-request.pb` from the old YTKACE roots and the old
`ytkace-outgoing.pb` temp dump. It does not remove your media or settings. A
one-time log-format migration removes the old diagnostics log. Deletion is normal
filesystem deletion, not a forensic secure-erase guarantee; already copied/shared
files and old device/cloud backups are outside its reach.

Native request state now stays in memory and expires lazily after 15 minutes of
inactivity. Recognized account-removal/sign-out/identity-change boundaries clear
MarufYT's captured state and cancel active SABR sessions. Native Google account
methods still run; MarufYT does not revoke or replace Google's own tokens.
Because saved authenticated templates are no longer restored, playback may need
to refresh a stream and a download may require retry after restart/account change.
Validate this on both hosts; private API ABI guards do not prove device coverage.

Diagnostics are off unless the existing Debug Logs option is enabled. When enabled,
object payloads are omitted and known sensitive formats are filtered. Avoid sharing
unreviewed logs, backups or screenshots containing personal information.

Rollback uses a preserved older IPA with compatible local signing. Older builds
retain the audited storage/network weaknesses; no older artifact was silently
patched. Code rollback and data/session recovery are separate operations.

For ROOTLESS jailbreak installation, the DEB retains `/var/jb` layout and its declared
loader/firmware dependencies. This task does not install or execute a DEB on a device.
Build instructions: [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md).
