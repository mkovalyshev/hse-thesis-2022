from typing import Iterable
import datetime


def wkt_from_tuple(coordinates: Iterable) -> str:
    coordinates_str = list(map(str, coordinates))

    return f'POINT({" ".join(coordinates_str)})'


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
        print("Failed:", e)
        session.rollback()

        return False
