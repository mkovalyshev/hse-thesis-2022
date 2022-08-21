if __name__ == "__main__":

    import os
    import yaml
    import datetime
    from models import cities_table, routes_table, points_table
    from models import Base, City, Route, TelemetryPoint
    from functions import (
        create,
        create_partitioned_table,
        insert_cities,
        insert_routes,
        insert_points,
    )
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

    Session = sessionmaker(bind=engine)
    session = Session()

    cities_table.create(engine)
    routes_table.create(engine)

    create_partitioned_table(session, points_table, "timestamp")

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

    insert_cities(session)

    insert_routes(session, BUSTIME.get("route").get("include"))

    dates = [
        datetime.date.today() - datetime.timedelta(days=i + 1)
        for i in range(BUSTIME.get("depth"))
    ]

    for date in dates:
        insert_points(
            session,
            points_table.schema,
            points_table.name,
            BUSTIME.get("route").get("include"),
            date,
        )

