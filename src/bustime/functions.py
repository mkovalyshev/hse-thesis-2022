import datetime


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


def partition_table(session: object, schema: str, name: str, key: str) -> None:
    """
    partitions table by range(key)
    """

