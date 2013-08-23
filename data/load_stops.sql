DROP TABLE IF EXISTS stops;
DROP TABLE IF EXISTS stop_times;

CREATE TABLE stops
       (stop_id char(100), stop_name char(100), stop_lat double precision,
        stop_lon double precision, stop_url char(255), stop_timezone char(255));

COPY stops FROM '/usr/local/amtrak/stops.txt' DELIMITER ',' CSV HEADER;

SELECT AddGeometryColumn('stops', 'geom', 4326, 'POINT', 2);

UPDATE stops SET geom=ST_SetSRID(ST_Point(stop_lon, stop_lat), 4326);

ALTER TABLE stops DROP COLUMN stop_lat;
ALTER TABLE stops DROP COLUMN stop_lon;

CREATE TABLE stop_times
       (trip_id char(100), arrival_time char(100), departure_time char(100),
       stop_id char(100), stop_sequence integer, pickup_type char(100),
       drop_off_type char(100));

COPY stop_times FROM '/usr/local/amtrak/stop_times.txt' DELIMITER ',' CSV HEADER;
