#!/usr/bin/env python

from decimal import Decimal
import warnings

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import journalism

class TestColumns(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )
        self.column_names = ('one', 'two', 'three')
        self.column_types = (journalism.IntColumn, journalism.IntColumn, journalism.TextColumn)

        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_stringify(self):
        self.assertEqual(str(self.table.columns['one']), "<journalism.columns.IntColumn: (1, 2, None)>")

    def test_stringify_long(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c')
        )
        
        self.table = journalism.Table(rows, self.column_types, self.column_names)

        self.assertEqual(str(self.table.columns['one']), "<journalism.columns.IntColumn: (1, 2, None, 1, 2, ...)>")

    def test_length(self):
        self.assertEqual(len(self.table.columns), 3)

    def test_get_column_data(self):
        self.assertSequenceEqual(self.table.columns['one']._data(), (1, 2, None))

    def test_get_column_data_cached(self):
        c = self.table.columns['one']

        self.assertIs(c._cached_data, None)

        data = c._data()

        self.assertSequenceEqual(c._cached_data, (1, 2, None))
        
        data2 = c._data()

        self.assertIs(data, data2)

    def test_get_column(self):
        self.assertSequenceEqual(self.table.columns['one'], (1, 2, None))

    def test_get_column_cached(self):
        c = self.table.columns['one']
        c2 = self.table.columns['one']
        c3 = self.table.columns['two']

        self.assertIs(c, c2)
        self.assertIsNot(c2, c3)

    def test_get_invalid_column(self):
        with self.assertRaises(journalism.ColumnDoesNotExistError):
            self.table.columns['four']

    def test_column_length(self):
        self.assertEqual(len(self.table.columns['one']), 3)

    def test_get_column_item(self):
        self.assertEqual(self.table.columns['one'][1], 2)

    def test_column_contains(self):
        self.assertEqual(1 in self.table.columns['one'], True)
        self.assertEqual(3 in self.table.columns['one'], False)

    def test_iterate_columns(self):
        it = iter(self.table.columns)

        self.assertSequenceEqual(next(it), (1, 2, None))
        self.assertSequenceEqual(next(it), (2, 3, 4))
        self.assertSequenceEqual(next(it), ('a', 'b', 'c'))

        with self.assertRaises(StopIteration):
            next(it)

    def test_immutable(self):
        with self.assertRaises(TypeError):
            self.table.columns['one'] = 'foo'

        with self.assertRaises(TypeError):
            self.table.columns['one'][0] = 100

    def test_any(self):
        self.assertEqual(self.table.columns['one'].any(lambda d: d == 2), True)
        self.assertEqual(self.table.columns['one'].any(lambda d: d == 5), False)

    def test_all(self):
        self.assertEqual(self.table.columns['one'].all(lambda d: d != 5), True)
        self.assertEqual(self.table.columns['one'].all(lambda d: d == 2), False)

    def test_count(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = journalism.Table(rows, self.column_types, self.column_names)

        self.assertEqual(table.columns['one'].count(1), 3)
        self.assertEqual(table.columns['one'].count(4), 0)
        self.assertEqual(table.columns['one'].count(None), 1)

    def test_counts(self):
        rows = (
            (1, 2, 'a'),
            (2, 3, 'b'),
            (None, 4, 'c'),
            (1, 2, 'a'),
            (1, 2, 'a')
        )

        table = journalism.Table(rows, self.column_types, self.column_names)

        new_table = table.columns['one'].counts()

        self.assertIsNot(new_table, table)
        self.assertEqual(len(new_table.columns), 2)
        self.assertEqual(len(new_table.rows), 3) 

        self.assertSequenceEqual(new_table.rows[0], (1, 3))
        self.assertSequenceEqual(new_table.rows[1], (2, 1))
        self.assertSequenceEqual(new_table.rows[2], (None, 1))

        self.assertSequenceEqual(new_table.columns['one'], (1, 2, None))
        self.assertSequenceEqual(new_table.columns['count'], (3, 1, 1))

class TestTextColumn(unittest.TestCase):
    def test_validate(self):
        column = journalism.TextColumn(None, 'one')
        column._data = lambda: ('a', 'b', 'c')
        column.validate()

        column._data = lambda: ('a', 'b', 3)

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

    def test_cast(self):
        column = journalism.TextColumn(None, 'one')
        column._data = lambda: ('a', 1, None, Decimal('2.7'))
        self.assertSequenceEqual(column._cast(), ('a', '1', None, '2.7'))

class TestIntColumn(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (1, 2, 'a'),
            (1, 1, 3, 'b'),
            (None, 4, 'c'),
            (2, 1, 'c')
        )
        self.column_names = ('one', 'two', 'three')
        self.column_types = (journalism.IntColumn, journalism.IntColumn, journalism.TextColumn)

        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_validate(self):
        column = journalism.IntColumn(None, 'one')
        column._data = lambda: (1, 2, 3)
        column.validate()

        column._data = lambda: (1, 'a', 3)

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

    def test_cast(self):
        column = journalism.IntColumn(None, 'one')
        column._data = lambda: (2, 1, None, Decimal('2.7'))
        self.assertSequenceEqual(column._cast(), (2, 1, None, 2))

    def test_sum(self):
        self.assertEqual(self.table.columns['one'].sum(), 4)
        self.assertEqual(self.table.columns['two'].sum(), 8)

    def test_min(self):
        self.assertEqual(self.table.columns['one'].min(), 1)
        self.assertEqual(self.table.columns['two'].min(), 1)

    def test_max(self):
        self.assertEqual(self.table.columns['one'].max(), 2)
        self.assertEqual(self.table.columns['two'].max(), 4)

    def test_median(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].median()

        self.assertEqual(self.table.columns['two'].median(), Decimal('1.5'))

    def test_mode(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].mode()

        self.assertEqual(self.table.columns['two'].mode(), 1)

    def test_variance(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].variance()

        self.assertEqual(self.table.columns['two'].variance(), Decimal('1.5'))

    def test_stdev(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].stdev()

        self.assertAlmostEqual(self.table.columns['two'].stdev(), Decimal('1.22474487'))

    def test_mad(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].mad()

        self.assertAlmostEqual(self.table.columns['two'].mad(), Decimal('0.5'))

class TestDecimalColumn(unittest.TestCase):
    def setUp(self):
        self.rows = (
            (Decimal('1.1'), Decimal('2.19'), 'a'),
            (Decimal('2.7'), Decimal('3.42'), 'b'),
            (None, Decimal('4.1'), 'c'),
            (Decimal('2.7'), Decimal('3.42'), 'c')
        )
        self.column_names = ('one', 'two', 'three')
        self.column_types = (journalism.DecimalColumn, journalism.DecimalColumn, journalism.TextColumn)

        self.table = journalism.Table(self.rows, self.column_types, self.column_names)

    def test_validate(self):
        column = journalism.DecimalColumn(None, 'one')
        column._data = lambda: (Decimal('1.0'), Decimal('2.1'), Decimal('3.3'))
        column.validate()

        column._data = lambda: (Decimal('1.0'), 'a', Decimal('3.3'))

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

        # Floats, not decimals
        column._data = lambda: (1.0, 2.1, 3.3)

        with self.assertRaises(journalism.ColumnValidationError):
            column.validate()

    def test_cast(self):
        column = journalism.DecimalColumn(None, 'one')
        column._data = lambda: (2, 1, None, Decimal('2.7'))
        self.assertSequenceEqual(column._cast(), (Decimal('2'), Decimal('1'), None, Decimal('2.7')))

    def test_cast_warn(self):
        column = journalism.DecimalColumn(None, 'one')
        column._data = lambda: (2, 1.1, None, Decimal('2.7'))

        with warnings.catch_warnings(record=True) as w:
            column._cast()

    def test_sum(self):
        self.assertEqual(self.table.columns['one'].sum(), Decimal('6.5'))
        self.assertEqual(self.table.columns['two'].sum(), Decimal('13.13'))

    def test_min(self):
        self.assertEqual(self.table.columns['one'].min(), Decimal('1.1'))
        self.assertEqual(self.table.columns['two'].min(), Decimal('2.19'))

    def test_max(self):
        self.assertEqual(self.table.columns['one'].max(), Decimal('2.7'))
        self.assertEqual(self.table.columns['two'].max(), Decimal('4.1'))

    def test_median(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].median()

        self.assertEqual(self.table.columns['two'].median(), Decimal('3.42'))

    def test_mode(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].mode()

        self.assertEqual(self.table.columns['two'].mode(), Decimal('3.42'))

    def test_variance(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].variance()
        
        self.assertEqual(self.table.columns['two'].variance().quantize(Decimal('0.01')), Decimal('0.47'))

    def test_stdev(self):
        with self.assertRaises(journalism.exceptions.NullComputationError):
            self.table.columns['one'].stdev()

        self.assertAlmostEqual(self.table.columns['two'].stdev().quantize(Decimal('0.01')), Decimal('0.69'))

