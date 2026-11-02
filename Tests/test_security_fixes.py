"""Focused source contracts. Foundation behavior executes separately in CI."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


class SecurityFixContracts(unittest.TestCase):
    def test_no_authenticated_seed_persistence_or_raw_protobuf_dump(self):
        sabr = read("Tweak/Features/Downloads/SABRDownloader.mm")
        hooks = read("Tweak/Features/Downloads/DownloadHooks.mm")
        for source in (sabr, hooks):
            self.assertNotIn("PersistSeed", source)
            self.assertNotIn("PersistPlayerRequest", source)
            self.assertNotIn("ytkace-outgoing.pb", source)
            self.assertNotIn("writeToURL:", source)
        lifecycle = read("Tweak/Runtime/SecurityLifecycle.mm")
        for name in ("sabr-seed.plist", "player-request.pb", "ytkace-outgoing.pb"):
            self.assertIn(name, lifecycle)
        self.assertIn("MarufYTPurgeLegacyRequestFiles", lifecycle)

    def test_expiry_logout_cleanup_and_signatures(self):
        source = read("Tweak/Runtime/SecurityLifecycle.mm")
        for name in ("YTKACEClearCapturedRequests", "YTKACESABRClearRequestState", "YTKACEClearPlaylistAuthorization"):
            self.assertIn(name + "();", source)
        self.assertIn("methodReturnType", source)
        self.assertIn("getArgumentTypeAtIndex", source)
        self.assertIn("removeAccount:completion:", source)
        self.assertIn("MarufYTRequestStateExpired", source)
        self.assertNotIn("NSTimer", source)

    def test_https_initial_tasks_and_both_redirect_layers(self):
        url = read("Tweak/Runtime/URLPolicy.mm")
        self.assertIn("!MarufYTIsSecureURL(request.URL)", url)
        self.assertIn("NSURLErrorUnsupportedURL", url)
        self.assertIn("previous.HTTPBody", url)
        sabr = read("Tweak/Features/Downloads/SABRDownloader.mm")
        self.assertIn("!MarufYTIsTrustedMediaURL(baseURL)", sabr)
        self.assertIn("!MarufYTIsTrustedMediaURL([NSURL URLWithString:redirect])", sabr)
        self.assertIn("MarufYTReplayHeaderAllowed", sabr)
        self.assertIn("securityGeneration != MarufYTSecurityGeneration()", sabr)
        for file in ("DirectDownloader.mm", "SABRDownloader.mm", "DownloadCoordinator.mm"):
            self.assertIn("willPerformHTTPRedirection:", read("Tweak/Features/Downloads/" + file))
        for path in (ROOT / "Tweak").rglob("*.mm"):
            self.assertNotIn("NSURLSession.sharedSession", path.read_text(encoding="utf-8"), str(path))

    def test_diagnostics_are_opt_in_and_objects_are_not_interpolated(self):
        log = read("Tweak/Features/Downloads/DownloadLog.mm")
        self.assertGreaterEqual(log.count("!YTKACEDebugLogsEnabled()"), 3)
        self.assertEqual(log.count('YTKACEWriteLogLine(identifier, format);'), 2)
        for marker in ('@"authorization"', '@"cookie"', '@"token"', '@"{"', '@"response="'):
            self.assertIn(marker, log)
        self.assertIn("NSURLIsExcludedFromBackupKey", log)
        self.assertIn("LogFormatVersion", read("Tweak/Runtime/SecurityLifecycle.mm"))
