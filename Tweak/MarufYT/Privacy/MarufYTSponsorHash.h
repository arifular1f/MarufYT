// MarufYT — SponsorBlock hash-prefix lookup helpers (pure C, header-only).
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// SponsorBlock's GET /api/skipSegments/:prefix takes the first 4..32 lowercase
// hex characters of SHA-256(videoID) (a single round, as the server's
// getHash(videoID, 1) stores it) and returns every video that shares the
// prefix. The client must keep only the entry whose videoID equals its own.
// No UIKit or Foundation here, so the same code is compiled and tested on the
// CI host (Tests/native/test_sponsor_hash.c) and shipped in the tweak.

#ifndef MARUFYT_SPONSOR_HASH_H
#define MARUFYT_SPONSOR_HASH_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define MARUFYT_SPONSOR_PREFIX_LENGTH 4

typedef struct {
    uint32_t state[8];
    uint64_t bits;
    uint8_t block[64];
    size_t used;
} MarufYTSha256;

static const uint32_t MarufYTSha256K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};

static inline uint32_t MarufYTRotr(uint32_t value, unsigned amount) {
    return (value >> amount) | (value << (32u - amount));
}

static inline void MarufYTSha256Compress(MarufYTSha256 *ctx, const uint8_t *chunk) {
    uint32_t w[64];
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)chunk[i * 4] << 24) | ((uint32_t)chunk[i * 4 + 1] << 16) |
               ((uint32_t)chunk[i * 4 + 2] << 8) | (uint32_t)chunk[i * 4 + 3];
    }
    for (int i = 16; i < 64; i++) {
        uint32_t s0 = MarufYTRotr(w[i - 15], 7) ^ MarufYTRotr(w[i - 15], 18) ^ (w[i - 15] >> 3);
        uint32_t s1 = MarufYTRotr(w[i - 2], 17) ^ MarufYTRotr(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    uint32_t a = ctx->state[0], b = ctx->state[1], c = ctx->state[2], d = ctx->state[3];
    uint32_t e = ctx->state[4], f = ctx->state[5], g = ctx->state[6], h = ctx->state[7];
    for (int i = 0; i < 64; i++) {
        uint32_t s1 = MarufYTRotr(e, 6) ^ MarufYTRotr(e, 11) ^ MarufYTRotr(e, 25);
        uint32_t ch = (e & f) ^ (~e & g);
        uint32_t t1 = h + s1 + ch + MarufYTSha256K[i] + w[i];
        uint32_t s0 = MarufYTRotr(a, 2) ^ MarufYTRotr(a, 13) ^ MarufYTRotr(a, 22);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        uint32_t t2 = s0 + maj;
        h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

static inline void MarufYTSha256Init(MarufYTSha256 *ctx) {
    static const uint32_t initial[8] = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                                        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
    memcpy(ctx->state, initial, sizeof initial);
    ctx->bits = 0;
    ctx->used = 0;
}

static inline void MarufYTSha256Update(MarufYTSha256 *ctx, const uint8_t *data, size_t length) {
    ctx->bits += (uint64_t)length * 8u;
    while (length > 0) {
        size_t take = 64 - ctx->used;
        if (take > length) take = length;
        memcpy(ctx->block + ctx->used, data, take);
        ctx->used += take;
        data += take;
        length -= take;
        if (ctx->used == 64) {
            MarufYTSha256Compress(ctx, ctx->block);
            ctx->used = 0;
        }
    }
}

static inline void MarufYTSha256Final(MarufYTSha256 *ctx, uint8_t digest[32]) {
    uint64_t bits = ctx->bits;
    ctx->block[ctx->used++] = 0x80;
    if (ctx->used > 56) {
        memset(ctx->block + ctx->used, 0, 64 - ctx->used);
        MarufYTSha256Compress(ctx, ctx->block);
        ctx->used = 0;
    }
    memset(ctx->block + ctx->used, 0, 56 - ctx->used);
    for (int i = 0; i < 8; i++) ctx->block[56 + i] = (uint8_t)(bits >> (56 - 8 * i));
    MarufYTSha256Compress(ctx, ctx->block);
    for (int i = 0; i < 8; i++) {
        digest[i * 4] = (uint8_t)(ctx->state[i] >> 24);
        digest[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 16);
        digest[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 8);
        digest[i * 4 + 3] = (uint8_t)ctx->state[i];
    }
}

// A YouTube video ID: exactly 11 characters from [A-Za-z0-9_-].
static inline bool MarufYTIsVideoID(const char *videoID) {
    if (videoID == NULL || strlen(videoID) != 11) return false;
    for (int i = 0; i < 11; i++) {
        char c = videoID[i];
        bool ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-';
        if (!ok) return false;
    }
    return true;
}

// Writes the lowercase hex prefix of SHA-256(videoID) plus a NUL into out.
// Returns false (and an empty string) for an invalid ID, a prefix length
// outside 4..32 (the server's accepted range, with 4 as our floor), or a
// buffer that is too small.
static inline bool MarufYTSponsorHashPrefix(const char *videoID, size_t prefixLength, char *out, size_t outSize) {
    static const char hex[] = "0123456789abcdef";
    if (out != NULL && outSize > 0) out[0] = '\0';
    if (out == NULL || prefixLength < 4 || prefixLength > 32 || outSize < prefixLength + 1) return false;
    if (!MarufYTIsVideoID(videoID)) return false;
    MarufYTSha256 ctx;
    uint8_t digest[32];
    MarufYTSha256Init(&ctx);
    MarufYTSha256Update(&ctx, (const uint8_t *)videoID, 11);
    MarufYTSha256Final(&ctx, digest);
    for (size_t i = 0; i < prefixLength; i++) {
        uint8_t nibble = (i % 2 == 0) ? (digest[i / 2] >> 4) : (digest[i / 2] & 0x0f);
        out[i] = hex[nibble];
    }
    out[prefixLength] = '\0';
    return true;
}

// True when `candidate` is the video we asked about. Entries for other videos
// that merely share the prefix must be discarded (exact, case-sensitive match).
static inline bool MarufYTSponsorEntryMatches(const char *requested, const char *candidate) {
    return requested != NULL && candidate != NULL && MarufYTIsVideoID(requested) && strcmp(requested, candidate) == 0;
}

#endif
