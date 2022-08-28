import sys
import os
from wsgiref.headers import Headers

sys.path.append(
    os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from database.migrations import (
    parking_categories_table,
    parking_congestions_table,
    parking_prices_table,
    parkings_table,
)

from functions import wkt_from_tuple
import requests
from sqlalchemy.orm import declarative_base

Base = declarative_base()


HEADERS = {
    "Accept": "application/json",
    "Referer": "https://parkingkzn.ru/ru/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/104.0.0.0 Safari/537.36",
}


class Client:
    def __init__(self, city_id: int, host: str, version: str):
        self.city_id = city_id
        self.host = host
        self.version = version

    def get_categories(self) -> dict:
        response = requests.get(
            f"https://{self.host}.ru/api/{self.version}/categories", headers=HEADERS
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def get_parkings(self) -> dict:

        params = {
            # "fields": "_id,center,category,zone,congestion,spaces,blocked,parentId",
        }

        response = requests.get(
            f"https://{self.host}.ru/api/{self.version}/parkings",
            params=params,
            headers=HEADERS,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {}


class ParkingCategory(Base):

    __table__ = parking_categories_table

    def __init__(
        self, category_id: int, name: str, type: str, parent_id: int, city_id: int
    ):
        self.category_id = category_id
        self.name = name
        self.type = type
        self.parent_id = parent_id
        self.city_id = city_id

    @staticmethod
    def fetchall(client: object) -> tuple[object]:  # TODO: client is WIP
        records = client.get_categories().get("categories", [])
        city_id = client.city_id

        objects = []

        parent_map = {}

        for record in records:
            if len(record.get("children", [])) > 0:
                for child in record.get("children"):
                    parent_map[child] = record.get("_id")

        for record in records:
            objects.append(
                ParkingCategory(
                    category_id=record.get("_id"),
                    name=record.get("name").get("ru"),
                    type=record.get("type"),
                    parent_id=parent_map.get(record.get("_id")),
                    city_id=city_id,
                )
            )

        return objects

    def serialize(self) -> dict:
        return self.__dict__


class ParkingCongestion(Base):

    __table__ = parking_congestions_table

    def __init__(self, parking_id: int, total: int, free: int, updated_at: int):
        self.parking_id = parking_id
        self.total = total
        self.free = free
        self.updated_at = updated_at

    def serialize(self) -> dict:
        return self.__dict__


class ParkingPrice(Base):

    __table__ = parking_prices_table

    def __init__(self, parking_id: int, vehicle_type: str, min: int, max: int):
        self.parking_id = parking_id
        self.vehicle_type = vehicle_type
        self.min = min
        self.max = max

    def serialize(self) -> dict:
        return self.__dict__


class Parking(Base):

    __table__ = parkings_table
    __mapper_args__ = {
        "exclude_properties": [
            "congestion_total",
            "congestion_free",
            "congestion_updated_at",
            "price_vehicle_type",
            "price_min",
            "price_max",
        ],
    }

    def __init__(
        self,
        parking_id: int,
        location: str,
        spaces_total: int,
        spaces_handicapped: int,
        congestion_total: int,
        congestion_free: int,
        congestion_updated_at: int,
        price_vehicle_type: str,
        price_min: int,
        price_max: int,
        category_id: int,
        city_id: int,
    ):
        self.parking_id = parking_id
        self.location = location
        self.spaces_total = spaces_total
        self.spaces_handicapped = spaces_handicapped
        self.congestion_total = congestion_total
        self.congestion_free = congestion_free
        self.congestion_updated_at = congestion_updated_at
        self.price_vehicle_type = price_vehicle_type
        self.price_min = price_min
        self.price_max = price_max
        self.category_id = category_id
        self.city_id = city_id

    @property
    def congestion(self) -> ParkingCongestion:
        return ParkingCongestion(
            self.parking_id,
            self.congestion_total,
            self.congestion_free,
            self.congestion_updated_at,
        )

    @property
    def price(self) -> ParkingPrice:
        return ParkingPrice(
            self.parking_id, self.price_vehicle_type, self.price_min, self.price_max
        )

    @staticmethod
    def fetch(client: Client) -> tuple[object]:

        records = client.get_parkings().get("parkings", [])
        city_id = client.city_id

        objects = []

        for record in records:
            obj = Parking(
                record.get("_id"),
                wkt_from_tuple(
                    record.get("center", {"coordinates": [0, 0]}).get(
                        "coordinates", [0, 0]
                    )
                ),
                record.get("spaces", {"total": 0}).get("total"),
                record.get("spaces", {"handicapped": 0}).get("handicapped"),
                record.get("congestion", {})
                .get("spaces", {})
                .get("overall", {})
                .get("total"),
                record.get("congestion", {})
                .get("spaces", {})
                .get("overall", {})
                .get("free"),
                record.get("congestion", {}).get("updateDate"),
                record.get("zone", {"prices": [{}]})
                .get("prices", [{}])[0]
                .get("vehicleType"),
                record.get("zone", {"prices": [{}]})
                .get("prices", [{}])[0]
                .get("price", {})
                .get("min"),
                record.get("zone", {"prices": [{}]})
                .get("prices", [{}])[0]
                .get("price", {})
                .get("max"),
                record.get("category", {}).get("_id"),
                city_id,
            )

            objects.append(obj)

        return objects

    def serialize(self) -> dict:
        return {
            "parking_id": self.parking_id,
            "location": self.location,
            "spaces_total": self.spaces_total,
            "spaces_handicapped": self.spaces_handicapped,
            "congestion": self.congestion,
            "price": self.price,
            "category_id": self.category_id,
            "city_id": self.city_id,
        }
