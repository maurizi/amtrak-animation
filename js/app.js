function f() {
    var map = L.map('map').setView([41.846, -87.736], 8);
    L.tileLayer('http://a.tile.stamen.com/toner-lite/{z}/{x}/{y}.png', {
        attribution: '',
        maxZoom: 18
    }).addTo(map);

    function makeSegmentMarker(segments) {
        var segment = segments[0];
        segments.splice(0, 1);

        var ll = _.map(segment.geom, function(l) {
            return L.latLng(l[1], l[0]);
        });

        ll.reverse();
        var line = L.polyline(ll);
        var animatedMarker = L.animatedMarker(
            line.getLatLngs(),
            {
                interval: 20, // milliseconds
                onEnd: function() {
                    map.removeLayer(animatedMarker);
                    makeSegmentMarker(segments);
                }
            });

        map.addLayer(animatedMarker);
    }

    $.ajax({
        url: 'http://192.168.16.77:16000',
        success: function(data) {
            var segments = JSON.parse(data);

            _.each(segments, function(segment) {
                var ll = _.map(segment.geom, function(l) {
                    return L.latLng(l[1], l[0]);
                });
                var line = L.polyline(ll);
                map.addLayer(line);
            });

            makeSegmentMarker(segments);
        }
    });
}

$(f);
//
