// MarufYT — pure layout and preference-resolution functions.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.
//
// Header-only C with no UIKit or Foundation dependency. The tweak includes it
// for its tab-bar geometry and preference decisions; Tests/native compiles
// the same file with the host C compiler and checks it, because there is no
// iOS test runner in CI. Every function is a pure function of its inputs, so
// repeated layout passes with the same inputs always give the same result.

#ifndef MARUFYT_LAYOUT_MATH_H
#define MARUFYT_LAYOUT_MATH_H

#include <math.h>
#include <stdbool.h>

typedef struct {
    double x;
    double y;
    double width;
    double height;
} MarufYTRect;

/* ---- Helpers ---- */

static inline double MarufYTFinite(double value, double fallback) {
    return isfinite(value) ? value : fallback;
}

static inline double MarufYTClamp(double value, double low, double high) {
    return value < low ? low : (value > high ? high : value);
}

// Rounds to a whole device pixel. Idempotent: align(align(v)) == align(v).
static inline double MarufYTPixelAlign(double value, double scale) {
    return scale > 0.0 ? round(value * scale) / scale : value;
}

/* ---- Tab bar mode ---- */

// Values of YTKACE.Preference.Tabs.GlassMode (unchanged from upstream).
enum {
    MarufYTTabModeDefault = 0,    // leave YouTube's own bar as it is
    MarufYTTabModeCapsule = 1,    // MarufYT Liquid Glass capsule (optional)
    MarufYTTabModeHostGlass = 2,  // force YouTube's own Liquid Glass bar
    MarufYTTabModeSimple = 3      // YouTube's classic docked bar (MarufYT default)
};

// A stored choice always wins. A stored value outside 0...3 is ignored. The
// older boolean switch comes next. With nothing stored, `unsetDefault` is
// used. Nothing is ever written, so no user choice can be changed here.
static inline long MarufYTResolveTabMode(bool hasStored, long stored,
                                         bool hasLegacy, bool legacyEnabled,
                                         long unsetDefault) {
    if (hasStored && stored >= MarufYTTabModeDefault && stored <= MarufYTTabModeSimple) return stored;
    if (hasLegacy) return legacyEnabled ? MarufYTTabModeCapsule : MarufYTTabModeDefault;
    return unsetDefault;
}

/* ---- Capsule geometry (optional MarufYT Liquid Glass mode) ---- */

// The capsule is laid out inside the tab bar's own bounds. It depends on the
// bar size and the host's item height only. It deliberately does not use the
// bottom safe-area inset: that inset is 0 for a moment while the host is
// still laying out, and a formula that includes it makes the capsule grow
// past the top of the bar and then jump when the inset arrives.
static inline MarufYTRect MarufYTCapsuleFrame(double barWidth, double barHeight,
                                              double itemHeight, int tabCount, bool expanded) {
    barWidth = fmax(MarufYTFinite(barWidth, 0.0), 0.0);
    barHeight = fmax(MarufYTFinite(barHeight, 0.0), 0.0);
    itemHeight = fmax(MarufYTFinite(itemHeight, 0.0), 0.0);
    const double minimumTarget = 44.0;
    const double verticalPadding = 7.0;
    double height = fmin(fmax(itemHeight, minimumTarget) + verticalPadding * 2.0, barHeight);
    double margin = expanded ? 14.0 : 21.0;
    double width = fmax(barWidth - margin * 2.0, 0.0);
    if (tabCount >= 1 && tabCount <= 4) width = fmin(width, 86.0 * (double)tabCount + 16.0);
    MarufYTRect frame;
    frame.x = (barWidth - width) * 0.5;
    frame.y = 0.0;
    frame.width = width;
    frame.height = height;
    return frame;
}

typedef struct {
    double start;
    double pitch;
    double overlap;
} MarufYTTabGeometry;

static inline MarufYTTabGeometry MarufYTTabSlots(MarufYTRect glass, int count) {
    MarufYTTabGeometry geometry;
    geometry.overlap = count <= 4 ? 8.0 : 16.0;
    geometry.pitch = count <= 0 ? 0.0 : fmax((glass.width - 8.0 - geometry.overlap) / (double)count, 0.0);
    geometry.start = glass.x + 4.0;
    return geometry;
}

