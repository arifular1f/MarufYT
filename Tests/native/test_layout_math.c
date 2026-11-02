// MarufYT layout and preference-resolution tests.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// Built with the host C compiler (CI and Tests/test_native_layout_math.py):
//   cc -std=c11 -Wall -Wextra -Werror -I Tweak/MarufYT/Design Tests/native/test_layout_math.c -lm
//
// These test the pure geometry and the preference decisions the tweak uses.
// They do not run UIKit and are not a substitute for testing on a device.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "MarufYTLayoutMath.h"

static int failures = 0;
static int checks = 0;

#define CHECK(condition, ...)                                              \
    do {                                                                   \
        checks++;                                                          \
        if (!(condition)) {                                                \
            failures++;                                                    \
            printf("FAIL %s:%d: ", __FILE__, __LINE__);                    \
            printf(__VA_ARGS__);                                           \
            printf("\n");                                                  \
        }                                                                  \
    } while (0)

static bool approx(double a, double b) { return fabs(a - b) < 1e-9; }

static bool inside(MarufYTRect inner, double width, double height) {
    return inner.x >= -1e-9 && inner.y >= -1e-9 && inner.width >= 0.0 && inner.height >= 0.0 &&
           inner.x + inner.width <= width + 1e-9 && inner.y + inner.height <= height + 1e-9;
}

static bool same_rect(MarufYTRect a, MarufYTRect b) {
    return approx(a.x, b.x) && approx(a.y, b.y) && approx(a.width, b.width) && approx(a.height, b.height);
}

// ---------------------------------------------------------------- preferences

static void test_tab_mode_resolution(void) {
    const long simple = MarufYTTabModeSimple;
    CHECK(MarufYTResolveTabMode(false, 0, false, false, simple) == simple, "nothing stored -> simple default");
    for (long stored = 0; stored <= 3; stored++) {
        CHECK(MarufYTResolveTabMode(true, stored, false, false, simple) == stored, "stored %ld must win", stored);
        CHECK(MarufYTResolveTabMode(true, stored, true, true, simple) == stored, "stored %ld beats legacy on", stored);
        CHECK(MarufYTResolveTabMode(true, stored, true, false, simple) == stored, "stored %ld beats legacy off", stored);
    }
    CHECK(MarufYTResolveTabMode(true, 0, false, false, simple) == MarufYTTabModeDefault,
          "an explicit Default (0) is kept, not replaced by the new default");
    CHECK(MarufYTResolveTabMode(false, 0, true, true, simple) == MarufYTTabModeCapsule, "legacy on -> capsule");
    CHECK(MarufYTResolveTabMode(false, 0, true, false, simple) == MarufYTTabModeDefault, "legacy off -> default");
    CHECK(MarufYTResolveTabMode(true, 9, false, false, simple) == simple, "out-of-range stored value ignored");
    CHECK(MarufYTResolveTabMode(true, -1, true, true, simple) == MarufYTTabModeCapsule, "negative stored falls to legacy");
    // Repeated resolution with the same inputs never changes.
    long first = MarufYTResolveTabMode(true, 2, true, true, simple);
    for (int i = 0; i < 1000; i++) CHECK(MarufYTResolveTabMode(true, 2, true, true, simple) == first, "unstable");
}

// -------------------------------------------------------------------- capsule

static MarufYTRect legacy_capsule(double barWidth, double barHeight, double safeBottom, int tabs, bool expanded) {
    // The formula used before Phase 3 (YTKACEApplyPivotBarGlass), kept to document the defect.
    double itemHeight = barHeight - safeBottom;
    double glassHeight = fmax(itemHeight, 44.0) + 7.0 * 2.0;
    double glassTop = fmin(0.0, barHeight - glassHeight - 4.0);
    double margin = expanded ? 14.0 : 21.0;
    double width = barWidth - margin * 2.0;
    if (tabs > 0 && tabs <= 4) width = fmin(width, 86.0 * tabs + 16.0);
    MarufYTRect r = {(barWidth - width) * 0.5, glassTop, width, glassHeight};
    return r;
}

