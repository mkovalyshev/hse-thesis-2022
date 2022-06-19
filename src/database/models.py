import yaml
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

with open("config.yaml") as file:
    CONFIG = yaml.load(file, Loader=yaml.SafeLoader)

with open("sql/create.sql", "r") as file:
    CREATE_STATEMENT = file.read()

with open("sql/grant_privileges.sql", "r") as file:
    GRANT_PRIVILEGES_STATEMENT = file.read()


class Database:
    def __init__(
        self,
        provider: str,
        host: str,
        username: str,
        password: str,
        database: str,
        *args,
        **kwargs
    ) -> None:
        self.__provider = provider
        self.__host = host
        self.__username = username
        self.__password = password
        self.__database = database

    def __get_credentials(self) -> dict:
        """
        returns psycopg2 compliant credentials for kwargs unpacking
        """

        return {
            "dbname": self.__provider,
            "user": self.__username,
            "host": self.__host,
            "password": self.__password,
        }

    def create_database(
        self, database: str = CONFIG["database"], owner: str = CONFIG["username"]
    ) -> None:
        """
        created database with owner
        """

        with psycopg2.connect(**self.__get_credentials()) as connection:
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            cursor.execute(CREATE_STATEMENT.format(owner=owner, database=database))
            connection.commit()
            cursor.execute(
                GRANT_PRIVILEGES_STATEMENT.format(owner=owner, database=database)
            )
            connection.commit()

