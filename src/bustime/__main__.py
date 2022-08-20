if __name__ == "__main__":

    import os
    import yaml
    import datetime
    from models import cities_table, routes_table, points_table
    from models import Base, City, Route, TelemetryPoint
    from functions import create
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker

    with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml"), "r") as f:
        CONFIG = yaml.load(f, yaml.FullLoader)

    DATABASE = CONFIG.get("database")
    BUSTIME = CONFIG.get("bustime")

    engine = create_engine(
        "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DATABASE)
    )

    Base.metadata.create_all(engine)

    relations = [cities_table, routes_table, points_table]

    for relation in relations:
        try:
            relation.create(engine)
        except:
            pass

    Session = sessionmaker(bind=engine)
    session = Session()

    print("Fetching cities...\n")

    cities = City.fetch()

    for i, city in enumerate(cities):
        create(session, city)

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
        create(session, route)

    print("Success\n")

    routes = (
        session.query(
            Route.route_id,
            Route.name,
            Route.type,
            Route.date,
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
        for i, route in enumerate(routes):
            for point in TelemetryPoint.fetch(route, date):
                print(i, end="\r")
                create(session, point)
                points.append(route)

    print("Success\n")
