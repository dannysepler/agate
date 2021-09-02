#!/usr/bin/env python

from agate.aggregations.base import Aggregation


class First(Aggregation):
    """
    Returns the first value that passes a test.

    If the test is omitted, the aggregation will return the first value in the column.

    If no values pass the test, the aggregation will raise an exception.

    :param column_name:
        The name of the column to check.
    :param test:
        A function that takes a value and returns `True` or `False`. Test may be
        omitted when checking :class:`.Boolean` data.
    """
    def __init__(self, column_name, test=None):
        self._column_name = column_name
        self._test = test

    def get_aggregate_data_type(self, table):
        return table.get_column(self._column_name).data_type

    def validate(self, table):
        if self._test is not None:
            try:
                self.run(table)
            except StopIteration:
                raise ValueError('No values pass the given test.')

    def run(self, table):
        column = table.get_column(self._column_name)
        data = column.itervalues()

        if self._test is None:
            return next(data)

        return next(d for d in data if self._test(d))
