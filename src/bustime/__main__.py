if __name__ == "__main__":

    import os
    import yaml
    import datetime
    from models import cities_table, routes_table, points_table  # TODO: move to migrations
    from functions import (
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

    POINTS_THRESHOLD = 1_000_000

    engine = create_engine(
        "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DATABASE)
    )

    relations = [cities_table, routes_table]

    Session = sessionmaker(bind=engine)
    session = Session()

    if not cities_table.exists(engine):  # TODO: remove, deprecated
        cities_table.create(engine)

    if not routes_table.exists(engine):  # TODO: remove, deprecated
        routes_table.create(engine)

    if not points_table.exists(engine):  # TODO: remove, deprecated
        create_partitioned_table(session, points_table, "timestamp")

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
        print("Column exists already, passing...")

    insert_cities(session)

    insert_routes(session, BUSTIME.get("route").get("include"))

    dates = [
        datetime.date.today() - datetime.timedelta(days=i + 1)
        for i in range(BUSTIME.get("depth"))
    ]

    for date in dates:

        points_count = session.execute(
            f"""
        select count(*)
        from points
        where True
            and date("timestamp") = date('{date}')
        """
        ).fetchone()[0]

        if points_count >= POINTS_THRESHOLD:
            print("{date} already parsed, skipping...")
            continue

        insert_points(
            session,
            points_table.schema,
            points_table.name,
            BUSTIME.get("route").get("include"),
            date,
        )

