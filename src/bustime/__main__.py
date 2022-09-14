if __name__ == "__main__":

    import os
    import sys
    import yaml
    import datetime
    from functions import (
        insert_cities,
        insert_routes,
        insert_points,
    )
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.schema import CreateTable

    sys.path.append(
        os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    from database.migrations import cities_table, routes_table, points_table
    from database.functions import create_partition

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

    for relation in relations:
        try:
            relation.create(session)
        except Exception as e:  # TODO: fix
            print(e)

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

        create_partition(session, points_table.schema, points_table.name, date)

        insert_points(
            session,
            points_table.schema,
            points_table.name,
            BUSTIME.get("route").get("include"),
            date,
        )
