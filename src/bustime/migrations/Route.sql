create table if not exists {{ schema }}.stg_routes (
    "route_id"    int8
  , "name"        varchar(64)
  , "type"        varchar(255)
  , "city"        json
  , "_updated_at" timestamp default current_timestamp not null
  
)
partition by range ("timestamp");