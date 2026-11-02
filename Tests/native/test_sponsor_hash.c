/* Native tests for MarufYTSponsorHash.h. Vectors were produced with Python's
 * hashlib (SHA-256) and cross-checked against the live SponsorBlock server:
 * the server returned dQw4w9WgXcQ and eXjGWlJOhWg for prefix 5f6b.
 * Copyright (c) 2026 arifular1f. MIT License; see LICENSE. */
#include <stdio.h>
#include <string.h>
#include "MarufYTSponsorHash.h"

static int failures = 0;
static int checks = 0;

#define CHECK(cond) do { checks++; if (!(cond)) { failures++; printf("FAIL line %d: %s\n", __LINE__, #cond); } } while (0)

static void hex(const uint8_t *digest, char *out) {
    static const char digits[] = "0123456789abcdef";
    for (int i = 0; i < 32; i++) { out[i * 2] = digits[digest[i] >> 4]; out[i * 2 + 1] = digits[digest[i] & 15]; }
    out[64] = '\0';
}

static void sha(const char *text, size_t repeat, char *out) {
    MarufYTSha256 ctx;
    uint8_t digest[32];
    MarufYTSha256Init(&ctx);
    for (size_t i = 0; i < repeat; i++) MarufYTSha256Update(&ctx, (const uint8_t *)text, strlen(text));
    MarufYTSha256Final(&ctx, digest);
    hex(digest, out);
}

int main(void) {
    char full[65];
    char prefix[40];

    /* SHA-256 known answers (FIPS 180-4 examples and hashlib). */
    sha("", 1, full);    CHECK(strcmp(full, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") == 0);
    sha("abc", 1, full); CHECK(strcmp(full, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") == 0);
    /* 1000 bytes: crosses block boundaries and padding. */
    sha("aaaaaaaaaa", 100, full);
    CHECK(strcmp(full, "41edece42d63e8d9bf515a9ba6932e1c20cbc9f5a5d134645adb5db1b9737ea3") == 0);
    /* 55, 56, 63, 64 byte messages exercise the padding edge cases. */
    sha("a", 55, full); CHECK(strcmp(full, "9f4390f8d30c2dd92ec9f095b65e2b9ae9b0a925a5258e241c9f1e910f734318") == 0);
    sha("a", 56, full); CHECK(strcmp(full, "b35439a4ac6f0948b6d6f9e3c6af0f5f590ce20f1bde7090ef7970686ec6738a") == 0);
    sha("a", 63, full); CHECK(strcmp(full, "7d3e74a05d7db15bce4ad9ec0658ea98e3f06eeecf16b4c6fff2da457ddc2f34") == 0);
    sha("a", 64, full); CHECK(strcmp(full, "ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb") == 0);

    /* Video ID prefixes. */
    CHECK(MarufYTSponsorHashPrefix("dQw4w9WgXcQ", 4, prefix, sizeof prefix));
    CHECK(strcmp(prefix, "5f6b") == 0);
    CHECK(MarufYTSponsorHashPrefix("eXjGWlJOhWg", 4, prefix, sizeof prefix));
    CHECK(strcmp(prefix, "5f6b") == 0);          /* real collision seen on the server */
    CHECK(MarufYTSponsorHashPrefix("aaaaaaaaaaa", 4, prefix, sizeof prefix));
    CHECK(strcmp(prefix, "28cb") == 0);
    CHECK(MarufYTSponsorHashPrefix("-_-_-_-_-_-", 4, prefix, sizeof prefix));
    CHECK(strcmp(prefix, "e7bb") == 0);
    CHECK(MarufYTSponsorHashPrefix("dQw4w9WgXcQ", 5, prefix, sizeof prefix));
    CHECK(strcmp(prefix, "5f6b0") == 0);          /* odd length uses the high nibble */
    CHECK(MarufYTSponsorHashPrefix("dQw4w9WgXcQ", 32, prefix, sizeof prefix));
    CHECK(strcmp(prefix, "5f6b0b4e201f2a7e66927abb5cadeec8") == 0);

    /* Rejections never write a partial prefix. */
    CHECK(!MarufYTSponsorHashPrefix("dQw4w9WgXcQ", 3, prefix, sizeof prefix) && prefix[0] == '\0');
    CHECK(!MarufYTSponsorHashPrefix("dQw4w9WgXcQ", 33, prefix, sizeof prefix));
    CHECK(!MarufYTSponsorHashPrefix("dQw4w9WgXcQ", 4, prefix, 4));   /* no room for NUL */
    CHECK(!MarufYTSponsorHashPrefix("short", 4, prefix, sizeof prefix));
    CHECK(!MarufYTSponsorHashPrefix("dQw4w9WgXc!", 4, prefix, sizeof prefix));
    CHECK(!MarufYTSponsorHashPrefix("dQw4w9WgXcQQ", 4, prefix, sizeof prefix));
    CHECK(!MarufYTSponsorHashPrefix("", 4, prefix, sizeof prefix));
    CHECK(!MarufYTSponsorHashPrefix(NULL, 4, prefix, sizeof prefix));
    CHECK(!MarufYTSponsorHashPrefix("dQw4w9WgXcQ", 4, NULL, 0));

    /* Entry selection: only the exact video counts. */
    CHECK(MarufYTSponsorEntryMatches("dQw4w9WgXcQ", "dQw4w9WgXcQ"));
    CHECK(!MarufYTSponsorEntryMatches("dQw4w9WgXcQ", "eXjGWlJOhWg"));
    CHECK(!MarufYTSponsorEntryMatches("dQw4w9WgXcQ", "dqw4w9wgxcq"));   /* IDs are case sensitive */
    CHECK(!MarufYTSponsorEntryMatches("dQw4w9WgXcQ", NULL));
    CHECK(!MarufYTSponsorEntryMatches(NULL, "dQw4w9WgXcQ"));
    CHECK(!MarufYTSponsorEntryMatches("not-an-id", "not-an-id"));

    printf("test_sponsor_hash: %d checks, %d failures\n", checks, failures);
    return failures == 0 ? 0 : 1;
}
