from requests import session


if __name__ == "__main__":

    import os
    import yaml
    import datetime
    from models import cities_table, routes_table, points_table
    from models import Base, City, Route, TelemetryPoint
    from functions import create
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker

    from sqlalchemy.schema import CreateTable

    with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml"), "r") as f:
        CONFIG = yaml.load(f, yaml.FullLoader)

    DATABASE = CONFIG.get("database")
    BUSTIME = CONFIG.get("bustime")

    engine = create_engine(
        "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DATABASE)
    )

    relations = [cities_table, routes_table]

    for relation in relations:
        try:
            relation.create(engine)
        except:
            pass

    points_DDL = (
        CreateTable(points_table).__str__() + "PARTITION BY RANGE(timestamp)\n;"
    )

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        session.execute(points_DDL)
        session.commit()
    except:
        pass

    try:
        session.execute(
            """
        ALTER TABLE points
        ADD COLUMN "_updated_at"
        TIMESTAMPTZ;
        
        ALTER TABLE points 
        ALTER COLUMN "_updated_at" 
        SET DEFAULT now();
        """
        )
        session.commit()
    except:
        pass

    print("Fetching cities...\n")

    cities = City.fetch()

    for i, city in enumerate(cities):
        create(session, city, autocommit=True)

    print("Success\n")

    cities = (
        session.query(City)
        .filter(City.slug.in_(BUSTIME.get("route").get("include")))
        .all()
    )

    routes = []

    print("Fetching routes...\n")

    for i, city in enumerate(cities):
        for route in Route.fetch(city):
            routes.append(route)

    print("Success\n")

    print("Loading routes...\n")

    for i, route in enumerate(routes):
        print(i, end="\r")
        create(session, route, autocommit=True)

    print("Success\n")

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
        .filter(City.slug.in_(BUSTIME.get("route").get("include")))
        .all()
    )

    dates = [
        datetime.date.today() - datetime.timedelta(days=i + 1)
        for i in range(BUSTIME.get("depth"))
    ]

    print("Fetching points...\n")

    points = []

    for date in dates:

        partition_start = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
        partition_end = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)

        session.execute(
            f"""
        CREATE TABLE IF NOT EXISTS points_{date.strftime("%Y_%m_%d")}
        PARTITION OF points
        FOR VALUES FROM ('{partition_start.isoformat()}') TO ('{partition_end.isoformat()}');
        """
        )

        session.commit()

        for i, route in enumerate(routes):
            for point in TelemetryPoint.fetch(route, date):
                print(i, end="\r")
                create(session, point)
                points.append(route)

            try:
                session.commit()
            except BaseException as e:
                print("Failed:", e.orig)
                session.rollback()

    print("Success\n")
