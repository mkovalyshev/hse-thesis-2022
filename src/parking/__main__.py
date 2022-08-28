if __name__ == "__main__":

    import sys
    import os

    sys.path.append(
        os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    import os
    import yaml
    from models import Client, ParkingCategory, Parking
    from functions import create

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker

    with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml"), "r") as f:
        CONFIG = yaml.load(f, yaml.FullLoader)

    DATABASE = CONFIG.get("database")
    PARKING = CONFIG.get("parking")

    engine = create_engine(
        "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DATABASE)
    )

    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as con:
        cities = con.execute(
            """
        select distinct city_id, slug
        from cities
        """
        ).fetchall()

        cities = list(filter(lambda x: x[1] in PARKING.get("api").keys(), cities))

    for city in cities:

        client = Client(
            city[0],
            PARKING.get("api", {}).get(city[1], {}).get("host"),
            PARKING.get("api", {}).get(city[1], {}).get("ver"),
        )

        for category in ParkingCategory.fetchall(client):
            create(session, category, autocommit=True)

        parkings = Parking.fetch(client)

        for parking in parkings:
            create(session, parking, autocommit=True)
            price = parking.price
            congestion = parking.congestion
            create(session, price, autocommit=True)
            create(session, congestion, autocommit=True)

