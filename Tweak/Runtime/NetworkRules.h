// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
// Shared by native iOS code and the portable security known-answer tests.
#pragma once
#include <stdbool.h>
#include <string.h>
#include <strings.h>
static inline bool MarufYTRequestStateExpired(double last, double now) {
    return last > 0 && (now < last || now - last > 900.0);
}
static inline bool MarufYTMediaHostAllowed(const char *host) {
    if (!host) return false;
    const char *suffix = ".googlevideo.com";
    size_t n = strlen(host), s = strlen(suffix);
    return strcasecmp(host, "googlevideo.com") == 0 ||
        (n > s && strcasecmp(host + n - s, suffix) == 0);
}
static inline bool MarufYTReplayHeaderAllowed(const char *name) {
    if (!name) return false;
    const char *allowed[] = {"user-agent", "range", "accept", "accept-encoding",
        "accept-language", "content-type", "x-youtube-client-name",
        "x-youtube-client-version", "x-goog-visitor-id"};
    for (size_t i = 0; i < sizeof allowed / sizeof allowed[0]; ++i)
        if (strcasecmp(name, allowed[i]) == 0) return true;
    return false;
}
static inline bool MarufYTPublicRedirectHeaderAllowed(const char *name) {
    if (!name) return false;
    const char *allowed[] = {"user-agent", "range", "accept", "accept-encoding", "accept-language"};
    for (size_t i = 0; i < sizeof allowed / sizeof allowed[0]; ++i)
        if (strcasecmp(name, allowed[i]) == 0) return true;
    return false;
}
