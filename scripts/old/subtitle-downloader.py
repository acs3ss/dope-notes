#!/usr/bin/python3

# input a url
import argparse
import json
import re
import urllib.parse, urllib.request

def download_subtitles(video):
    id = retrieve_id(video)

    # Lots of the following taken from you-get
    req = urllib.request.Request(video)

    response = urllib.request.urlopen(req)
    data = response.read()

    # Handle HTTP compression for gzip and deflate (zlib)
    content_encoding = response.getheader('Content-Encoding')
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

    # Decode the response body
    match = re.search(r'charset=([\w-]+)', response.getheader('Content-Type'))
    if match:
        data = data.decode(match.group(1))
    else:
        data = data.decode('utf-8', 'ignore')

    video_page = data
    ytplayer_config = json.loads(re.search('ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))
    try:
        caption_tracks = json.loads(ytplayer_config['args']['player_response'])['captions']['playerCaptionsTracklistRenderer']['captionTracks']
        filename = False
        for ct in caption_tracks:
            if ct['languageCode'] == 'en':
                filename = id + '_' + ct['languageCode']
                urllib.request.urlretrieve(ct['baseUrl'], filename)
                break
        if not filename:
            filename = id + '_' + caption_tracks[0]['languageCode']
            urllib.request.urlretrieve(caption_tracks[0]['baseUrl'], filename)
    except:
        return None

    return filename


def retrieve_id(url):
    # Adopted from you-get
    match = re.search(r'(?:youtube\.com/(?:embed|v|watch)|youtu\.be)/([^/?]+)', url)
    if match:
        return match.group(1)
    else:
        try:
            return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)['v'][0]
        except:
            return None

parser = argparse.ArgumentParser()
parser.add_argument(dest='url', help='YouTube url to extract subtitles from')
args = parser.parse_args()

print(download_subtitles(args.url))
