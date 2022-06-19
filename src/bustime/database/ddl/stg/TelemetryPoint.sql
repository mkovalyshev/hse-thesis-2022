CREATE TABLE {schema}.stg_telemetry_points (
    "track_id"     varchar(255)
  , "route"        json
  , "vehicle_id"   varchar(255)
  , "plate_number" varchar(255)
  , "heading"      int8
  , "direction"    int8
  , "speed"        int8
  , "mileage"      int8
  , "lon"          float
  , "lat"          float
  , "timestamp"    timestamp
)
PARTITION BY RANGE ("timestamp");