static void test_capsule_geometry(void) {
    // iPhone 15 Pro Max steady state: 430 pt wide bar, 83 pt tall (49 + 34 home indicator).
    MarufYTRect steady = MarufYTCapsuleFrame(430.0, 83.0, 49.0, 5, false);
    CHECK(approx(steady.x, 21.0) && approx(steady.y, 0.0) && approx(steady.width, 388.0) && approx(steady.height, 63.0),
          "steady frame %.1f %.1f %.1f %.1f", steady.x, steady.y, steady.width, steady.height);
    MarufYTRect old_steady = legacy_capsule(430.0, 83.0, 34.0, 5, false);
    CHECK(same_rect(steady, old_steady), "must match the previous layout when everything has settled");

    // Previous layout while the safe-area inset is still 0: taller, and above the bar.
    MarufYTRect old_transient = legacy_capsule(430.0, 83.0, 0.0, 5, false);
    CHECK(old_transient.y < -1.0, "documenting the defect: legacy capsule starts %.1f pt above the bar", old_transient.y);
    CHECK(old_transient.height > steady.height + 20.0, "documenting the defect: legacy capsule grows to %.1f", old_transient.height);
    // The new frame does not depend on the inset at all, so it cannot jump when the inset arrives.
    for (int pass = 0; pass < 200; pass++) {
        MarufYTRect again = MarufYTCapsuleFrame(430.0, 83.0, 49.0, 5, false);
        CHECK(same_rect(again, steady), "capsule moved on pass %d", pass);
    }

    // Sweep: always finite, non-negative and inside the bar.
    for (double width = 280.0; width <= 1100.0; width += 17.0) {
        for (double height = 30.0; height <= 140.0; height += 9.0) {
            for (double item = -5.0; item <= 70.0; item += 7.0) {
                for (int tabs = 0; tabs <= 8; tabs++) {
                    for (int expanded = 0; expanded <= 1; expanded++) {
                        MarufYTRect f = MarufYTCapsuleFrame(width, height, item, tabs, expanded != 0);
                        CHECK(isfinite(f.x) && isfinite(f.y) && isfinite(f.width) && isfinite(f.height), "non-finite");
                        CHECK(inside(f, width, height), "capsule outside bar w=%.0f h=%.0f item=%.0f tabs=%d", width, height, item, tabs);
                    }
                }
            }
        }
    }
    MarufYTRect nan = MarufYTCapsuleFrame(NAN, INFINITY, NAN, 5, false);
    CHECK(isfinite(nan.x) && isfinite(nan.width) && isfinite(nan.height), "invalid input must not produce NaN");
    // No bar-height overflow even with no safe area (49 pt bar).
    MarufYTRect small_bar = MarufYTCapsuleFrame(390.0, 49.0, 49.0, 5, false);
    CHECK(inside(small_bar, 390.0, 49.0), "capsule must fit a 49 pt bar");
}

static void test_tab_slots(void) {
    for (int count = 1; count <= 6; count++) {
        MarufYTRect glass = MarufYTCapsuleFrame(430.0, 83.0, 49.0, count, false);
        MarufYTTabGeometry geometry = MarufYTTabSlots(glass, count);
        double previous_max = -1.0;
        for (int index = 0; index < count; index++) {
            MarufYTRect frame = MarufYTTabItemFrame(glass, geometry, index, 49.0);
            CHECK(frame.width > 20.0, "slot %d too narrow (%.1f)", index, frame.width);
            CHECK(frame.x >= glass.x - 1e-9 && frame.x + frame.width <= glass.x + glass.width + 1e-9,
                  "slot %d/%d leaves the capsule", index, count);
            if (index > 0) CHECK(approx(frame.x, previous_max), "slots %d/%d must touch exactly (gap or overlap)", index, count);
            previous_max = frame.x + frame.width;
            // Centred vertically.
            CHECK(approx(frame.y + frame.height * 0.5, glass.y + glass.height * 0.5), "slot %d not centred", index);
            // Idempotent under repeated passes and pixel alignment.
            for (int pass = 0; pass < 50; pass++) {
                MarufYTRect again = MarufYTTabItemFrame(glass, geometry, index, 49.0);
                CHECK(same_rect(again, frame), "slot moved on pass %d", pass);
            }
            double aligned = MarufYTPixelAlign(frame.x, 3.0);
            CHECK(approx(MarufYTPixelAlign(aligned, 3.0), aligned), "pixel alignment must be idempotent");
        }
    }
}

