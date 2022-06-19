CREATE TABLE schema.stg_routes (
    "route_id"  int8
  , "name"      varchar(64)
  , "type"      varchar(255)
  , "city"      json
  , "timestamp" timestamp default current_timestamp
)
PARTITION BY RANGE ("timestamp");