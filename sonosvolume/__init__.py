import falcon
import json
import soco

import sys

class JSONTranslator(object):
    def process_request(self, req, resp):
        if req.content_length in (None, 0):
            # Nothing to do.
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['input'] = json.loads(body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return
        resp.content_type = 'application/json'
        resp.body = json.dumps(req.context['result'])
        print >>sys.stderr, "JSON:", repr(req.context['result'])

class CORS(object):
    def process_response(self, req, resp, resource):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Headers', 'Content-Type')

class SpeakersResource(object):
    def __init__(self):
        self.speakers = {
            speaker.uid: speaker
            for speaker in soco.discover()
        }

    def as_json(self, speaker):
        return {
            'uid': speaker.uid,
            'name': speaker.player_name,
            'volume': speaker.volume,
        }

    def on_options(self, req, resp, uid=None):
        resp.status = falcon.HTTP_204

    def on_get(self, req, resp, uid=None):
        if uid is not None:
            result = self.as_json(self.speakers[uid])
        else:
            result = {
                'speakers': [
                    self.as_json(speaker)
                    for _, speaker in sorted(self.speakers.items())
                ],
            }

        resp.status = falcon.HTTP_200
        req.context['result'] = result

    def on_post(self, req, resp, uid):
        speaker = self.speakers[uid]

        if 'volume' in req.context['input']:
            speaker.volume = req.context['input']['volume']

        resp.status = falcon.HTTP_200
        req.context['result'] = self.as_json(speaker)

application = falcon.API(middleware=[JSONTranslator(), CORS()])
application.add_route('/api/v1/speakers/{uid}', SpeakersResource())
application.add_route('/api/v1/speakers', SpeakersResource())
