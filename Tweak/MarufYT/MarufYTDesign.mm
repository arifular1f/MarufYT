// MarufYT — Liquid Glass design system.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

#import "MarufYTDesign.h"

#import <objc/runtime.h>

NSString *const MarufYTDepthShadowKey = @"YTKACE.Preference.Glass.DepthShadow";

CGFloat const MarufYTCapsuleShadowRadius = 18.0;
CGFloat const MarufYTCapsuleShadowOffsetY = 6.0;

static CGFloat const MarufYTShadowOpacityLight = 0.14;
static CGFloat const MarufYTShadowOpacityDark = 0.40;

static NSArray<NSString *> *MarufYTGlassPresetKeys(void) {
    return @[@"YTKACE.Preference.Tabs.Glass",
             @"YTKACE.Preference.Glass.TopBar",
             @"YTKACE.Preference.Glass.Menus",
             @"YTKACE.Preference.Glass.Notices",
             @"YTKACE.Preference.Glass.Player"];
}

NSDictionary<NSString *, id> *MarufYTPreferenceDefaults(void) {
    static NSDictionary *defaults;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        NSMutableDictionary *values = [NSMutableDictionary dictionary];
        values[MarufYTDepthShadowKey] = @YES;
        // Only where the native material exists; older systems keep upstream defaults.
        if (NSClassFromString(@"UIGlassEffect") != Nil) {
            for (NSString *key in MarufYTGlassPresetKeys()) values[key] = @YES;
        }
        defaults = [values copy];
    });
    return defaults;
}

BOOL MarufYTGlassPreferenceEnabled(NSString *key) {
    id stored = [NSUserDefaults.standardUserDefaults objectForKey:key];
    if (stored != nil) return [stored boolValue];
    return [MarufYTPreferenceDefaults()[key] boolValue];
}

#pragma mark - Tab-bar capsule depth

// A shadow-only view behind the glass capsule. The shadow is masked to the
// area outside the capsule, so it never darkens the translucent glass itself.
@interface MarufYTCapsuleDepthView : UIView
@property(nonatomic) CGRect capsuleFrame;
@property(nonatomic) CGFloat capsuleRadius;
@property(nonatomic) UIUserInterfaceStyle appliedStyle;
@end

@implementation MarufYTCapsuleDepthView

- (instancetype)initWithFrame:(CGRect)frame {
    self = [super initWithFrame:frame];
    if (self) {
        self.userInteractionEnabled = NO;
        self.backgroundColor = UIColor.clearColor;
        self.opaque = NO;
        self.isAccessibilityElement = NO;
        self.accessibilityElementsHidden = YES;
        self.accessibilityIdentifier = @"YTKACE.MarufYT.CapsuleDepth";
        CALayer *layer = self.layer;
        layer.shadowColor = UIColor.blackColor.CGColor;
        layer.shadowRadius = MarufYTCapsuleShadowRadius;
        layer.shadowOffset = CGSizeMake(0.0, MarufYTCapsuleShadowOffsetY);
        layer.shadowOpacity = 0.0;
        CAShapeLayer *mask = [CAShapeLayer layer];
        mask.fillRule = kCAFillRuleEvenOdd;
        layer.mask = mask;
        // A masked layer needs an offscreen pass; its content only changes on
        // layout/theme changes, so cache it as a bitmap instead of every frame.
        layer.shouldRasterize = YES;
        _appliedStyle = UIUserInterfaceStyleUnspecified;
    }
    return self;
}

- (void)updateForGlass:(UIView *)glass inBar:(UIView *)bar {
    CGRect capsule = glass.frame;
    CGFloat radius = glass.layer.cornerRadius;
    // Minimised (circle) and degenerate states: no extra depth layer.
    BOOL visible = CGRectGetWidth(capsule) > CGRectGetHeight(capsule) * 1.5 &&
        CGRectGetHeight(capsule) > 1.0 && !glass.hidden && glass.alpha > 0.01;
    UIUserInterfaceStyle style = bar.traitCollection.userInterfaceStyle;
    CGFloat opacity = !visible ? 0.0 :
        (style == UIUserInterfaceStyleDark ? MarufYTShadowOpacityDark : MarufYTShadowOpacityLight);

    BOOL geometryChanged = !CGRectEqualToRect(capsule, self.capsuleFrame) || radius != self.capsuleRadius;
    if (!geometryChanged && style == self.appliedStyle && self.layer.shadowOpacity == (float)opacity) return;

    [CATransaction begin];
    [CATransaction setDisableActions:YES];
    if (geometryChanged) {
        CGFloat pad = MarufYTCapsuleShadowRadius * 2.0 + fabs(MarufYTCapsuleShadowOffsetY);
        [UIView performWithoutAnimation:^{
            self.frame = CGRectInset(capsule, -pad, -pad);
        }];
        CGRect local = CGRectMake(pad, pad, CGRectGetWidth(capsule), CGRectGetHeight(capsule));
        UIBezierPath *shape = [UIBezierPath bezierPathWithRoundedRect:local cornerRadius:radius];
        self.layer.shadowPath = shape.CGPath;
        UIBezierPath *outside = [UIBezierPath bezierPathWithRect:self.bounds];
        [outside appendPath:shape];
        CAShapeLayer *mask = (CAShapeLayer *)self.layer.mask;
        mask.frame = self.bounds;
        mask.path = outside.CGPath;
        self.capsuleFrame = capsule;
        self.capsuleRadius = radius;
    }
    self.layer.shadowOpacity = (float)opacity;
    self.layer.rasterizationScale = MAX(1.0, bar.traitCollection.displayScale);
    self.appliedStyle = style;
    [CATransaction commit];
}

@end

static const void *MarufYTCapsuleDepthAssociation = &MarufYTCapsuleDepthAssociation;

void MarufYTDecorateTabCapsule(UIView *bar, UIView *glass) {
    if (bar == nil || glass == nil || glass.superview != bar) return;
    MarufYTCapsuleDepthView *depth = objc_getAssociatedObject(bar, MarufYTCapsuleDepthAssociation);
    if (!MarufYTGlassPreferenceEnabled(MarufYTDepthShadowKey)) {
        if (depth != nil) MarufYTRemoveTabCapsuleDecoration(bar);
        return;
    }
    if (depth == nil) {
        depth = [[MarufYTCapsuleDepthView alloc] initWithFrame:CGRectZero];
        objc_setAssociatedObject(bar, MarufYTCapsuleDepthAssociation, depth,
                                 OBJC_ASSOCIATION_RETAIN_NONATOMIC);
    }
    NSUInteger glassIndex = [bar.subviews indexOfObjectIdenticalTo:glass];
    NSUInteger depthIndex = [bar.subviews indexOfObjectIdenticalTo:depth];
    if (depth.superview != bar || depthIndex == NSNotFound || depthIndex + 1 != glassIndex) {
        [bar insertSubview:depth belowSubview:glass];
    }
    [depth updateForGlass:glass inBar:bar];
}

void MarufYTRemoveTabCapsuleDecoration(UIView *bar) {
    if (bar == nil) return;
    UIView *depth = objc_getAssociatedObject(bar, MarufYTCapsuleDepthAssociation);
    [depth removeFromSuperview];
    objc_setAssociatedObject(bar, MarufYTCapsuleDepthAssociation, nil,
                             OBJC_ASSOCIATION_RETAIN_NONATOMIC);
}

BOOL MarufYTIsDecorationView(UIView *view) {
    return [view isKindOfClass:MarufYTCapsuleDepthView.class];
}
