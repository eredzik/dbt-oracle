import agate
from typing import List, Optional, Tuple, Any, Iterable, Dict
from contextlib import contextmanager
import enum
import time

import dbt.exceptions
import cx_Oracle
from cx_Oracle import Connection as OracleConnection

from dbt.logger import GLOBAL_LOGGER as logger

from dataclasses import dataclass

from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager
from dbt.contracts.connection import Connection as DBTConnection
from dbt.events.types import InfoLevel, Cli, File
from dbt.events.functions import fire_event


@dataclass
class HookInfo(InfoLevel, Cli, File):
    msg: str
    code: str = "E040"

    def message(self) -> str:
        return f"{self.msg}."


@dataclass
class DummyResponse:
    _message: str


class OracleConnectionMethod(enum.Enum):
    HOST = 1
    TNS = 2
    CONNECTION_STRING = 3


@dataclass
class OracleAdapterCredentials(Credentials):
    """Collect Oracle credentials

    An OracleConnectionMethod is inferred from the combination
    of parameters profiled in the profile.
    """

    user: str
    password: str
    # Note: The port won't be used if the host is not provided
    # Default Oracle database port
    port: Optional[int] = 1521
    host: Optional[str] = None
    service: Optional[str] = None
    connection_string: Optional[str] = None
    debug_log_commands: Optional[bool] = False
    cursor_precode: Optional[str] = None

    _ALIASES = {"dbname": "database", "pass": "password"}

    @property
    def type(self):
        return "oracle"

    def _connection_keys(self) -> Tuple[str]:
        """
        List of keys to display in the `dbt debug` output. Omit password.
        """
        return (
            "user",
            "database",
            "schema",
            "host",
            "port",
            "service",
            "connection_string",
        )

    def connection_method(self) -> OracleConnectionMethod:
        "Return an OracleConnecitonMethod inferred from the configuration"
        if self.connection_string:
            return OracleConnectionMethod.CONNECTION_STRING
        elif self.host:
            return OracleConnectionMethod.HOST
        else:
            return OracleConnectionMethod.TNS

    def get_dsn(self) -> str:
        """Create dsn for cx_Oracle for either any connection method

        See https://cx-oracle.readthedocs.io/en/latest/user_guide/connection_handling.html"""

        method = self.connection_method()
        if method == OracleConnectionMethod.TNS:
            return self.database
        if method == OracleConnectionMethod.CONNECTION_STRING:
            return self.connection_string

        # Assume host connection method OracleConnectionMethod.HOST

        # If the 'service' property is not provided, use 'database' property for
        # purposes of connecting.
        if self.service:
            service = self.service
        else:
            service = self.database

        return f"{self.host}:{self.port}/{service}"


class OracleAdapterConnectionManager(SQLConnectionManager):
    TYPE = "oracle"

    @classmethod
    def open(cls, connection: DBTConnection):
        if connection.state == "open":
            logger.debug("Connection is already open, skipping open.")
            return connection
        credentials = cls.get_credentials(connection.credentials)
        method = credentials.connection_method()
        dsn = credentials.get_dsn()

        logger.debug(
            f"Attempting to connect using Oracle method: '{method}' "
            f"and dsn: '{dsn}'"
        )
        try:
            handle = cx_Oracle.connect(
                credentials.user, credentials.password, dsn, encoding="UTF-8"
            )
            connection.handle = handle
            connection.state = "open"

        except cx_Oracle.DatabaseError as e:
            logger.info(
                f"Got an error when attempting to open an Oracle " f"connection: '{e}'"
            )
            connection.handle = None
            connection.state = "fail"

            raise dbt.exceptions.FailedToConnectException(str(e))

        return connection

    @classmethod
    def cancel(cls, connection: DBTConnection):
        connection_name = connection.name
        oracle_connection = connection.handle

        logger.info("Cancelling query '{}' ".format(connection_name))

        try:
            OracleConnection.close(oracle_connection)
        except Exception as e:
            logger.error("Error closing connection for cancel request")
            raise Exception(str(e))

        logger.info("Canceled query '{}'".format(connection_name))

    @classmethod
    def get_status(cls, cursor):
        # Do oracle cx has something for this? could not find it
        return DummyResponse("OK")

    @classmethod
    def get_response(cls, cursor):
        return DummyResponse("OK")

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except cx_Oracle.DatabaseError as e:
            logger.error("Oracle error: {}".format(str(e)))

            try:
                # attempt to release the connection
                self.release()
            except cx_Oracle.Error:
                logger.error("Failed to release connection!")
                pass

            raise dbt.exceptions.DatabaseException(str(sql) + str(e).strip()) from e

        except Exception as e:
            logger.error("Rolling back transaction.")
            self.release()
            if isinstance(e, dbt.exceptions.RuntimeException):
                # during a sql query, an internal to dbt exception was raised.
                # this sounds a lot like a signal handler and probably has
                # useful information, so raise it without modification.
                raise e

            raise dbt.exceptions.RuntimeException(e) from e

    @classmethod
    def get_credentials(cls, credentials) -> OracleAdapterCredentials:
        return credentials

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = {},
        abridge_sql_log: bool = False,
    ) -> Tuple[DBTConnection, Any]:
        connection = self.get_thread_connection()
        if auto_begin and connection.transaction_open is False:
            self.begin()

        logger.debug('Using {} connection "{}".'.format(self.TYPE, connection.name))

        with self.exception_handler(sql):
            if abridge_sql_log:
                log_sql = "{}...".format(sql[:512])
            else:
                log_sql = sql

            if connection._credentials.debug_log_commands:

                fire_event(
                    HookInfo(
                        "On {connection_name}: {sql}".format(
                            connection_name=connection.name,
                            sql=log_sql,
                        )
                    )
                )
            pre = time.time()

            cursor = connection.handle.cursor()
            if connection._credentials.cursor_precode:
                # print(f'ALTER SESSION SET SCHEMA "{connection._credentials.schema}"')
                # cursor.execute(
                #     f"ALTER SESSION SET CURRENT_SCHEMA = {connection._credentials.schema}"
                # )
                cursor.execute(connection._credentials.cursor_precode)
            cursor.execute(sql, bindings)
            connection.handle.commit()
            if connection._credentials.debug_log_commands:
                fire_event(
                    HookInfo(
                        "SQL status: {status} in {elapsed:0.2f} seconds".format(
                            status=self.get_status(cursor),
                            elapsed=(time.time() - pre),
                        )
                    ),
                )

            return connection, cursor

    def add_begin_query(self):
        connection = self.get_thread_connection()
        cursor = connection.handle.cursor
        return connection, cursor
