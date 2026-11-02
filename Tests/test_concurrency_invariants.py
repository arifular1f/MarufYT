"""Static regression guards for observer lifecycle, blocking waits and artwork I/O.

Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

These read the Objective-C++ source; they do not execute UIKit. They pin the
reviewed Phase 4.1 inventory, so a new observer, a new blocking wait or a
synchronous artwork read on the main thread fails until it is reviewed and the
inventory below is updated deliberately.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TWEAK = ROOT / "Tweak"


def sources():
    for path in sorted(TWEAK.rglob("*.mm")):
        yield path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8", errors="replace")


# file -> number of notification/KVO registrations (reviewed 2026-11-02).
OBSERVERS = {
    "Tweak/Features/Compatibility/CastCompatibility.mm": 1,
    "Tweak/Features/Downloads/DownloadProgressView.mm": 1,
    "Tweak/Features/Downloads/GlobalDownloadMiniPlayer.mm": 6,
    "Tweak/Features/Downloads/YTKACEAudioPlayerController.mm": 2,
    "Tweak/Features/Downloads/YTKACEDownloadPlayerController.mm": 11,
    "Tweak/Features/Interface/ContentVisibilityHooks.mm": 2,
    "Tweak/Features/Interface/MiscellaneousHooks.mm": 1,
    "Tweak/Features/Interface/NavigationVisibility.mm": 1,
    "Tweak/Features/Interface/PostImageSaver.mm": 1,
    "Tweak/Features/Interface/ProfilePictureViewer.mm": 1,
    "Tweak/Features/Playback/LoopControls.mm": 1,
    "Tweak/Features/Playback/PiPControls.mm": 1,
    "Tweak/Features/Playback/ProgressBarStyle.mm": 1,
    "Tweak/Features/Playback/RemoteSkip.mm": 2,
    "Tweak/Features/Playback/SleepTimerControls.mm": 2,
    "Tweak/Features/Playback/SpeedControls.mm": 2,
    "Tweak/Features/Queue/QueueHooks.mm": 1,
    "Tweak/Features/Shorts/ShortsHooks.mm": 1,
    "Tweak/Features/Shorts/ShortsSessionLimit.mm": 1,
    "Tweak/Features/SponsorBlock/DeArrow.mm": 1,
    "Tweak/Features/SponsorBlock/SponsorHooks.mm": 1,
    "Tweak/Settings/YTKACEDownloadsController.mm": 5,
    "Tweak/UI/ExtraDim.mm": 1,
}
OBSERVER_PATTERN = re.compile(r"addObserverForName:|addObserver:\s*[A-Za-z_\[]|\[[A-Za-z_.]+ addObserver:")

# Files that block a background thread on a network or muxer completion
# (reviewed: every wait runs on a global queue; none runs on the main thread).
BLOCKING_WAITS = {
    "Tweak/Features/Downloads/DirectDownloader.mm": 2,
    "Tweak/Features/Downloads/PlaylistDownloader.mm": 2,
    "Tweak/Features/Downloads/YTKACEMediaImporter.mm": 2,
    "Tweak/Features/Interface/AiSList.mm": 1,
    "Tweak/Features/Streaming/HLSPlayback.mm": 1,
    "Tweak/Features/Streaming/TVClient.mm": 1,
}


class ObserverLifecycleTests(unittest.TestCase):
    def test_observer_inventory_is_reviewed(self):
        found = {}
        for name, text in sources():
            count = len(re.findall(r"addObserverForName:|\baddObserver:", text))
            if count:
                found[name] = count
        self.assertEqual(found, OBSERVERS,
                         "A notification/KVO registration was added or removed; review its lifetime and update OBSERVERS")

    def test_instance_observers_are_removed_in_dealloc(self):
        # View controllers register in viewDidLoad/init and must unregister in dealloc.
        for name in ("Tweak/Features/Downloads/YTKACEAudioPlayerController.mm",
                     "Tweak/Features/Downloads/YTKACEDownloadPlayerController.mm",
                     "Tweak/Settings/YTKACEDownloadsController.mm"):
            text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
            self.assertIn("removeObserver:self", text, name)
            self.assertIn("- (void)dealloc", text, name)

    def test_block_observers_are_installed_once(self):
        # Block observers return a token that is never removed, so each must sit
        # behind a once-guard (dispatch_once, flag or nil check) or a constructor.
        guarded = {
            "Tweak/Features/Compatibility/CastCompatibility.mm": "dispatch_once",
            "Tweak/Features/Interface/ContentVisibilityHooks.mm": "dispatch_once",
            "Tweak/Features/Interface/MiscellaneousHooks.mm": "dispatch_once",
            "Tweak/Features/Interface/NavigationVisibility.mm": "YTKACENavigationObserverInstalled",
            "Tweak/Features/Interface/ProfilePictureViewer.mm": "dispatch_once",
            "Tweak/Features/Playback/ProgressBarStyle.mm": "dispatch_once",
            "Tweak/Features/Shorts/ShortsHooks.mm": "YTKACEReelViews == nil",
            "Tweak/Features/Shorts/ShortsSessionLimit.mm": "YTKACEShortsLimitObserver != nil",
            "Tweak/Features/SponsorBlock/SponsorHooks.mm": "YTKACEPlaybackPreferenceObserver == nil",
        }
        for name, guard in guarded.items():
            text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
            self.assertIn(guard, text, name)
        entry = (TWEAK / "Entry.mm").read_text(encoding="utf-8")
        # The module installers (QueueHooks, DeArrow, PostImageSaver ...) run from one constructor.
        self.assertEqual(entry.count("YTKACEInstallModules();"), 1)
        for installer in ("YTKACEInstallQueueHooks", "YTKACEInstallDeArrow", "YTKACEInstallPostImageSaverHooks"):
            self.assertEqual(entry.count(installer + "();"), 1, installer)
        self.assertEqual(len(re.findall(r"YTKACEInstallQueueHooks\(\)", "\n".join(t for _, t in sources()))), 1)  # only the Entry.mm call site

    def test_no_strong_self_in_block_observers(self):
        for name, text in sources():
            for match in re.finditer(r"addObserverForName:[\s\S]{0,400}?usingBlock:\^[^{]*\{([\s\S]{0,300}?)\n\s*\}\];", text):
                body = match.group(1)
                self.assertNotRegex(body, r"\bself\b", f"{name}: block observer captures self")


class BlockingWaitTests(unittest.TestCase):
    def test_wait_inventory_is_reviewed(self):
        found = {}
        for name, text in sources():
            count = text.count("dispatch_semaphore_wait")
            if count:
                found[name] = count
        self.assertEqual(found, BLOCKING_WAITS,
                         "A blocking wait was added; prove it never runs on the main thread, then update BLOCKING_WAITS")

    def test_waits_are_inside_background_dispatch_files(self):
        for name in BLOCKING_WAITS:
            text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
            self.assertRegex(text, r"dispatch_get_global_queue|dispatch_async", name)

    def test_network_waits_have_timeouts(self):
        # Only the muxer waits may be unbounded (large files); network waits use a deadline.
        for name in BLOCKING_WAITS:
            if name.endswith("YTKACEMediaImporter.mm"):
                continue
            text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("DISPATCH_TIME_FOREVER", text, name)


class ArtworkIOTests(unittest.TestCase):
    def test_no_synchronous_artwork_read_on_main_paths(self):
        for name in ("Tweak/Features/Downloads/GlobalDownloadMiniPlayer.mm",
                     "Tweak/Features/Downloads/YTKACEAudioPlayerController.mm"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertEqual(len(re.findall(r"YTKACEMediaArtworkImage\(", text)), 1 if "AudioPlayer" in name else 0, name)
            self.assertIn("YTKACEMediaArtworkImageAsync(", text, name)
        # The one remaining direct call in the audio player is inside its global-queue queue-info loader.
        audio = (ROOT / "Tweak/Features/Downloads/YTKACEAudioPlayerController.mm").read_text(encoding="utf-8")
        index = audio.index("YTKACEMediaArtworkImage(URL)")
        self.assertIn("dispatch_get_global_queue", audio[max(0, index - 400):index])
        player = (ROOT / "Tweak/Features/Downloads/YTKACEDownloadPlayerController.mm").read_text(encoding="utf-8")
        self.assertNotIn("YTKACEMediaArtworkImage(self.currentURL)", player)

    def test_artwork_cache_is_bounded(self):
        text = (ROOT / "Tweak/Features/Downloads/MediaArtwork.mm").read_text(encoding="utf-8")
        self.assertIn("countLimit = 8", text)
        self.assertIn("totalCostLimit", text)


class SponsorPrivateLookupTests(unittest.TestCase):
    def test_private_mode_never_sends_the_video_id(self):
        text = (ROOT / "Tweak/Features/SponsorBlock/SponsorClient.mm").read_text(encoding="utf-8")
        self.assertIn("SponsorBlock.PrivateLookup", text)
        # Private branch: categories only; invalid IDs return before any request.
        self.assertRegex(text, r"privateLookup\s*\?\s*@\[categoryItem\]")
        self.assertRegex(text, r"if \(!MarufYTSponsorHashPrefix\([\s\S]{0,400}?completion\(@\[\]\);\s*return;")

    def test_private_lookup_is_opt_in(self):
        for name in ("Tweak/Runtime/Preferences.mm", "Tweak/MarufYT/Design/MarufYTDesign.mm"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("PrivateLookup", text, f"{name}: must not be defaulted on")


if __name__ == "__main__":
    unittest.main()
