import datetime


def log(func):
    def wrapper(*args, **kwargs):
        print(datetime.datetime.now().isoformat(), func.__name__, args, kwargs)
        result = func(*args, **kwargs)
        return result

    return wrapper


@log
def create(session: object, record: object) -> bool:
    """
    creates object at database
    """

    try:
        session.add(record)
        session.commit()

        return True

    except BaseException as e:
        print(e)
        session.rollback()

        return False
