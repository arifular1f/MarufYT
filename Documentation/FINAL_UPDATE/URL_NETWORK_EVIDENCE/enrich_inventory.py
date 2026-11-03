"""Classify lexical audit evidence; never infer a connection from a string.
Only creates/updates this audit's output files, not the app or release artifacts.
"""
from pathlib import Path
import collections
import csv
import gzip
import hashlib
import ipaddress
import json
import re
import shutil
import urllib.parse

OUT=Path(__file__).resolve().parent
csv.field_size_limit(32*1024*1024)


def safer(text):
    def field(m):
        key=urllib.parse.unquote_plus(m.group(2)).lower()
        sensitive=any(s in key for s in ['token','secret','password','passwd','cookie','authorization','signature','credential','api_key','apikey','api-key','session','visitordata']) or key in ['key','sig','code','auth','pot']
        return m.group(1)+m.group(2)+'='+('[redacted]' if sensitive else m.group(3))
    return re.sub(r'([?&;])([^=&#;\s]+)=([^&#;\s]*)',field,text)


def source_map(value,kind):
    if kind=='declared-custom-scheme':
        return ('Declared inbound/open-query scheme','Info.plist CFBundleURLTypes / LSApplicationQueriesSchemes','Declaration, not an outbound request','Depends on caller/host; no transmission proved','No HTTP header implied')
    if kind.startswith('IPv'):
        return ('IP-shaped literal; may be version/mask/example','Opaque compiled/resource context; inspect occurrence offset','UNKNOWN; not probed','UNKNOWN','UNKNOWN')
    try:
        parts=urllib.parse.urlsplit(value if '://' in value else 'https://'+value);host=(parts.hostname or '').lower();path=parts.path
    except ValueError:
        return None
    if kind=='URL' and parts.scheme.lower()!='https': return None
    common_auth='No explicit Google Authorization header at this source site; ordinary per-origin session state is not runtime-tested'
    if host=='sponsor.ajay.app':
        if path.startswith('/api/branding'):
            return ('DeArrow branding','Tweak/Features/SponsorBlock/DeArrow.mm::YTKACEFetchBranding','Conditional code path when enabled; NOT observed in IPA','Full video ID; receives title/thumbnail metadata',common_auth)
        return ('SponsorBlock lookup / vote / submit route family','SponsorClient.mm:73-100 (lookup construction); SponsorMenu.mm::YTKACESponsorPost','Conditional lookup or explicit user vote/submission; NOT observed in IPA','Lookup: full ID/categories OR 4-hex hash prefix/categories. Vote/submit: contributor ID, UUID or video/segment data',common_auth)
    if host=='dearrow-thumb.ajay.app': return ('DeArrow thumbnails','DeArrow.mm:254 (thumbnail URL construction)','Conditional when replacement enabled; NOT observed in IPA','Full video ID and timestamp; receives image',common_auth)
    if host=='api.aisloplist.com': return ('AiSList reporting','AiSListReport.mm::YTKACEAiSListSubmit','Explicit report confirmation; NOT observed in IPA','Channel handle, video URL, reporter name JSON',common_auth)
    if host=='raw.githubusercontent.com' and ('Override92/AiSList' in path or kind=='domain-candidate'):
        return ('AiSList public list refresh','AiSList.mm::YTKACEAiSListDownload / YTKACEAiSListRefreshIfStale','Conditional enabled/stale refresh; NOT observed in IPA','Standard public-list GET; IP/timing visible to service',common_auth)
    if host=='youtubei.googleapis.com':
        return ('First-party playback/download/playlist API family','Streaming/TVClient.mm::YTKACETVRequest; HLSPlayback.mm::YTKACEVisionRequest; Downloads/DirectDownloader.mm::YTKACEDirectAPIRequest; PlaylistDownloader.mm::YTKACEFetchPlaylistPages','Feature-dependent code paths; NOT observed in IPA','Video/playlist/continuation, visitor and client/device context; receives player/stream/playlist data','Playlist browse may attach host Google bearer token/on-behalf-of context on fixed Google origin; others have visitor/client headers')
    if host=='i.ytimg.com':return ('Queue/playlist thumbnail URL construction','Queue/QueueHooks.mm; Downloads/PlaylistDownloader.mm','Constructed/fetched for relevant content; NOT observed in IPA','Video ID/image size; image response',common_auth)
    if host=='www.youtube.com':
        if path=='/iframe_api' or path.startswith('/s/player/'):
            return ('Player-script fetch','Streaming/TVClient.mm::YTKACETVPlayer (129-164) / YTKACETVFetch','Conditional download/playback helper; NOT observed in IPA','Player identifier/path; receives script',common_auth)
        if path.startswith('/oembed'):
            return ('Public video metadata','Queue/QueueHooks.mm::YTKACEQueueFetchFromOEmbed (282-290); Interface/AiSListReport.mm','Queue/report workflow; report metadata lookup may precede confirmation; NOT observed in IPA','Video URL/ID; receives title/channel metadata',common_auth)
        if path in ('','/'):
            return ('YouTube Origin/client-context literal','Streaming/TVClient.mm client header builder','Header/context value, not proof this root URL is fetched','Origin header constant; not itself an upload destination','Header value, not an authentication header')
    if host in ('youtube.com','youtu.be','www.youtube.com'):
        if 'yt-dlp-wins' in value:return ('Bundled EJS sample/identifier string','YTKACE.bundle/ejs; JavaScriptCore solver context','No matching network request proven for this literal','Not established','Not established')
        return ('Generated share/report link','Interface/NativeShareHooks.mm; AiSListReport.mm','URL construction/copy/share; not itself a request','Selected video/clip/post/channel/playlist link','External app/browser may use its own session; no auth header added by URL construction')
    if host=='github.com' and path.startswith('/arifular1f'):
        return ('Developer/project external link','MarufYT/Branding/MarufYTBranding.mm::MarufYTOpenURLString','Explicit user external-open action; NOT observed in IPA','Browser navigation to developer/project','Browser/session dependent, not a tweak API token')
    if host=='googlevideo.com' or host.endswith('.googlevideo.com'):
        return ('Trusted media suffix / runtime CDN family','Runtime/NetworkRules.h; Downloads/SABRDownloader.mm','Allowlist pattern; actual server URL comes from response, not this literal','Signed media URL/protobuf context, visitor/PoToken and device metadata','SABR explicit header allowlist excludes Authorization/Cookie; body still contains Google media context')
    return None


