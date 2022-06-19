CREATE TABLE schema.stg_cities (
    "name"      varchar(255)
  , "slug"      varchar(255)
  , "timestamp" timestamp default current_timestamp
)
PARTITION BY RANGE ("timestamp");