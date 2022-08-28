from sqlalchemy import Table
from sqlalchemy.schema import CreateTable
import datetime

def create_partitioned_table(session: object, table: Table, key: str) -> None:
    """
    creates table partitioned by range(key)
    """

    if table.exists(session.get_bind()):
        table.drop(session.get_bind())

    DDL = CreateTable(table).__str__() + f"PARTITION BY RANGE({key})\n;"

    session.execute(DDL)
    session.commit()


def create_partition(
    session: object, table_schema: str, table_name: str, date: datetime.date
) -> None:
    """
    creates partition of date partitioned table
    """

    partition_start = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    partition_end = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)

    relation = ".".join(
        list(filter(lambda x: x is not None, [table_schema, table_name]))
    )

    session.execute(
        f"""
    CREATE TABLE IF NOT EXISTS {relation}_{date.strftime("%Y_%m_%d")}
    PARTITION OF points
    FOR VALUES FROM ('{partition_start.isoformat()}') TO ('{partition_end.isoformat()}');
    """
    )

    session.commit()