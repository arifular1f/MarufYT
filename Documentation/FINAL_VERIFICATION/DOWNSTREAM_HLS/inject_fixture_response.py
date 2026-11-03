"""Optional mitmproxy test-traffic addon; not application code.
Use only on an owned, logged-out test device, with voluntary test-CA trust.
Never bypass certificate pinning; never change auth/entitlement response fields.
"""
import json
from mitmproxy import ctx

class HLSFixture:
    def load(self, loader):
        loader.add_option('hls_fixture_enabled',bool,False,'Opt in to anonymous VISIONOS HLS URL substitution')
        loader.add_option('hls_fixture_url',str,'','Controlled master URL; empty string tests empty input')

    def response(self, flow):
        if not ctx.options.hls_fixture_enabled or flow.response is None:return
        if flow.request.pretty_host!='youtubei.googleapis.com':return
        if flow.request.path.split('?',1)[0]!='/youtubei/v1/player':return
        if flow.request.headers.get('Authorization') or flow.request.headers.get('Cookie'):
            ctx.log.warn('HLS fixture skipped: credential-bearing request; no values logged')
            return
        try:
            request=json.loads(flow.request.get_text())
            if request.get('context',{}).get('client',{}).get('clientName')!='VISIONOS':return
            response=json.loads(flow.response.get_text())
            if not isinstance(response.get('streamingData'),dict):return
        except (ValueError,AttributeError,TypeError):return
        response['streamingData']['hlsManifestUrl']=ctx.options.hls_fixture_url
        flow.response.set_text(json.dumps(response))
        ctx.log.info('Anonymous VISIONOS HLS fixture field substituted; no URL/header/body values logged')

addons=[HLSFixture()]
