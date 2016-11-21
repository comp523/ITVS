"""
SQL Query Builder
"""

import abc


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
                    param = "%({})s".format(param_id)
                else:
                    param = "%(_c{})s".format(Condition._param_counter)
                    Condition._param_counter += 1
                    self.params[param[2:-2]] = value  # slice the colon from param
            self.sql = "{} {} {}".format(column, operand, param)

    def __and__(self, other):

        condition = Condition()
        # Logical XOR to check if only one condition is empty
        if bool(self.sql) is not bool(other.sql):
            condition.sql = self.sql if self.sql else other.sql
        else:
            condition.sql = "({} AND {})".format(self.sql, other.sql)
        condition.params = dict(self.params, **other.params)
        return condition

    def __or__(self, other):

        condition = Condition()
        if bool(self.sql) is not bool(other.sql):
            condition.sql = self.sql if self.sql else other.sql
        else:
            condition.sql = "({} OR {})".format(self.sql, other.sql)
        condition.params = dict(self.params, **other.params)
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
    def sql(self):
        pass

    @property
    @abc.abstractmethod
    def params(self):
        pass


class InsertQuery(Query):
    """"""

    FORMAT = "INSERT INTO {table} ({columns}) VALUES ({values})"

    def __init__(self, table, values):

        params = {key: "_i{}".format(i) for i, key in enumerate(values)}
        self._params = {param: values[key] for key, param in params.items()}
        values = ", ".join(["%({})s".format(v) for v in params.values()])
        self._sql = InsertQuery.FORMAT.format(table=table,
                                              columns=", ".join(params.keys()),
                                              values=values)

    @property
    def sql(self):
        return self._sql

    @property
    def params(self):
        return self._params


class SelectQuery(Query):
    """"""

    FORMAT = "{select} {columns} FROM {table} {where} {group} {order} {limit} {offset}"

    def __init__(self, table, columns="*", where=None, distinct=False,
                 order=None, limit=None, group=None, offset=None):

        limit = "LIMIT {}".format(limit) if limit else ""

        order = "ORDER BY {}".format(order) if order else ""

        group = "GROUP BY {}".format(group) if group else ""

        offset = "OFFSET {}".format(offset) if offset else ""

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
                                              where=where,
                                              group=group,
                                              order=order,
                                              limit=limit,
                                              offset=offset)

    @property
    def sql(self):
        return self._sql

    @property
    def params(self):
        return self._params


class UpdateQuery(Query):
    """
    """

    FORMAT = "UPDATE {table} SET {columns} WHERE {where}"

    def __init__(self, table, values, where):

        params = {key: "_u{}".format(i) for i, key in enumerate(values.keys())}
        columns = ", ".join(["{}=%({})s".format(key, param)
                             for key, param in params.items()])
        self._params = {param: values[key] for key, param in params.items()}
        self._params.update(where.params)
        self._sql = UpdateQuery.FORMAT.format(table=table,
                                              columns=columns,
                                              where=where.sql)

    @property
    def sql(self):
        return self._sql

    @property
    def params(self):
        return self._params
