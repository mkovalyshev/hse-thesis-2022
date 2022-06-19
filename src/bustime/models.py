from sqlite3 import Date
import requests
import datetime
from bs4 import BeautifulSoup


class City:
    def __init__(self, name: str, slug: str) -> None:
        self.name = name
        self.slug = slug

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


class Route:
    def __init__(
        self, route_id: int, name: str, type: str, city: City, date: datetime.date
    ) -> None:
        self.route_id = route_id
        self.name = name
        self.type = type
        self.city = city
        self.date = date

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
        date: datetime.date = datetime.date.today(),
    ) -> tuple[object]:
        """
        returns tuple of Route objects
        """

        html = requests.get(
            f"{schema}://{host}/{city.slug}/transport/{date.strftime('%Y-%m-%d')}/"
        ).text

        soup = BeautifulSoup(html, features="html.parser")

        items = soup.find("select", {"name": "bus_id"}).find_all("option")

        objects = []

        for item in items:
            if item.get("value") == "0":
                continue

            id_ = int(item.get("value"))
            name = item.text.split(" ")[-1]
            type = " ".join(item.text.split(" ")[:-1]).lower()

            objects.append(
                Route(route_id=id_, name=name, type=type, city=city, date=date)
            )

        return tuple(objects)


class TelemetryPoint:
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
        self.route = route
        self.vehicle_id = vehicle_id
        self.plate_number = plate_number
        self.heading = heading
        self.direction = direction
        self.speed = speed
        self.mileage = mileage
        self.lon = lon
        self.lat = lat
        self.timestamp = timestamp

    def serialize(self) -> dict:
        """
        returns a serialized object
        """

        return {
            "track_id": self.track_id,
            "route": self.route.serialize(),
            "vehicle_id": self.vehicle_id,
            "plate_number": self.plate_number,
            "heading": self.heading,
            "direction": self.direction,
            "speed": self.speed,
            "mileage": self.mileage,
            "lon": self.lon,
            "lat": self.lat,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

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
            "city_slug": route.city.slug,
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