// ------------------------------------------------------------ MarufYT tab item

static bool outputs_equal(MarufYTReplacementOutput a, MarufYTReplacementOutput b) {
    return approx(a.iconCenterX, b.iconCenterX) && approx(a.iconCenterY, b.iconCenterY) && approx(a.iconSize, b.iconSize) &&
           approx(a.labelMinY, b.labelMinY) && approx(a.labelHeight, b.labelHeight) && a.labelVisible == b.labelVisible;
}

typedef struct {
    double iconMidY;
    double labelMinY;
    double labelHeight;
} NativeViews;

static MarufYTReplacementOutput legacy_replacement(NativeViews native, double width, double height, bool hideLabel) {
    // The pre-Phase-3 rule: anchor to the native icon and label frames as they are right now.
    MarufYTReplacementOutput out;
    double size = fmin(24.0, fmin(width, height));
    double textHeight = 12.0, gap = 2.0;
    double stack = fmin(height, size + gap + textHeight);
    double top = height * 0.5 - stack * 0.5;
    bool imageAnchor = native.iconMidY > 0.0, textAnchor = native.labelHeight > 0.0;
    out.iconSize = size;
    out.iconCenterX = width * 0.5;
    out.iconCenterY = imageAnchor ? native.iconMidY : (hideLabel ? height * 0.5 : top + size * 0.5);
    if (hideLabel) out.iconCenterY = height * 0.5;
    out.labelMinY = textAnchor ? native.labelMinY : fmin(height - textHeight, top + size + gap);
    out.labelHeight = textHeight;
    out.labelVisible = !hideLabel;
    return out;
}

