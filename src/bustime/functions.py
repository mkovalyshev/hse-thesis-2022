import datetime
from sqlalchemy import Table
from sqlalchemy.schema import CreateTable
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


def create_partitioned_table(session: object, table: Table, key: str) -> None:
    """
    creates table partitioned by range(key)
    """

    if table.exists(session):
        table.drop(session)

    DDL = CreateTable(table).__str__() + f"PARTITION BY RANGE({key})\n;"

    session.execute(DDL)
    session.commit()


def create_partition(
    session: object, table_schema: str, table_name: str, date: datetime.date
) -> None:
    """
    creates partition of date partitioned table
    """

    partition_start = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    partition_end = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)

    relation = ".".join(
        list(filter(lambda x: x is not None, [table_schema, table_name]))
    )

    session.execute(
        f"""
    CREATE TABLE IF NOT EXISTS {relation}_{date.strftime("%Y_%m_%d")}
    PARTITION OF points
    FOR VALUES FROM ('{partition_start.isoformat()}') TO ('{partition_end.isoformat()}');
    """
    )

    session.commit()


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

    create_partition(session, table_schema, table_name, date)

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

