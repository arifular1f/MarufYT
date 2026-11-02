// MarufYT — About, credits and licences page.
// Copyright (c) 2026 arifular1f. MIT License; see LICENSE.

#import "MarufYTBranding.h"
#import "../Runtime/Localization.h"
#import "../YTKACE.h"

#import <UIKit/UIKit.h>

@interface MarufYTCreditsController : UITableViewController
@property(nonatomic, copy) NSArray<NSString *> *sectionTitles;
@property(nonatomic, copy) NSArray<NSArray<NSDictionary<NSString *, NSString *> *> *> *sections;
@end

@implementation MarufYTCreditsController

- (instancetype)init {
    self = [super initWithStyle:UITableViewStyleInsetGrouped];
    if (self) {
        self.title = YTKACELocalized(@"Credits");
        NSString *version = [NSString stringWithFormat:@"%@ %@", MarufYTProductName, YTKACEVersion];
        self.sectionTitles = @[MarufYTProductName, YTKACELocalized(@"Built on"),
                               YTKACELocalized(@"Third-party components")];
        self.sections = @[
            @[
                @{@"title": version, @"detail": @"MIT", @"symbol": @"sparkles"},
                @{@"title": MarufYTDeveloperName, @"detail": YTKACELocalized(@"Developer"),
                  @"symbol": @"person.crop.circle", @"url": MarufYTDeveloperURLString},
                @{@"title": YTKACELocalized(@"Repository"), @"detail": @"github.com/arifular1f/MarufYT",
                  @"symbol": @"chevron.left.forwardslash.chevron.right", @"url": MarufYTRepositoryURLString}
            ],
            @[
                @{@"title": [NSString stringWithFormat:@"%@ by %@", MarufYTUpstreamName, MarufYTUpstreamAuthor],
                  @"detail": @"MIT", @"symbol": @"shippingbox", @"url": MarufYTUpstreamURLString}
            ],
            @[
                @{@"title": @"FFmpeg", @"detail": @"LGPL", @"symbol": @"film", @"url": @"https://ffmpeg.org/legal.html"},
                @{@"title": @"SponsorBlock / DeArrow data", @"detail": @"CC BY-NC-SA 4.0",
                  @"symbol": @"forward.end", @"url": @"https://sponsor.ajay.app/"},
                @{@"title": @"yt-dlp EJS solver", @"detail": @"Unlicense",
                  @"symbol": @"curlybraces", @"url": @"https://github.com/yt-dlp/ejs"},
                @{@"title": @"YTPlaybackFix by Mark02", @"detail": @"MIT",
                  @"symbol": @"wrench.and.screwdriver", @"url": @"https://github.com/Mark02-2012/YTPlaybackFix"},
                @{@"title": @"YTLiquidGlass ideas by UltraGeek0102", @"detail": YTKACELocalized(@"With permission"),
                  @"symbol": @"drop", @"url": @"https://github.com/UltraGeek0102/YTLiquidGlassEXTRA"},
                @{@"title": @"meriyah · astring", @"detail": @"ISC · MIT", @"symbol": @"doc.text"}
            ]
        ];
    }
    return self;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    (void)tableView;
    return (NSInteger)self.sections.count;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    (void)tableView;
    return (NSInteger)self.sections[(NSUInteger)section].count;
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    (void)tableView;
    return self.sectionTitles[(NSUInteger)section];
}

- (NSString *)tableView:(UITableView *)tableView titleForFooterInSection:(NSInteger)section {
    (void)tableView;
    if (section != (NSInteger)self.sections.count - 1) return nil;
    return YTKACELocalized(@"Full licence texts are in LICENSE and THIRD_PARTY_NOTICES.md in the repository.");
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    static NSString *const identifier = @"YTKACE.MarufYT.Credit";
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:identifier];
    if (cell == nil) {
        cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleValue1 reuseIdentifier:identifier];
    }
    NSDictionary<NSString *, NSString *> *row = self.sections[(NSUInteger)indexPath.section][(NSUInteger)indexPath.row];
    cell.textLabel.text = row[@"title"];
    cell.textLabel.font = [UIFont systemFontOfSize:16.0 weight:UIFontWeightMedium];
    cell.detailTextLabel.text = row[@"detail"];
    cell.detailTextLabel.textColor = UIColor.secondaryLabelColor;
    cell.imageView.image = [UIImage systemImageNamed:row[@"symbol"]];
    cell.imageView.tintColor = UIColor.labelColor;
    BOOL link = row[@"url"].length != 0;
    cell.accessoryType = link ? UITableViewCellAccessoryDisclosureIndicator : UITableViewCellAccessoryNone;
    cell.selectionStyle = link ? UITableViewCellSelectionStyleDefault : UITableViewCellSelectionStyleNone;
    return cell;
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    [tableView deselectRowAtIndexPath:indexPath animated:YES];
    NSString *url = self.sections[(NSUInteger)indexPath.section][(NSUInteger)indexPath.row][@"url"];
    if (url.length != 0) MarufYTOpenURLString(url);
}

@end

UIViewController *MarufYTMakeCreditsController(void) {
    return [MarufYTCreditsController new];
}