static void test_replacement_tab(void) {
    const double width = 78.0, height = 49.0;
    // Native tab: icon centre 18 from the top (icon 6...30), label 31...43.
    MarufYTReplacementInput in;
    memset(&in, 0, sizeof in);
    in.width = width;
    in.height = height;
    in.hideLabel = false;
    in.haveReference = true;
    in.refHeight = 49.0;
    in.refIconCenterY = 18.0;
    in.refLabelMinY = 31.0;
    in.refLabelHeight = 12.0;
    in.labelLineHeight = 12.0;
    MarufYTReplacementOutput with_label = MarufYTReplacementTabLayout(in);
    CHECK(approx(with_label.iconCenterY, 18.0) && approx(with_label.labelMinY, 31.0),
          "MarufYT tab must sit on the sibling's baselines (%.1f / %.1f)", with_label.iconCenterY, with_label.labelMinY);
    CHECK(with_label.iconCenterY + with_label.iconSize * 0.5 <= with_label.labelMinY + 1e-9,
          "icon must not overlap the label");

    // Repeated passes: a fixed point.
    for (int pass = 0; pass < 500; pass++) {
        CHECK(outputs_equal(MarufYTReplacementTabLayout(in), with_label), "replacement tab drifted on pass %d", pass);
    }

    // The defect: the old rule anchors to the native views, which the host moves once MarufYT blanks them.
    NativeViews before_blank = {18.0, 31.0, 12.0};   // native label still laid out
    NativeViews after_blank = {24.5, 24.5, 0.0};     // host recentred the icon, collapsed the label
    MarufYTReplacementOutput pass_one = legacy_replacement(before_blank, width, height, false);
    MarufYTReplacementOutput pass_two = legacy_replacement(after_blank, width, height, false);
    CHECK(!outputs_equal(pass_one, pass_two), "documenting the defect: the old rule gives different results for the same tab");
    CHECK(pass_two.iconCenterY + pass_two.iconSize * 0.5 > pass_two.labelMinY,
          "documenting the defect: after the host relayout the old icon (%.1f..%.1f) overlaps the label at %.1f",
          pass_two.iconCenterY - 12.0, pass_two.iconCenterY + 12.0, pass_two.labelMinY);
    // The new rule ignores those views entirely, so both passes agree.
    MarufYTReplacementOutput new_one = MarufYTReplacementTabLayout(in);
    MarufYTReplacementOutput new_two = MarufYTReplacementTabLayout(in);
    CHECK(outputs_equal(new_one, new_two), "new rule differs between passes");

    // Labels hidden: icon exactly centred, no label.
    in.hideLabel = true;
    MarufYTReplacementOutput hidden = MarufYTReplacementTabLayout(in);
    CHECK(approx(hidden.iconCenterY, height * 0.5) && !hidden.labelVisible, "hidden label layout");
    in.hideLabel = false;

    // No sibling reference: fallback stack is inside the bounds and icon above label.
    in.haveReference = false;
    MarufYTReplacementOutput fallback = MarufYTReplacementTabLayout(in);
    CHECK(fallback.iconCenterY - fallback.iconSize * 0.5 >= -1e-9, "fallback icon above the top");
    CHECK(fallback.labelMinY + fallback.labelHeight <= height + 1e-9, "fallback label below the bottom");
    CHECK(fallback.iconCenterY + fallback.iconSize * 0.5 <= fallback.labelMinY + 1e-9, "fallback overlap");

    // Sweep of item sizes and references: always inside, never overlapping when a label shows.
    for (double w = 40.0; w <= 130.0; w += 10.0) {
        for (double h = 30.0; h <= 90.0; h += 6.0) {
            for (int ref = 0; ref <= 1; ref++) {
                in.width = w;
                in.height = h;
                in.haveReference = ref != 0;
                MarufYTReplacementOutput o = MarufYTReplacementTabLayout(in);
                CHECK(o.iconCenterY - o.iconSize * 0.5 >= -1e-9 && o.iconCenterY + o.iconSize * 0.5 <= h + 1e-9,
                      "icon outside item w=%.0f h=%.0f", w, h);
                CHECK(o.labelMinY >= -1e-9 && o.labelMinY + o.labelHeight <= h + 1e-9, "label outside item");
            }
        }
    }
    in.refHeight = 0.0;
    in.haveReference = true;
    in.width = width;
    in.height = height;
    MarufYTReplacementOutput bad_reference = MarufYTReplacementTabLayout(in);
    CHECK(isfinite(bad_reference.iconCenterY), "invalid reference must fall back");
}

static void test_label_policy(void) {
    CHECK(MarufYTShouldHideReplacementLabel(true, false, 4, 4), "user preference hides");
    CHECK(MarufYTShouldHideReplacementLabel(false, true, 4, 4), "host item flag hides");
    CHECK(MarufYTShouldHideReplacementLabel(false, false, 4, 0), "all native labels hidden -> follow the host");
    CHECK(!MarufYTShouldHideReplacementLabel(false, false, 4, 4), "native labels shown -> show ours");
    CHECK(!MarufYTShouldHideReplacementLabel(false, false, 4, 1), "some native labels shown -> show ours");
    CHECK(!MarufYTShouldHideReplacementLabel(false, false, 0, 0), "no siblings measured -> do not guess");
}

int main(void) {
    test_tab_mode_resolution();
    test_capsule_geometry();
    test_tab_slots();
    test_replacement_tab();
    test_label_policy();
    printf("%d checks, %d failures\n", checks, failures);
    return failures == 0 ? 0 : 1;
}
