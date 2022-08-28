import datetime
from models import City, Route, TelemetryPoint


def create_log(func):
    def wrapper(*args, **kwargs):
        print(datetime.datetime.now().isoformat(), "Create", args[1])
        result = func(*args, **kwargs)
        return result

    return wrapper


@create_log
def create(session: object, record: object, autocommit: bool = False) -> bool:
    """
    creates object at database
    """

    try:
        session.add(record)

        if autocommit:
            session.commit()

        return True

    except BaseException as e:
        print("Failed:", e.orig)
        session.rollback()

        return False


def bulk_create() -> None:
    pass


def insert_cities(session: object) -> None:
    """
    loads cities into database
    """

    cities = City.fetch()

    for city in cities:
        create(session, city, autocommit=True)


def insert_routes(session: object, cities_include: list) -> None:
    """
    loads routes into database
    """

    cities = session.query(City).filter(City.slug.in_(cities_include)).all()

    for city in cities:
        for route in Route.fetch(city):
            create(session, route)  # TODO: change to bulk_create

        try:
            session.commit()
        except BaseException as e:
            print("Failed:", e.orig)
            session.rollback()


def insert_points(
    session: object,
    table_schema: str,
    table_name: str,
    cities_include: list,
    date: datetime.date,
) -> None:

    routes = (
        session.query(
            Route.route_id,
            Route.name,
            Route.type,
            Route.date,
            City.city_id.label("city_id"),
            City.name.label("city_name"),
            City.slug.label("city_slug"),
        )
        .join(City)
        .filter(City.slug.in_(cities_include))
        .all()
    )

    for route in routes:
        for point in TelemetryPoint.fetch(route, date):
            create(session, point)

        try:
            session.commit()
        except BaseException as e:
            print("Failed:", e.orig)
            session.rollback()