// Frame of tab `index`, centred vertically in the capsule. A function of the
// index, not of any item's current position, so a host layout pass that moves
// the items cannot change where the next pass puts them.
static inline MarufYTRect MarufYTTabItemFrame(MarufYTRect glass, MarufYTTabGeometry geometry,
                                              int index, double itemHeight) {
    MarufYTRect frame;
    frame.x = geometry.start + geometry.overlap * 0.5 + geometry.pitch * (double)index;
    frame.y = glass.y + (glass.height - itemHeight) * 0.5;
    frame.width = geometry.pitch;
    frame.height = itemHeight;
    return frame;
}

/* ---- The MarufYT tab (injected item) ---- */

// True when the MarufYT tab should not draw its own label. It follows the
// host: the user's own "hide tab labels" setting, the host's per-item
// `hideLabel` flag (YouTube 21.43.5 and later), or every native sibling tab
// showing no label (YouTube's icon-only layout).
static inline bool MarufYTShouldHideReplacementLabel(bool preferenceHidesLabels, bool itemHidesLabel,
                                                     int siblingsConsidered, int siblingsShowingLabel) {
    if (preferenceHidesLabels || itemHidesLabel) return true;
    return siblingsConsidered > 0 && siblingsShowingLabel == 0;
}

typedef struct {
    double width;
    double height;
    bool hideLabel;
    bool haveReference;      // a native sibling tab with a visible label was measured
    double refHeight;        // that sibling's height
    double refIconCenterY;   // its icon centre, measured from its own top
    double refLabelMinY;     // its label top, measured from its own top
    double refLabelHeight;
    double labelLineHeight;  // line height of the MarufYT label's font
} MarufYTReplacementInput;

typedef struct {
    double iconCenterX;
    double iconCenterY;
    double iconSize;
    double labelMinY;
    double labelHeight;
    bool labelVisible;
} MarufYTReplacementOutput;

// Places the MarufYT tab's icon and label. Positions come from the tab's own
// bounds and from a *native sibling's* measured geometry, never from views
// MarufYT has already changed. Pure, so it is a fixed point.
static inline MarufYTReplacementOutput MarufYTReplacementTabLayout(MarufYTReplacementInput input) {
    MarufYTReplacementOutput output;
    double width = fmax(MarufYTFinite(input.width, 0.0), 0.0);
    double height = fmax(MarufYTFinite(input.height, 0.0), 0.0);
    double size = fmin(24.0, fmin(width, height));
    output.iconSize = size;
    output.iconCenterX = width * 0.5;
    if (input.hideLabel) {
        output.iconCenterY = height * 0.5;
        output.labelVisible = false;
        output.labelHeight = 0.0;
        output.labelMinY = height;
        return output;
    }
    output.labelVisible = true;
    if (input.haveReference && isfinite(input.refHeight) && input.refHeight > 0.0 &&
        isfinite(input.refIconCenterY) && isfinite(input.refLabelMinY) && isfinite(input.refLabelHeight)) {
        double scale = height / input.refHeight;
        output.labelHeight = fmin(fmax(input.refLabelHeight, 0.0), height);
        output.iconCenterY = MarufYTClamp(input.refIconCenterY * scale, size * 0.5, height - size * 0.5);
        output.labelMinY = MarufYTClamp(input.refLabelMinY * scale, 0.0, height - output.labelHeight);
        return output;
    }
    double textHeight = fmin(ceil(fmax(MarufYTFinite(input.labelLineHeight, 12.0), 0.0)), height);
    double gap = 2.0;
    double stack = fmin(height, size + gap + textHeight);
    double top = height * 0.5 - stack * 0.5;
    output.iconCenterY = top + size * 0.5;
    output.labelHeight = textHeight;
    output.labelMinY = fmin(height - textHeight, top + size + gap);
    return output;
}

#endif
