import falcon
import json
import Levenshtein
import os
import soco
import sys

CONTENT_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
}

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

    def as_json(self, speaker, name=None):
        result = {
            'uid': speaker.uid,
            'speaker_info': speaker.get_speaker_info(),
            'name': speaker.player_name,
            'volume': speaker.volume,
            'is_playing': {
                'tv': speaker.is_playing_tv,
            }
        }
        if name is not None:
            result['name_ratio'] = Levenshtein.ratio(name, result['name'])
        return result

    def on_options(self, req, resp, uid=None):
        resp.status = falcon.HTTP_204

    def on_get(self, req, resp, uid=None):
        if uid is not None:
            result = self.as_json(self.speakers[uid])
        else:
            name = req.get_param('name')
            result = {
                'speakers': [
                    self.as_json(speaker, name=name)
                    for _, speaker in sorted(self.speakers.items())
                ],
            }

        resp.status = falcon.HTTP_200
        req.context['result'] = result

    def on_post(self, req, resp, uid):
        speaker = self.speakers[uid]

        if 'volume' in req.context['input']:
            speaker.volume = req.context['input']['volume']
        if 'is_playing' in req.context['input']:
            is_playing = req.context['input']['is_playing']
            if is_playing.get('tv') and not speaker.is_playing_tv:
                speaker.switch_to_tv()

        resp.status = falcon.HTTP_200
        req.context['result'] = self.as_json(speaker)

def static_ui(req, resp):
    prefix = os.path.join(os.path.dirname(__file__), 'static-ui')
    path = os.path.normpath(os.path.join(
        prefix,
        req.path.lstrip("/") or 'index.html'))
    if not os.path.isfile(path):
        path = os.path.join(prefix, 'index.html')
    resp.status = falcon.HTTP_200
    _, ext = os.path.splitext(path)
    resp.content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')
    with open(path, 'rb') as static_file:
        resp.body = static_file.read()

application = falcon.API(middleware=[JSONTranslator(), CORS()])
application.add_route('/api/v1/speakers/{uid}', SpeakersResource())
application.add_route('/api/v1/speakers', SpeakersResource())
application.add_sink(static_ui)