with (OUT/'COMPLETE_INVENTORY.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
authorities=collections.defaultdict(lambda:{'ids':set(),'builds':set(),'owners':set(),'urls':set()})
for row in rows:
    original=row['value'];row['value']=safer(original)
    if row['value']!=original:row['redacted']='True'
    own='MarufYT (' in row['owners']
    mapped=source_map(row['value'],row['kind']) if own or row['kind']=='declared-custom-scheme' else None
    if mapped:
        row['classification'],row['function'],row['reachability'],row['dataTransmitted'],row['authentication']=mapped
        if 'Original host' in row['owners'] and own:
            row['function']+='; ORIGINAL HOST FUNCTION UNKNOWN'
    elif row['kind']=='URL':
        try:query=urllib.parse.parse_qs(urllib.parse.urlsplit(row['value']).query,keep_blank_values=True)
        except ValueError:query={}
        row['dataTransmitted']='Runtime body/data UNKNOWN. Literal query names: '+(', '.join(sorted(query)) if query else 'none')
        if any(x in row['value'].lower() for x in ['id_type=idfa','/pagead/','/conversion/','/collect','analytics','crashlytics']):
            row['classification']='Advertising/telemetry-shaped literal/template; activity not proved'
        elif any(x in row['value'].lower() for x in ['www.w3.org','/dtds/','ns.adobe.com','crl.','ocsp.','/appleca','repository.swisssign']):
            row['classification']='Standards/schema/certificate metadata candidate; raw DER matches may include trailing bytes'
    if row['kind']=='URL':
        try:
            p=urllib.parse.urlsplit(row['value']);host=(p.hostname or '').lower()
            if not host or '%' in host or '[' in host or ']' in host:continue
        except ValueError:continue
        authority=authorities[host];authority['ids'].add(row['id']);authority['urls'].add(row['value'])
        authority['builds'].update(['Latest','Stable'] if row['comparison']=='Common' else [row['comparison'].split('-')[0]])
        authority['owners'].add(row['owners'])

def write(name,columns,data):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(data)
write('COMPLETE_INVENTORY.csv',list(rows[0]),rows)
# Reapply query-name decoding protection to occurrence copies as well.
temp=OUT/'OCCURRENCES.protected.csv'
with (OUT/'OCCURRENCES.csv').open(encoding='utf-8-sig',newline='') as old,temp.open('w',encoding='utf-8-sig',newline='') as new:
    reader=csv.DictReader(old);writer=csv.DictWriter(new,fieldnames=reader.fieldnames);writer.writeheader()
    for row in reader:
        value=safer(row['value'])
        if value!=row['value']:row['redacted']='True'
        row['value']=value;writer.writerow(row)
temp.replace(OUT/'OCCURRENCES.csv')

authority_rows=[]
for host,item in sorted(authorities.items()):
    authority_rows.append({'host':host,'comparison':'Common' if len(item['builds'])==2 else next(iter(item['builds']))+'-only',
        'owners':'; '.join(sorted(item['owners'])),'URLRecordIDs':'; '.join(sorted(item['ids'])),
        'URIExamples':'; '.join(sorted(item['urls'])),'reachability':'Only literal authority evidence; see per-record source map; not a connection observation'})
write('URL_AUTHORITY_DOMAINS.csv',list(authority_rows[0]),authority_rows)
write('DOMAIN_CLASSIFICATION.csv',list(rows[0])+['alsoURLAuthority'],[{**r,'alsoURLAuthority':r['value'] in authorities} for r in rows if r['kind']=='domain-candidate'])
write('IP_LITERAL_INVENTORY.csv',list(rows[0]),[r for r in rows if r['kind'].startswith('IPv')])
write('SCHEME_INVENTORY.csv',list(rows[0]),[r for r in rows if r['kind'] in ['custom-URI','declared-custom-scheme']])
write('VERSION_ONLY_URLS.csv',list(rows[0]),[r for r in rows if r['kind']=='URL' and r['comparison']!='Common'])
write('MARUFYT_COMPONENT_URLS.csv',list(rows[0]),[r for r in rows if r['kind']=='URL' and 'MarufYT (' in r['owners']])

summary=json.loads((OUT/'SUMMARY.json').read_text())
summary.update({'URLSchemeCounts':dict(collections.Counter(r['value'].split(':',1)[0].lower() for r in rows if r['kind']=='URL')),
    'URLAuthorityHostCount':len(authorities),'versionOnlyURLCount':sum(r['kind']=='URL' and r['comparison']!='Common' for r in rows),
    'MarufYTComponentURLCount':sum(r['kind']=='URL' and 'MarufYT (' in r['owners'] for r in rows),
    'redactedRecordsAfterDecodedQueryNameProtection':sum(r['redacted']=='True' for r in rows),
    'dataSafety':'Credential-shaped URL values redacted, including percent-encoded query names. Raw hashes retained; no surrounding binary strings dumped.',
    'functionMapping':'Known tweak call sites annotated; original host/library function attribution remains UNKNOWN unless source evidence exists.',
    'observationNote':'Extractor sent zero requests. Separate CONTROLLED_NETWORK_OBSERVATIONS.json records exactly five GET public-fixture probes, not app traffic.'})
(OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Enriched',len(rows),'records;',len(authorities),'URL authority hosts;',summary['URLSchemeCounts'],flush=True)
