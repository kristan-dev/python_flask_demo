import psycopg2
from psycopg2.extensions import quote_ident
import io
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from typing import List
import logging
import itertools
from config import cfg

# A way for you to create a DB connection using pyscopg2. You can use the code below to create seprate connections or use connection for your whole project

class Database:
    # NOTE: Use this class if you want to utlize one connection for your entire process
    db_usr = cfg["databases"]["demo"]["user"]
    db_pwd = cfg["databases"]["demo"]["password"]
    db_hst = cfg["databases"]["demo"]["host"]
    db_prt = cfg["databases"]["demo"]["port"]
    db_sch = cfg["databases"]["demo"]["database"]
    database_connection = None

    @classmethod
    def create_db_connection(cls):
        cls.database_connection = psycopg2.connect(
            user=cls.db_usr,
            password=cls.db_pwd,
            host=cls.db_hst,
            port=cls.db_prt,
            database=cls.db_sch,
        )

    @classmethod
    def commit_db_actions(cls):
        cls.database_connection.commit()

    @classmethod
    def close_db_connection(cls):
        cls.database_connection.close()

    @classmethod
    def rollback_db_actions(cls):
        cls.database_connection.rollback()

    @classmethod
    def return_select_rows(cls, sql_statement, arg_vals=None):
        try:
            if arg_vals is not None and arg_vals != "":
                cursor = cls.database_connection.cursor()
                cursor.execute(sql_statement, (arg_vals,))
                return cursor
            else:
                cursor = cls.database_connection.cursor()
                cursor.execute(sql_statement)
                return cursor
        except Exception as e:
            raise e

    @classmethod
    def get_cursor_as_dictionary(cls, sql_statement, arg_vals=None):
        if arg_vals is not None and arg_vals != "":
            cursor = cls.database_connection.cursor(
                "my-cursor", cursor_factory=psycopg2.extras.DictCursor
            )
            cursor.execute(sql_statement, (arg_vals,))
            return cursor
        else:
            cursor = cls.database_connection.cursor(
                "my-cursor", cursor_factory=psycopg2.extras.DictCursor
            )
            cursor.execute(sql_statement)
            return cursor


class connect:
    def __init__(self, database_config):
        self._database_config = database_config

    def __enter__(self):
        self.conn = connect_psycopg2(self._database_config)
        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.close()


def execute(db_creds, stmt):
    with connect(db_creds) as conn:
        cursor = conn.cursor()
        cursor.execute(stmt)
        conn.commit()


def query(query: str, db_creds: dict, qparams=[], batch_size: int = 200):
    """
  Performs a database query and allows interation through the result set.
  Batches results, so that only so many results are kept in memory at a time.
  """
    with connect(db_creds) as conn:
        cursor = conn.cursor()
        cursor.execute(query, qparams)
        results = cursor.fetchmany(batch_size)
        while len(results):
            for res in results:
                yield res

            results = cursor.fetchmany(batch_size)


def connect_psycopg2(db_opts):
    return psycopg2.connect(
        "dbname='{0}' user='{1}' password='{2}' host='{3}' port='{4}'".format(
            db_opts["database"],
            db_opts["user"],
            db_opts["password"],
            db_opts["host"],
            db_opts["port"],
        )
    )


# Engines need to be singletons. One per db per process.
engines = {}

def get_engine(db_opts) -> Engine:
    conn_string = "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
        db_opts["user"],
        db_opts["password"],
        db_opts["host"],
        db_opts["port"],
        db_opts["database"],
    )

    if conn_string not in engines:
        engines[conn_string] = create_engine(conn_string)

    return engines[conn_string]


def to_sql(
    engine,
    df,
    table,
    schema,
    if_exists="fail",
    sep="\t",
    encoding="utf8",
    index=False,
    dtype=None,
):
    # Create Table
    df[:0].to_sql(
        table, engine, schema=schema, if_exists=if_exists, index=index, dtype=dtype
    )

    # Prepare data
    output = io.StringIO()
    df.to_csv(
        output, sep=sep, header=False, encoding=encoding, index=index, na_rep="\\N"
    )
    output.seek(0)

    # Insert data
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.copy_from(output, schema + "." + table, sep=sep)
    connection.commit()
    cursor.close()


def sql_to_sql(
    db_config1: dict,
    db_config2: dict,
    select_query: str,
    to_schema: str,
    to_table: str,
    batch_size=1000,
):
    with connect_psycopg2(db_config1) as conn1:
        cursor = conn1.cursor()
        cursor.execute(select_query)
        columns = ",".join([col.name for col in cursor.description])
        record_placeholders = ",".join(["%s" for col in cursor.description])

        with connect_psycopg2(db_config2) as conn2:
            cursor2 = conn2.cursor()
            results = cursor.fetchmany(batch_size)
            inserted_cnt = 0
            next_results_cnt = len(results)

            while next_results_cnt:
                placeholders = ",".join(
                    ["({})".format(record_placeholders) for result in results]
                )
                insert_sql = """
          INSERT INTO {schema}.{table} ({columns})
          VALUES {records}
        """.format(
                    schema=quote_ident(to_schema, cursor2),
                    table=quote_ident(to_table, cursor2),
                    columns=columns,
                    records=placeholders,
                )
                query_params = list(itertools.chain.from_iterable(results))
                cursor2.execute(insert_sql, query_params)

                inserted_cnt += len(results)
                logging.info(
                    "{} Documents Imported to {}".format(inserted_cnt, to_table)
                )
                results = cursor.fetchmany(batch_size)
                next_results_cnt = len(results)

            conn2.commit()
