#!/usr/bin/env python

try:
    from cdecimal import Decimal
except ImportError:  # pragma: no cover
    from decimal import Decimal

from functools import lru_cache

from agate.data_types.base import DEFAULT_NULL_VALUES, DataType
from agate.exceptions import CastError

#: Default values which will be automatically cast to :code:`True`.
DEFAULT_TRUE_VALUES = set(['yes', 'y', 'true', 't', '1'])

#: Default values which will be automatically cast to :code:`False`.
DEFAULT_FALSE_VALUES = set(['no', 'n', 'false', 'f', '0'])


class Boolean(DataType):
    """
    Data representing true and false.

    Note that by default numerical `1` and `0` are considered valid boolean
    values, but other numbers are not.

    :param true_values: A sequence of values which should be cast to
        :code:`True` when encountered with this type.
    :param false_values: A sequence of values which should be cast to
        :code:`False` when encountered with this type.
    """
    def __init__(self, true_values=DEFAULT_TRUE_VALUES, false_values=DEFAULT_FALSE_VALUES,
                 null_values=DEFAULT_NULL_VALUES):
        super().__init__(null_values=null_values)

        self.true_values = true_values
        self.false_values = false_values

    @lru_cache(maxsize=1000)
    def cast(self, d):
        """
        Cast a single value to :class:`bool`.

        :param d: A value to cast.
        :returns: :class:`bool` or :code:`None`.
        """
        if d is None:
            return d

        t = type(d)
        if t is bool and t is not int:
            return d
        elif t is int or isinstance(d, Decimal):
            if d == 1:
                return True
            elif d == 0:
                return False
        elif isinstance(d, str):
            d = d.replace(',', '').strip()

            d_lower = d.lower()

            if d_lower in self.null_values:
                return None
            elif d_lower in self.true_values:
                return True
            elif d_lower in self.false_values:
                return False

        raise CastError('Can not convert value %s to bool.' % d)

    def jsonify(self, d):
        return d
