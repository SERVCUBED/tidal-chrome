// Tidal-MPRIS
// Bridge for tidal-chrome web API and MPRIS
// Author: SERVCUBED
// License: GPL

var Player = require('mpris-service');
var request = require("request");

var host = "http://127.0.0.1:1230/";

var clientid = undefined;

var player = Player({
    name: 'tidal-chrome',
    identity: 'Tidal-Chrome API bridge',
    supportedUriSchemes: [],
    supportedMimeTypes: [],
    supportedInterfaces: ['player']
});

player.on('quit', function () {
    request(host + "quit");
    process.exit();
});

player.on('play', function () {
    request(host + "player/play");
});

player.on('pause', function () {
    request(host + "player/pause");
});

player.on('playpause', function () {
    request(host + "player/playpause");
});

player.on('next', function () {
    request(host + "player/next");
});

player.on('previous', function () {
    request(host + "player/previous");
});

setInterval(function () {
    if (clientid === undefined)
    {
        request(host + "ping/id", function(error, response, body) {
            clientid = parseInt(body)
        });
        // Try again next time
        return;
    }

    request(host + "ping/" + clientid, function(error, response, body) {
        if (body === undefined || body.length === 0)
            return;

        player.metadata = JSON.parse(body);
    });

    request(host + "player/is/playing", function(error, response, body) {
        newstate = body === "True"? "Playing" : "Paused";

        if (player.playbackStatus !== newstate)
            player.playbackStatus = newstate;
    });
}, 7000);