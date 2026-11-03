"""A few authorized GET-only public-fixture probes, not IPA/iPhone traffic.
No cookies/authentication/proxies, API keys, POSTs, or arbitrary inventory hosts.
"""
from pathlib import Path
import hashlib
import json
import ssl
import urllib.parse
import urllib.request
import urllib.error

OUT = Path(__file__).resolve().parent
VIDEO = 'dQw4w9WgXcQ'  # Public known-answer fixture, not user's viewing history.
PREFIX = hashlib.sha256(VIDEO.encode()).hexdigest()[:4]
CASES = [
    ('SponsorBlock normal public fixture', 'https://sponsor.ajay.app/api/skipSegments?' + urllib.parse.urlencode({'videoID':VIDEO,'categories':'["sponsor"]'})),
    ('SponsorBlock private prefix public fixture', 'https://sponsor.ajay.app/api/skipSegments/' + PREFIX + '?' + urllib.parse.urlencode({'categories':'["sponsor"]'})),
    ('YouTube public oEmbed fixture', 'https://www.youtube.com/oembed?' + urllib.parse.urlencode({'url':'https://www.youtube.com/watch?v='+VIDEO,'format':'json'})),
    ('AiSList public block list', 'https://raw.githubusercontent.com/Override92/AiSList/main/AiSList/aislist_blocklist.txt'),
    ('AiSList public warning list', 'https://raw.githubusercontent.com/Override92/AiSList/main/AiSList/aislist_warnlist.txt'),
]

results=[]
for label,url in CASES:
    hops=[]; allowed=urllib.parse.urlsplit(url).hostname
    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,request,fp,code,msg,headers,newurl):
            parsed=urllib.parse.urlsplit(newurl)
            hops.append({'status':code,'destination':newurl,'followed':False})
            if parsed.scheme!='https' or parsed.hostname!=allowed or parsed.username or parsed.password or parsed.port not in (None,443) or len(hops)>3:
                raise urllib.error.URLError('Redirect rejected by probe boundary')
            hops[-1]['followed']=True
            return super().redirect_request(request,fp,code,msg,headers,newurl)
    context=ssl.create_default_context()
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPSHandler(context=context),Redirect())
    row={'label':label,'url':url,'client':'Windows Python urllib audit fixture; not MarufYT/iPhone',
         'method':'GET','authorizationSent':False,'cookiesSent':False,'apiKeySent':False,
         'redirects':hops,'defaultCertificateValidation':True}
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'MarufYT-URL-Audit/1.0','Accept':'application/json, text/plain;q=0.9'})
        with opener.open(request,timeout=20) as response:
            row['status']=response.status
            row['finalURL']=response.url
            row['contentType']=response.headers.get('Content-Type')
            data=response.read(1024*1024+1)
            row['bytesRead']=len(data);row['bodyTruncated']=len(data)>1024*1024
            row['bodySHA256']=hashlib.sha256(data).hexdigest()
            try:
                obj=json.loads(data)
                row['jsonShape']=type(obj).__name__
                if isinstance(obj,list):row['arrayEntries']=len(obj)
            except ValueError:pass
    except urllib.error.HTTPError as error:
        row['status']=error.code;row['errorClass']='HTTPError';error.close()
    except Exception as error:
        row['status']=None;row['errorClass']=type(error).__name__;row['error']=str(error)[:240]
    results.append(row)
    print(label, row.get('status'),row.get('errorClass','response'),flush=True)
(OUT/'CONTROLLED_NETWORK_OBSERVATIONS.json').write_text(json.dumps({'clientDate':'2026-11-03 Asia/Kuala_Lumpur','results':results,
    'limits':['No app execution, iPhone packet capture, account token, cookie, POST/report/vote, or arbitrary extracted host probe.',
              'Only these allowlisted GET public fixtures were requested; no response body or Set-Cookie is persisted.',
              'Success proves reachability from this audit environment at observation time, not app invocation, iOS TLS or future availability.']},indent=2)+'\n')
