import psycopg2
from typing import Iterable
from jinja2 import Template


def get_template(path: str) -> Template:
    pass


class Column:
    """
    class for PostgreSQL column
    """

    def __init__(
        self, name: str, type: str,
    ):
        self.name = name
        self.type = type

    def __repr__(self) -> str:
        return "Column {name}({type})".format(name=self.name, type=self.type)


class Table:
    """
    class for PostgreSQL table
    """

    def __init__(
        self,
        schema: str,
        name: str,
        columns: Iterable[Column],
        partition_by: Iterable[Column],
    ):
        self.schema = schema
        self.name = name
        self.columns = columns
        self.partition_by = partition_by

    def __repr__(self) -> str:
        return "Table {schema}.{name}".format(schema=self.schema, name=self.name)


class PostgreSQL:
    """
    class for handling PostgreSQL operations
    """

    def __init__(
        self, host: str, port: int, user: str, password: str, database: str = None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def __repr__(self):
        return "PostgreSQL({host}:{port}/{database}); user={user}; password=***".format(
            host=self.host, port=self.port, database=self.database, user=self.user
        )

    def _connect(self) -> object:
        """
        returns psycopg2 connection
        """

        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )

        return connection

    def execute(self, query: str, commit: bool = False) -> None:
        """
        executes query
        """

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query)

            if commit:
                connection.commit()

    def create_database(self, database: str, owner: str) -> None:
        """
        creates database with owner
        """

        template = get_template("templates/create_database.sql")
        self.execute(template.render(database=database, owner=owner), commit=True)

    def grant_privileges(self, database: str, owner: str) -> None:
        """
        grants all privileges on database to owner
        """

        template = get_template("templates/grant_privileges.sql")
        self.execute(template.render(database=database, owner=owner), commit=True)

    def create_table(self, table: Table) -> None:
        """
        creates table
        """

        template = get_template("templates/create_table.sql")
        self.execute(template.render(table=table), commit=True)

