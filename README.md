Animating Amtrak
================

Bootstrap your Database
----------

You need to have a spatial database available. First install the
geometry:

```
gunzip data/amtrak.sql.gz
psql -h $HOST $DB $USER -f data/amtrak.sql
```

Now load up the relevant GTFS tables:

```
gunzip data/stops.gz
gunzip data/stop_times.gz

# Fix absolute paths
$EDITOR data/load_stops.sql
psql -h $HOST $DB $USER -f data/load_stops.sql
```

Server
----------

Amtrak paths are generated and then cached. To get a server going:

```
virtualenv env
source env/bin/activate

pip install -r requirements.txt

python server.py
```

Static Files
---------

The server doesn't yet server static fields (*doh*) so you may want to
do that yourself:

```
python -mSimpleHTTPServer 4000
```
