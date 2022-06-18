import requests
import datetime
from bs4 import BeautifulSoup


class City:
    def __init__(self, name: str, slug: str) -> None:
        self.name = name
        self.slug = slug

    def serialize(self) -> tuple:
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

        return cities


class Point:
    def __init__(
        self,
        track_id: str,
        route_id: int,
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
        self.route_id = route_id
        self.vehicle_id = vehicle_id
        self.plate_number = plate_number
        self.heading = heading
        self.direction = direction
        self.speed = speed
        self.mileage = mileage
        self.lon = lon
        self.lat = lat
        self.timestamp = timestamp

    def serialize(self) -> tuple:
        """
        returns a serialized object
        """

        return {
            "track_id": self.track_id,
            "route_id": self.route_id,
            "vehicle_id": self.vehicle_id,
            "plate_number": self.plate_number,
            "heading": self.heading,
            "direction": self.direction,
            "speed": self.speed,
            "mileage": self.mileage,
            "lon": self.lon,
            "lat": self.lat,
            "timestamp": self.timestamp,
        }


class Route:
    def __init__(self) -> None:
        pass
