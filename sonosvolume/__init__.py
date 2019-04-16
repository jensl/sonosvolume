import argparse
import falcon
import json
import pylev
import os
import soco
import sys

CONTENT_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
}

SPEAKERS = None

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
        print("JSON:", repr(req.context['result']), file=sys.stderr)

class CORS(object):
    def process_response(self, req, resp, resource):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Headers', 'Content-Type')

class SpeakersResource(object):
    def __init__(self):
        if SPEAKERS:
            speakers = [soco.SoCo(address) for address in SPEAKERS.split(",")]
        else:
            speakers = soco.discover()
        if speakers is None:
            speakers = []
        self.speakers = {
            speaker.uid: speaker
            for speaker in speakers
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
            distance = pylev.levenshtein(name, result['name'])
            length = max(len(name), len(result['name']))
            if distance == 0:
                result['name_ratio'] = 1
            else:    
                result['name_ratio'] = (length - distance) / length
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
                'debug': SPEAKERS,
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

default_port = 8080

if "SNAP_DATA" in os.environ:
    options_dir = os.path.join(os.environ["SNAP_DATA"], "options")
    if os.path.isfile(os.path.join(options_dir, "port")):
        with open(os.path.join(options_dir, "port")) as file:
            default_port = int(file.read().strip())
    if os.path.isfile(os.path.join(options_dir, "speakers")):
        with open(os.path.join(options_dir, "speakers")) as file:
            SPEAKERS = file.read().strip()

def main():
    global SPEAKERS
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=default_port)
    arguments = parser.parse_args()
    gunicorn = os.path.join(os.path.dirname(sys.argv[0]), "gunicorn")
    os.execv(gunicorn,
             [gunicorn, "-b", ":{}".format(arguments.port), "sonosvolume:application"])
    return "failed to execute gunicorn"
