import datetime
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import declarative_base
import sys
import os

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from database.migrations import cities_table, routes_table, points_table


Base = declarative_base()

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
        speed: int,
        lon: float,
        lat: float,
        timestamp: datetime.datetime,
    ) -> None:

        self.track_id = track_id
        self.route_id = route.route_id
        self.vehicle_id = vehicle_id
        self.speed = speed
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
                    speed=item["speed"],
                    lon=item["lon"],
                    lat=item["lat"],
                    timestamp=datetime.datetime.strptime(
                        date.strftime("%Y-%m-%d") + " " + item["timestamp"],
                        "%Y-%m-%d %H:%M:%S",
                    ),
                )
            )

        return tuple(objects)

