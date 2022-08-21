import datetime
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import declarative_base, registry
from sqlalchemy import (
    Table,
    Float,
    ForeignKey,
    Column,
    Integer,
    VARCHAR,
    TIMESTAMP,
)

Base = declarative_base()

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
    Column("plate_number", VARCHAR(255)),
    Column("heading", Integer),
    Column("direction", Integer),
    Column("speed", Integer),
    Column("mileage", Integer),
    Column("lon", Float),
    Column("lat", Float),
    Column("timestamp", TIMESTAMP, primary_key=True, nullable=False),
)


class City(Base):

    __table__ = cities_table

    def __init__(self, name: str, slug: str, city_id: int = None) -> None:

        self.name = name.strip()
        self.slug = slug.strip()
        self.city_id = city_id

    def serialize(self) -> dict:
        """
        returns a serialized object
        """

        return {"name": self.name, "slug": self.slug}

    @staticmethod
    def fetch(schema: str = "https", host: str = "busti.me") -> tuple[object]:
        """
        returns tuple of City objects
        """

        html = requests.get(f"{schema}://{host}/").text
        soup = BeautifulSoup(html, features="html.parser")

        items = soup.findAll("div", {"class": "menu"})[1].findAll(
            "a", {"class": "item"}
        )

        cities = [City(item.text, item.get("href").strip("/")) for item in items]

        return tuple(cities)


class Route(Base):

    __table__ = routes_table
    __mapper_args__ = {"exclude_properties": ["city_name", "city_slug", "city"]}

    def __init__(
        self,
        route_id: int,
        name: str,
        type: str,
        city_id: int,
        city_name: str,
        city_slug: str,
        date: datetime.date,
    ) -> None:

        self.route_id = route_id
        self.name = name
        self.type = type
        self.city_id = city_id
        self.city_name = city_name
        self.city_slug = city_slug
        self.date = date

    @property
    def city(self) -> City:
        return City(name=self.city_name, slug=self.city_slug)

    def serialize(self) -> dict:
        """
        returns a serialized object
        """

        return {
            "route_id": self.route_id,
            "name": self.name,
            "type": self.type,
            "city": self.city.serialize(),
            "date": self.date.strftime("%Y-%m-%d"),
        }

    @staticmethod
    def fetch(
        city: City,
        schema: str = "https",
        host: str = "busti.me",
        date: datetime.date = datetime.datetime.today(),
    ) -> tuple[object]:
        """
        returns tuple of Route objects
        """

        html = requests.get(
            f"{schema}://{host}/{city.slug}/transport/{date.strftime('%Y-%m-%d')}/"
        ).text

        soup = BeautifulSoup(html, features="html.parser")

        items = soup.find("select", {"name": "bus_id"})

        if items is None:
            return []

        items = items.find_all("option")

        objects = []

        for item in items:
            if item.get("value") == "0":
                continue

            id_ = int(item.get("value"))
            name = item.text.split(" ")[-1]
            type = " ".join(item.text.split(" ")[:-1]).lower()

            objects.append(
                Route(
                    route_id=id_,
                    name=name,
                    type=type,
                    city_id=city.city_id,
                    city_name=city.name,
                    city_slug=city.slug,
                    date=date,
                )
            )

        return tuple(objects)


class TelemetryPoint(Base):

    __table__ = points_table
    __mapper_args__ = {
        "exclude_properties": ["route"],
    }

    def __init__(
        self,
        track_id: str,
        route: Route,
        vehicle_id: str,
        plate_number: str,
        heading: int,
        direction: int,
        speed: int,
        mileage: int,
        lon: float,
        lat: float,
        timestamp: datetime.datetime,
    ) -> None:

        self.track_id = track_id
        self.route_id = route.route_id
        self.vehicle_id = vehicle_id
        self.plate_number = plate_number
        self.heading = heading
        self.direction = direction
        self.speed = speed
        self.mileage = mileage
        self.lon = lon
        self.lat = lat
        self.timestamp = timestamp

        self._route = route

    @staticmethod
    def fetch(
        route: Route,
        date: datetime.date,
        schema: str = "https",
        host: str = "busti.me",
    ) -> tuple[object]:
        """
        returns tuple of Point objects
        """

        data = {
            "city_slug": route.city_slug,
            "bus_id": route.route_id,
            "day": date.strftime("%Y-%m-%d"),
        }

        items = requests.post(f"{schema}://{host}/ajax/transport/", data=data).json()

        objects = []

        for item in items:
            objects.append(
                TelemetryPoint(
                    track_id=item["uniqueid"],
                    route=route,
                    vehicle_id=item["bortnum"],
                    plate_number=item["gosnum"],
                    heading=item["heading"],
                    direction=item["direction"],
                    speed=item["speed"],
                    mileage=item["probeg"],
                    lon=item["lon"],
                    lat=item["lat"],
                    timestamp=datetime.datetime.strptime(
                        date.strftime("%Y-%m-%d") + " " + item["timestamp"],
                        "%Y-%m-%d %H:%M:%S",
                    ),
                )
            )

        return tuple(objects)

