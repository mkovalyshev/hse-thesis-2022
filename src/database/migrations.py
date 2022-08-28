import datetime
from sqlalchemy.orm import registry
from sqlalchemy import (
    Table,
    Float,
    ForeignKey,
    Column,
    Integer,
    VARCHAR,
    TIMESTAMP,
    BIGINT,
)

mapper_registry = registry()

cities_table = Table(
    "cities",
    mapper_registry.metadata,
    Column("city_id", Integer, primary_key=True, nullable=False),
    Column("name", VARCHAR(255), unique=True),
    Column("slug", VARCHAR(255), unique=True),
    Column("_updated_at", TIMESTAMP, default=datetime.datetime.now().isoformat()),
)

routes_table = Table(
    "routes",
    mapper_registry.metadata,
    Column("route_id", Integer, primary_key=True, nullable=False),
    Column("name", VARCHAR(255)),
    Column("type", VARCHAR(255)),
    Column("city_id", Integer, ForeignKey("cities.city_id")),
    Column("date", TIMESTAMP),
    Column("_updated_at", TIMESTAMP, default=datetime.datetime.now().isoformat()),
)

points_table = Table(
    "points",
    mapper_registry.metadata,
    Column("track_id", VARCHAR(255), primary_key=True, nullable=False),
    Column(
        "route_id",
        Integer,
        ForeignKey("routes.route_id"),
        primary_key=True,
        nullable=False,
    ),
    Column("vehicle_id", VARCHAR(255)),
    Column("speed", Integer),
    Column("lon", Float),
    Column("lat", Float),
    Column("timestamp", TIMESTAMP, primary_key=True, nullable=False),
)

parking_categories_table = Table(
    "parking_categories",
    mapper_registry.metadata,
    Column("category_id", Integer, primary_key=True, nullable=False),
    Column("name", VARCHAR(255), unique=False),
    Column("type", VARCHAR(255), unique=False),
    Column("parent_id", Integer, unique=False),
    Column("city_id", Integer, ForeignKey("cities.city_id")),
    Column("_updated_at", TIMESTAMP, default=datetime.datetime.now().isoformat()),
)

parking_congestions_table = Table(
    "parking_congestions",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("parking_id", Integer, ForeignKey("parkings.parking_id"), nullable=False),
    Column("total", Integer),
    Column("free", Integer),
    Column("updated_at", BIGINT),
    Column(
        "city_id", Integer, ForeignKey("cities.city_id"), primary_key=True, unique=False
    ),
    Column("_updated_at", TIMESTAMP, default=datetime.datetime.now().isoformat()),
)


parking_prices_table = Table(
    "parking_prices",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("parking_id", Integer, ForeignKey("parkings.parking_id"), nullable=False),
    Column("vehicle_type", VARCHAR(255)),
    Column("min", Integer),
    Column("max", Integer),
    Column(
        "city_id", Integer, ForeignKey("cities.city_id"), primary_key=True, unique=False
    ),
    Column("_updated_at", TIMESTAMP, default=datetime.datetime.now().isoformat()),
)

parkings_table = Table(
    "parkings",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("parking_id", Integer, unique=False),
    Column("location", VARCHAR(255)),
    Column("spaces_total", Integer),
    Column("spaces_handicapped", Integer),
    Column("category_id", Integer, ForeignKey("parking_categories.category_id")),
    Column("city_id", Integer, ForeignKey("cities.city_id"), unique=False),
    Column("_updated_at", TIMESTAMP, default=datetime.datetime.now().isoformat()),
)
