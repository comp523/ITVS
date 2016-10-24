"""
SQL Query Builder
"""

import abc

from typing import List, Union


class Condition:

    _param_counter = 0

    params = {}

    def __init__(self, *args):
        self.sql = ""
        nargs = len(args)
        if nargs > 0:
            column = args[0]
            operand, value = (args[1], args[2]) if nargs == 3 else ("=", args[1])
            if value is None:
                param = "NULL"
                if operand == "=":
                    operand = "IS"
            else:
                if value in Condition.params.values():
                    keys = Condition.params.keys()
                    values = Condition.params.values()
                    param_id = list(keys)[list(values).index(value)]
                    param = ":{}".format(param_id)
                else:
                    param = ":_c{}".format(Condition._param_counter)
                    Condition._param_counter += 1
                    self.params[param[1:]] = value  # slice the colon from param
            self.sql = "{} {} {}".format(column, operand, param)

    def __and__(self, other: 'Condition') -> 'Condition':

        condition = Condition()
        # Logical XOR to check if only one condition is empty
        if bool(self.sql) is not bool(other.sql):
            condition.sql = self.sql if self.sql else other.sql
        else:
            condition.sql = "({} AND {})".format(self.sql, other.sql)
        condition.params = {**self.params, **other.params}
        return condition

    def __or__(self, other: 'Condition') -> 'Condition':

        condition = Condition()
        if bool(self.sql) is not bool(other.sql):
            condition.sql = self.sql if self.sql else other.sql
        else:
            condition.sql = "({} OR {})".format(self.sql, other.sql)
        condition.params = {**self.params, **other.params}
        return condition

    def __invert__(self):

        condition = Condition()
        condition.sql = "NOT ({})".format(self.sql)
        condition.params = self.params
        return condition


class Query(object, metaclass=abc.ABCMeta):
    """
    Base class for all queries
    """

    @property
    @abc.abstractmethod
    def sql(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def params(self) -> dict:
        pass


class InsertQuery(Query):
    """"""

    FORMAT = "INSERT INTO {table} {columns} VALUES {values}"

    def __init__(self, table: str, values: dict):

        params = {key: "_i{}".format(i) for i, key in enumerate(values)}
        self._params = {param: values[key] for key, param in params.items()}
        self._sql = InsertQuery.FORMAT.format(table=table,
                                              columns=params.keys(),
                                              values=params.values())

    @property
    def sql(self) -> str:
        return self._sql

    @property
    def params(self) -> dict:
        return self._params


class SelectQuery(Query):
    """"""

    FORMAT = "{select} {columns} FROM {table} {where}"

    def __init__(self, table: str,
                 columns: Union[str, List[str]]="*",
                 where: Condition=None,
                 distinct: bool=False):

        if type(columns) is list:
            columns = ", ".join(columns)
        self._params, where = ((where.params, "WHERE {}".format(where.sql))
                               if where else ({}, ""))
        select = "SELECT"
        if distinct:
            select += " DISTINCT"
        self._sql = SelectQuery.FORMAT.format(select=select,
                                              columns=columns,
                                              table=table,
                                              where=where)

    @property
    def sql(self) -> str:
        return self._sql

    @property
    def params(self) -> dict:
        return self._params


class UpdateQuery(Query):
    """
    """

    FORMAT = "UPDATE {table} SET ({columns}) WHERE {where}"

    def __init__(self, table: str, values: dict, where: Condition):

        params = {key: "_u{}".format(i) for i, key in enumerate(values.keys())}
        columns = ", ".join(["{}=:{}".format(key, param)
                             for key, param in params.items()])
        self._params = {param: values[key] for key, param in params.items()}
        self._params.update(where.params)
        self._sql = UpdateQuery.FORMAT.format(table=table,
                                              columns=columns,
                                              where=where.sql)

    @property
    def sql(self) -> str:
        return self._sql

    @property
    def params(self) -> dict:
        return self._params