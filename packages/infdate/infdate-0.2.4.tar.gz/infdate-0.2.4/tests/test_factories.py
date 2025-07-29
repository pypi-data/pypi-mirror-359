# -None*- coding: utf-8 -*-

"""
Tests for the infdate module
"""

import datetime

from math import inf, nan
from time import mktime
from unittest.mock import Mock, patch

import infdate

from . import test_base as tb


class FactoryFunctions(tb.VerboseTestCase):
    """Factory functions in the module"""

    @patch.object(infdate, "RealDate")
    def test_private__from_datetime_object(self, mock_real_date):
        """private _from_datetime_object() factory function"""
        # pylint: disable=protected-access ; required to test private function
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            mocked_date = Mock(year=year, month=month, day=day)
            infdate._from_datetime_object(mocked_date)
            mock_real_date.assert_called_with(year, month, day)
        #

    @patch.object(infdate, "_from_datetime_object")
    def testdatetime(self, mock_private_fdo):
        """fromdatetime() factory function"""
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            mocked_date = Mock(year=year, month=month, day=day)
            infdate.fromdatetime(mocked_date)
            mock_private_fdo.assert_called_with(mocked_date)
        #

    @patch.object(infdate, "_from_datetime_object")
    def test_deprecated_from_datetime_object(self, mock_private_fdo):
        """deprecated from_datetime_object() factory function"""
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            mocked_date = Mock(year=year, month=month, day=day)
            with self.subTest("deprecation warning", mocked_date=mocked_date):
                self.assertWarns(
                    DeprecationWarning, infdate.from_datetime_object, mocked_date
                )
            #
            mock_private_fdo.assert_called_with(mocked_date)
        #

    @patch("infdate.datetime")
    @patch.object(infdate, "_from_datetime_object")
    def test_deprecated_from_native_type(self, mock_private_fdo, mock_datetime):
        """deprecated from_native_type() factory function"""
        for native_data, params in (
            ("2022-12-31T23:59:59.321Z", {}),
            ("2023-05-23T11:00:15.654321Z", {}),
            ("2008-04-06", {"fmt": "%Y-%m-%d"}),
            (inf, {}),
            (-inf, {}),
            (None, {}),
            (None, {"past_bound": False}),
            (None, {"past_bound": True}),
        ):
            if isinstance(native_data, str):
                with self.subTest(
                    "Real date",
                    native_data=native_data,
                    params=params,
                ):
                    mocked_intermediate_result = Mock()
                    mock_datetime.strptime.return_value = mocked_intermediate_result
                    self.assertWarns(
                        DeprecationWarning,
                        infdate.from_native_type,
                        native_data,
                        **params,
                    )
                    mock_datetime.strptime.assert_called_with(
                        native_data,
                        params.get("fmt", infdate.ISO_DATETIME_FORMAT_UTC),
                    )
                    mock_private_fdo.assert_called_with(mocked_intermediate_result)
                #
            else:
                with self.subTest(
                    "Infinity",
                    native_data=native_data,
                    params=params,
                ):
                    self.assertWarns(
                        DeprecationWarning,
                        infdate.from_native_type,
                        native_data,
                        **params,
                    )
                #
            #
        #

    @patch("infdate.datetime")
    @patch.object(infdate, "_from_datetime_object")
    def test_fromnative(self, mock_private_fdo, mock_datetime):
        """from_native() factory function"""
        for native_data, params, expected_result in (
            ("2022-12-31T23:59:59.321Z", {}, (2022, 12, 31)),
            ("2023-05-23T11:00:15.654321Z", {}, (2023, 5, 23)),
            ("2008-04-06", {"fmt": "%Y-%m-%d"}, (2008, 4, 6)),
            (inf, {}, infdate.INFINITE_FUTURE),
            (-inf, {}, infdate.INFINITE_PAST),
            (None, {}, infdate.INFINITE_FUTURE),
            (None, {"past_bound": False}, infdate.INFINITE_FUTURE),
            (None, {"past_bound": True}, infdate.INFINITE_PAST),
        ):
            if isinstance(native_data, str):
                with self.subTest(
                    "Real date",
                    native_data=native_data,
                    params=params,
                    expected_result=expected_result,
                ):
                    mocked_intermediate_result = Mock()
                    mock_datetime.strptime.return_value = mocked_intermediate_result
                    mock_private_fdo.return_value = expected_result
                    result = infdate.fromnative(native_data, **params)
                    mock_datetime.strptime.assert_called_with(
                        native_data,
                        params.get("fmt", infdate.ISO_DATETIME_FORMAT_UTC),
                    )
                    mock_private_fdo.assert_called_with(mocked_intermediate_result)
                    self.assertEqual(result, expected_result)
                #
            else:
                with self.subTest(
                    "Infinity",
                    native_data=native_data,
                    params=params,
                    expected_result=expected_result,
                ):
                    self.assertIs(
                        infdate.fromnative(native_data, **params), expected_result
                    )
                #
            #
        #
        for source in (1, -7, 3.5, True, False):
            with self.subTest("unhandled value", source=source):
                self.assertRaisesRegex(
                    ValueError,
                    f"^Don’t know how to convert {source!r} into a date$",
                    infdate.fromnative,
                    source,
                )
            #
        #

    @patch("infdate.date")
    @patch.object(infdate, "_from_datetime_object")
    def test_fromtimestamp(self, mock_private_fdo, mock_date):
        """test_fromtimestamp() factory function"""
        for timestamp, expected_result in (
            (-inf, infdate.INFINITE_PAST),
            (inf, infdate.INFINITE_FUTURE),
            (1e500, infdate.INFINITE_FUTURE),
        ):
            with self.subTest(
                "infinity", timestamp=timestamp, expected_result=expected_result
            ):
                self.assertIs(infdate.fromtimestamp(timestamp), expected_result)
            #
        #
        for stdlib_date in (
            datetime.date.min,
            datetime.date(1000, 1, 1),
            datetime.date(2022, 2, 22),
            datetime.date.max,
        ):
            timestamp = mktime(stdlib_date.timetuple())
            with self.subTest(
                "regular_result", timestamp=timestamp, stdlib_date=stdlib_date
            ):
                mocked_final_result = Mock(
                    year=stdlib_date.year, month=stdlib_date.month, day=stdlib_date.day
                )
                mock_date.fromtimestamp.return_value = stdlib_date
                mock_private_fdo.return_value = mocked_final_result
                self.assertEqual(infdate.fromtimestamp(timestamp), mocked_final_result)
                mock_date.fromtimestamp.assert_called_with(timestamp)
                mock_private_fdo.assert_called_with(stdlib_date)
            #
        #

    def test_fromtimestamp_errors(self):
        """test_fromtimestamp() factory function errors"""
        for timestamp in (
            mktime(datetime.date.min.timetuple()) - 1,
            mktime(datetime.date.max.timetuple()) + 86400,
        ):
            with self.subTest(
                "unsupported date, re-raised value error", timestamp=timestamp
            ):
                self.assertRaises(
                    ValueError,
                    infdate.fromtimestamp,
                    timestamp,
                )
            #
        #

    @patch("infdate.date")
    @patch.object(infdate, "_from_datetime_object")
    def test_fromordinal(self, mock_private_fdo, mock_date):
        """fromordinal() factory function"""
        for ordinal, expected_result in (
            (-inf, infdate.INFINITE_PAST),
            (inf, infdate.INFINITE_FUTURE),
            (1e500, infdate.INFINITE_FUTURE),
        ):
            with self.subTest(
                "infinity", ordinal=ordinal, expected_result=expected_result
            ):
                self.assertIs(infdate.fromordinal(ordinal), expected_result)
            #
        #
        for ordinal, intermediate_result in (
            (2.1, datetime.date(1, 1, 2)),
            (730120.0, datetime.date(2000, 1, 1)),
        ):
            with self.subTest(
                "fromordinal", ordinal=ordinal, intermediate_result=intermediate_result
            ):
                mocked_final_result = Mock()
                mock_date.fromordinal.return_value = intermediate_result
                mock_private_fdo.return_value = mocked_final_result
                self.assertEqual(infdate.fromordinal(ordinal), mocked_final_result)
                mock_date.fromordinal.assert_called_with(int(ordinal))
                mock_private_fdo.assert_called_with(intermediate_result)
            #
        #
        default_overflow_re = "^RealDate value out of range$"
        for ordinal, exception_class, error_re in (
            (-1, OverflowError, default_overflow_re),
            (0, OverflowError, default_overflow_re),
            (1234567890, OverflowError, default_overflow_re),
            (nan, ValueError, tb.NAN_INT_CONVERSION_ERROR_RE),
        ):
            with self.subTest("overflow error", ordinal=ordinal):
                self.assertRaisesRegex(
                    exception_class,
                    error_re,
                    infdate.fromordinal,
                    ordinal,
                )
            #
        #

    @patch.object(infdate, "date")
    @patch.object(infdate, "_from_datetime_object")
    def test_fromisoformat(self, mock_private_fdo, mock_date):
        """fromisoformat() factory function"""
        for source, expected_object in (
            ("<inf>", infdate.INFINITE_FUTURE),
            ("<-inf>", infdate.INFINITE_PAST),
        ):
            with self.subTest(
                "fromisoformat", source=source, expected_object=expected_object
            ):
                self.assertIs(infdate.fromisoformat(source), expected_object)
            #
        #
        for source, expected_date in (
            ("2019-12-04", datetime.date(2019, 12, 4)),
            ("20191204", datetime.date(2019, 12, 4)),
            ("2021-W01-1", datetime.date(2021, 1, 4)),
        ):
            with self.subTest(
                "fromisoformat", source=source, expected_date=expected_date
            ):
                mock_date.fromisoformat.return_value = expected_date
                infdate.fromisoformat(source)
                mock_date.fromisoformat.assert_called_with(source)
                mock_private_fdo.assert_called_with(expected_date)
            #
        #

    @patch.object(infdate, "date")
    @patch.object(infdate, "_from_datetime_object")
    def test_fromisocalendar(self, mock_private_fdo, mock_date):
        """fromisocalendar() factory function"""
        for year, week, weekday, expected_date in (
            (2004, 1, 1, datetime.date(2003, 12, 29)),
            (2004, 1, 7, datetime.date(2004, 1, 4)),
            (2004, 53, 3, datetime.date(2004, 12, 29)),
        ):
            with self.subTest(
                "fromisocalendar",
                year=year,
                week=week,
                weekday=weekday,
                expected_date=expected_date,
            ):
                mock_date.fromisocalendar.return_value = expected_date
                infdate.fromisocalendar(year, week, weekday)
                mock_date.fromisocalendar.assert_called_with(year, week, weekday)
                mock_private_fdo.assert_called_with(expected_date)
            #
        #

    @patch.object(infdate, "date")
    @patch.object(infdate, "_from_datetime_object")
    def test_today(self, mock_private_fdo, mock_date):
        """today() factory function"""
        mocked_date = Mock(year=2025, month=6, day=17)
        mock_date.today.return_value = mocked_date
        infdate.today()
        mock_date.today.assert_called_with()
        mock_private_fdo.assert_called_with(mocked_date)
