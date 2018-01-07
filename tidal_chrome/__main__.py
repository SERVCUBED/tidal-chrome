#!/usr/bin/python

# Tidal-Chrome MPRIS bridge

# Author: SERVCUBED
# License: GPL

import os
import random
import sys
import flask
import threading
from Naked.toolshed.shell import execute_js
import tidal_chrome_driver

app = flask.Flask(__name__)
d = tidal_chrome_driver.Driver()
id_last_track_title = {}
t1 = None
t2 = None


@app.route('/')
def index():
    return "Tidal Chrome web API"


@app.route('/player/canPlay')
def player_canplay():
    return str(d.CanPlay())


@app.route('/player/play')
def player_play():
    d.play()
    return ""


@app.route('/player/pause')
def player_pause():
    d.pause()
    return ""


@app.route('/player/playpause')
def player_playpause():
    if d.isPlaying():
        d.pause()
    else:
        d.play()
    return ""


@app.route('/player/next')
def player_next():
    d.next()
    return ""


@app.route('/player/previous')
def player_previous():
    d.previous()
    return ""


@app.route('/player/is/playing')
def player_is_playing():
    return str(d.isPlaying())


@app.route('/player/is/shuffle')
def player_is_shuffle():
    return str(d.isShuffle())


@app.route('/player/toggle/shuffle')
def player_toggle_shuffle():
    d.toggleShuffle()
    return ""


@app.route('/player/current/title')
def player_current_title():
    return d.currentTrackTitle()


@app.route('/player/current/artists')
def player_current_artists():
    return d.currentTrackArtists()


@app.route('/player/current/image')
def player_current_image():
    return d.currentTrackImage()


@app.route('/player/current/progress')
def player_current_progress():
    return d.currentTrackProgress()


@app.route('/player/current/duration')
def player_current_duration():
    return d.currentTrackDuration()


@app.route('/quit')
def quit():
    d.quit()
    if t1 is not None:
        t1.join()
    if t2 is not None:
        t2.join()
    sys.exit(0)


@app.route('/ping/<int:id>')
def ping(id):
    try:
        curr_title = d.currentTrackTitle()

        if id not in id_last_track_title or id_last_track_title[id] != curr_title:
            # Title has changed, return new metadata
            id_last_track_title[id] = curr_title

            # @see http://www.freedesktop.org/wiki/Specifications/mpris-spec/metadata/
            return flask.jsonify({
                'mpris:length': d.currentTrackDuration() * 1000 * 1000,  # In microseconds
                'mpris:artUrl': d.currentTrackImage(),
                'xesam:title': curr_title,
                'xesam:album': d.currentLocation(),
                'xesam:artist': d.currentTrackArtists()
            })
    except:
        e = sys.exc_info()[0]
        print("Exception in ping: " + str(e))
    return ""


@app.route('/unping/<int:id>')
def unping(id):
    # Release the client ID
    id_last_track_title.pop(id, None)
    return ""


@app.route('/ping/id')
def ping_id():
    # Get a new, unused client ID
    rid = random.randint(0, 1000)
    while rid in id_last_track_title:
        rid = random.randint(0, 1000)
    id_last_track_title[rid] = ""
    return str(rid)


def startFlask():
    print("Starting Flask app")
    app.run(host='0.0.0.0', port=1230)


def startNode():
    print("Starting node MPRIS bridge")
    execute_js(os.path.join(sys.path[0], "node-mpris", "index.js"))


if __name__ == '__main__':
    t1 = threading.Thread(target=startFlask)
    t1.start()

    t2 = threading.Thread(target=startNode)
    t2.start()
