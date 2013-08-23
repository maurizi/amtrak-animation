import psycopg2
import json

tripid = '5437724'
conn = psycopg2.connect('dbname=amtrak user=amtrak password=amtrak host=localhost')

cur = conn.cursor()
# Get a list of all stops on the given trip

cur.execute(
    'SELECT ST_X(geom), ST_Y(geom), stops.stop_id, '
    'stop_times.arrival_time, stop_times.departure_time FROM stop_times '
    'JOIN stops ON stop_times.stop_id = stops.stop_id '
    'WHERE trip_id=%s', (tripid,))

def read_trip_stop_cache(stop1, stop2, trip):
    try:
        return json.loads(open('cache/%s_%s_%s.json' % (stop1, stop2, trip)).read())
    except:
        return None

def write_trip_stop_cache(stop1, stop2, trip, thing):
    open('cache/%s_%s_%s.json' % (stop1, stop2, trip), 'w').write(json.dumps(thing))

def touching_lines(gid_lists, target_gid):
    """
    Gids is a list of paths already looked at
    """
    new_gid_lists = []
    for gid_list in gid_lists:
        gid = gid_list[0]

        in_clause = "('%s')" % "','".join([str(s) for s in gid_list])

        cur.execute('SELECT gid FROM amtrak WHERE ST_Touches(the_geom, (SELECT the_geom FROM amtrak where gid=%s)) AND gid NOT IN ' + in_clause, (gid,))

        for (new_gid,) in cur.fetchall():
            new_gid_list = [new_gid] + gid_list
            if new_gid == target_gid:
                return new_gid_list
            else:
                new_gid_lists.append(new_gid_list)

    new_gid_lists = prune_lines(new_gid_lists)
    return touching_lines(new_gid_lists, target_gid)

def prune_lines(gid_lists):
    kept = []
    for gid_list in gid_lists:
        head = gid_list[0]

        if len([g for g in gid_lists if head in g]) == 1:
            kept.append(gid_list)

    return kept



stop_times = cur.fetchall()

stops = len(stop_times) - 1
stop = 1

data = []
for (r1, r2) in zip(stop_times, stop_times[1:]):
    print 'Working on stop %s of %s' % (stop, stops)
    stop += 1

    # Now we want to find a line segment connecting these two points:
    p1 = 'ST_Point(%s, %s)' % r1[:2]
    p2 = 'ST_Point(%s, %s)' % r2[:2]

    stop1, arr_time1, dep_time1 = [a.strip() for a in r1[2:]]
    stop2, arr_time2, dep_time2 = [a.strip() for a in r2[2:]]

    if stop1 in ['GBB', 'DEN', 'SLC', 'TRU']:
        continue

    # Find a line segment that matches this starting point
    segments = []

    nearest_pt = (
        'SELECT gid, ST_Distance(the_geom, %(p)s) d '
        'FROM amtrak ORDER BY d LIMIT 1')

    cur.execute(nearest_pt % {'p': p1})

    start_gid, _ = cur.fetchone()

    print 'Starting with %s (%s)' % (start_gid, stop1)

    cur.execute(nearest_pt % {'p': p2})

    target_gid = cur.fetchone()[0]
    print 'Going to %s (%s)' % (target_gid, stop2)

    path = read_trip_stop_cache(start_gid, target_gid, tripid)
    if path is None:
        path = touching_lines([[start_gid]], target_gid)
        write_trip_stop_cache(start_gid, target_gid, tripid, path)

    #path = path[:10]
    #path = "('%s')" % "','".join(str(s) for s in path)

    # cur.execute('SELECT ST_AsGeoJSON(ST_LineMerge(the_geom)) '
    #             'FROM amtrak WHERE gid IN %s' % path)
    jsons = []
    for gid in path:
        cur.execute('SELECT ST_AsGeoJSON(the_geom) FROM amtrak WHERE gid=%s', (gid,))
        jsonc = json.loads(cur.fetchone()[0])['coordinates']

        jsoncc = []
        for line_string in jsonc:
            jsoncc += line_string

        if len(jsons) == 0:
            jsons = jsons + jsoncc
        else:
            last_old_json = jsons[-1]

            last_new_json = jsoncc[-1]
            first_new_json = jsoncc[0]

            if last_old_json == first_new_json:
                print 'fwd'
                jsons = jsons + jsoncc
            else:
                print 'rev'
                jsons = jsons + list(reversed(jsoncc))


    data.append({
        'start': {
             'stop': stop1,
             'arrive': arr_time1,
             'depart': dep_time1},
        'end': {
            'stop': stop2,
            'arrive': arr_time2,
            'depart': dep_time2},
        'geom': jsons})


from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

from flask import Flask
app = Flask(__name__)

@app.route('/')
@crossdomain(origin='*')
def hello():
    return json.dumps(data)

app.run(port=8000, host='0.0.0.0')
