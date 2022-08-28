if __name__ == "__main__":

    import os
    import yaml
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.schema import CreateTable
    from migrations import (
        parking_categories_table,
        parking_congestions_table,
        parking_prices_table,
        parkings_table,
        cities_table,
        routes_table,
        points_table,
    )
    from functions import create_partitioned_table

    with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml"), "r") as f:
        CONFIG = yaml.load(f, yaml.FullLoader)

    DATABASE = CONFIG.get("database")

    engine = create_engine(
        "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DATABASE)
    )

    Session = sessionmaker(bind=engine)
    session = Session()

    if not cities_table.exists(engine):  # TODO: remove, deprecated
        cities_table.create(engine)

    if not routes_table.exists(engine):  # TODO: remove, deprecated
        routes_table.create(engine)

    if not parking_categories_table.exists(engine):  # TODO: remove, deprecated
        parking_categories_table.create(engine)

    if not parkings_table.exists(engine):  # TODO: remove, deprecated
        parkings_table.create(engine)

    if not parking_congestions_table.exists(engine):  # TODO: remove, deprecated
        parking_congestions_table.create(engine)

    if not parking_prices_table.exists(engine):  # TODO: remove, deprecated
        parking_prices_table.create(engine)

    if not points_table.exists(engine):  # TODO: remove, deprecated
        create_partitioned_table(session, points_table, "timestamp")
