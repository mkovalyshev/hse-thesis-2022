create table if not exists {{ schema }}.stg_cities (
    "name"        varchar(255)
  , "slug"        varchar(255)
  , "_updated_at" timestamp default current_timestamp
)
partition by range ("timestamp");