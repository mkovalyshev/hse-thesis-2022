import requests
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
    def get_cities(schema: str = "https", host: str = "busti.me") -> tuple[object]:
        """
        returns tuple of City objects
        """

        html = requests.get(f"{schema}://{host}/").text
        soup = BeautifulSoup(html, features="html.parser")

        items = soup.findAll("div", {"class": "menu"})[1].findAll(
            "a", {"class": "item"}
        )

        cities = []

        for item in items:
            cities.append(City(item.text, item.get("href").strip("/")))

        return cities


class Point:
    pass


class Route:
    pass
