# -None*- coding: utf-8 -*-

"""
Tests for the infdate module: date classes
"""

import datetime
import secrets

from math import inf, isnan, nan
from time import struct_time
from unittest.mock import call, patch

import infdate

from . import test_base as tb


def random_deterministic_date() -> infdate.GenericDate:
    """Helper function: create a random deterministic Date"""
    return infdate.fromordinal(secrets.randbelow(tb.MAX_ORDINAL) + 1)


class GenericDateBase(tb.VerboseTestCase):
    """GenericDate objects - base functionality"""

    def test_nan_not_allowed(self):
        """test initialization with nan"""
        self.assertRaisesRegex(
            ValueError, tb.NAN_INT_CONVERSION_ERROR_RE, infdate.GenericDate, nan
        )

    def test_toordinal(self):
        """initialization and .toordinal() method"""
        num = 1.23
        gd = infdate.GenericDate(num)
        self.assertEqual(gd.toordinal(), 1)

    # pylint: disable=comparison-with-itself ; to show lt/gt ↔ le/ge difference

    def test_lt(self):
        """gd_instance1 < gd_instance2 capability"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.INFINITE_PAST < random_date)
                self.assertFalse(random_date < infdate.INFINITE_PAST)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date < infdate.INFINITE_FUTURE)
                self.assertFalse(infdate.INFINITE_FUTURE < random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date < random_date)
            #
        #

    def test_le(self):
        """less than or equal"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.INFINITE_PAST <= random_date)
                self.assertFalse(random_date <= infdate.INFINITE_PAST)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= infdate.INFINITE_FUTURE)
                self.assertFalse(infdate.INFINITE_FUTURE <= random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= random_date)
            #
        #

    def test_gt(self):
        """greater than"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(infdate.INFINITE_PAST > random_date)
                self.assertTrue(random_date > infdate.INFINITE_PAST)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date > infdate.INFINITE_FUTURE)
                self.assertTrue(infdate.INFINITE_FUTURE > random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date > random_date)
            #
        #

    def test_ge(self):
        """greater than or equal"""

        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(infdate.INFINITE_PAST >= random_date)
                self.assertTrue(random_date >= infdate.INFINITE_PAST)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date >= infdate.INFINITE_FUTURE)
                self.assertTrue(infdate.INFINITE_FUTURE >= random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= random_date)
            #
        #

    def test_ne(self):
        """not equal"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.INFINITE_PAST != random_date)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.INFINITE_FUTURE != random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(infdate.INFINITE_PAST != infdate.INFINITE_PAST)
                self.assertFalse(infdate.INFINITE_FUTURE != infdate.INFINITE_FUTURE)
                self.assertFalse(random_date != random_date)
            #
        #

    def test_eq(self):
        """equal"""
        random_date = random_deterministic_date()
        with self.subTest("compared to <-inf>", random_date=random_date):
            self.assertFalse(infdate.INFINITE_PAST == random_date)
        #
        with self.subTest("compared to <inf>", random_date=random_date):
            self.assertFalse(infdate.INFINITE_FUTURE == random_date)
        #
        with self.subTest("compared to itself", random_date=random_date):
            self.assertTrue(infdate.INFINITE_PAST == infdate.INFINITE_PAST)
            self.assertTrue(infdate.INFINITE_FUTURE == infdate.INFINITE_FUTURE)
            self.assertTrue(random_date == random_date)
        #

    # pylint: enable=comparison-with-itself

    def test_bool(self):
        """bool(gd_instance) capability"""
        gd = infdate.GenericDate(3.579)
        self.assertFalse(gd)

    def test_hash(self):
        """bool(gd_instance) capability"""
        gd = infdate.GenericDate(0.5)
        self.assertEqual(hash(gd), hash("date with ordinal 0"))

    def test_repr(self):
        """repr(gd_instance) capability"""
        for base, expected_display in (
            (inf, "inf"),
            (-inf, "-inf"),
            (9.81, "9"),
            (314, "314"),
        ):
            gd = infdate.GenericDate(base)
            with self.subTest(
                "representation of",
                base=base,
                expected_display=expected_display,
            ):
                self.assertEqual(repr(gd), f"GenericDate({expected_display})")
            #
        #

    def test_str(self):
        """str(gd_instance) capability"""
        gd = infdate.GenericDate(777)
        mocked_isoformat_result = "[777]"
        with patch.object(gd, "isoformat") as mock_isoformat:
            mock_isoformat.return_value = mocked_isoformat_result
            result = str(gd)
            self.assertEqual(result, mocked_isoformat_result)
            mock_isoformat.assert_called_with()
        #

    def test_isoformat(self):
        """.isoformat() method"""
        gd = infdate.GenericDate(777)
        mocked_strftime_result = "[777]"
        with patch.object(gd, "strftime") as mock_strftime:
            mock_strftime.return_value = mocked_strftime_result
            result = str(gd)
            self.assertEqual(result, mocked_strftime_result)
            mock_strftime.assert_called_with(infdate.ISO_DATE_FORMAT)
        #

    def test_strftime(self):
        """.strftime() method"""
        gd = infdate.GenericDate(-inf)
        self.assertRaises(NotImplementedError, gd.strftime, "")

    def test_replace(self):
        """.replace() method"""
        gd = infdate.GenericDate(inf)
        self.assertRaises(NotImplementedError, gd.replace, year=1)

    def test_pretty(self):
        """.pretty() method"""
        gd = infdate.GenericDate(inf)
        self.assertRaises(NotImplementedError, gd.pretty)

    def test_tonative(self):
        """.tonative() method"""
        gd = infdate.GenericDate(inf)
        self.assertRaises(NotImplementedError, gd.tonative)


class GenericDateArithmetics(tb.VerboseTestCase):
    """GenericDate objects - arithmetics"""

    # pylint: disable=protected-access ; ok for testing

    def test_add_days(self):
        """._add_days() method"""
        for base, delta, expected_result_ordinal, expected_call, expected_self in (
            (inf, -inf, -inf, -inf, False),
            (inf, inf, inf, None, True),
            (inf, 2.5, inf, None, True),
            (-inf, inf, inf, inf, False),
            (-inf, -inf, -inf, None, True),
            (-inf, 77.98, -inf, None, True),
            (9.81, inf, inf, inf, False),
            (9.81, -inf, -inf, -inf, False),
            (1.234, 7.89, 8, 8, False),
            (7.62, 0, 7, None, True),
            (1.234, -5.678, -4, -4, False),
            (3.14, -0, 3, None, True),
        ):
            with patch.object(infdate, "fromordinal") as mock_fromordinal:
                gd = infdate.GenericDate(base)
                mock_fromordinal.return_value = infdate.GenericDate(
                    expected_result_ordinal
                )
                result = gd._add_days(delta)
                with self.subTest(
                    "result",
                    base=base,
                    delta=delta,
                    expected_result_ordinal=expected_result_ordinal,
                ):
                    self.assertEqual(result.toordinal(), expected_result_ordinal)
                #
                if expected_call:
                    with self.subTest(
                        "fromordinal() call with",
                        base=base,
                        delta=delta,
                        expected_call=expected_call,
                    ):
                        mock_fromordinal.assert_called_with(expected_call)
                    #
                elif expected_self:
                    with self.subTest(
                        "self returned",
                        base=base,
                        delta=delta,
                        expected_self=expected_self,
                    ):
                        self.assertIs(result, gd)
                    #
                #
            #
        #

    def test_add_and_radd(self):
        """gd_instance + delta capability"""
        for base, delta in (
            (inf, inf),
            (inf, -inf),
            (inf, 2.5),
            (-inf, -inf),
            (-inf, inf),
            (-inf, 77.98),
            (9.81, -inf),
            (9.81, inf),
            (1.234, -7.89),
            (7.62, -0),
            (1.234, 5.678),
            (3.14, 0.0),
        ):
            gd = infdate.GenericDate(base)
            with patch.object(gd, "_add_days") as mock_adder:
                _ = gd + delta
                with self.subTest(
                    f"GenericDate({base}) + {delta} → Gen…()._add_days({delta}) call"
                ):
                    mock_adder.assert_called_with(delta)
                #
                _ = delta + gd
                with self.subTest(
                    f"{delta} + GenericDate({base}) → Gen…()._add_days({delta}) call"
                ):
                    mock_adder.assert_called_with(delta)
                #
            #
        #

    def test_sub_number(self):
        """gd_instance - number capability"""
        for base, delta, expected_result_ordinal, expected_call, expected_self in (
            (inf, inf, -inf, -inf, False),
            (inf, -inf, inf, None, True),
            (inf, 2.5, inf, None, True),
            (-inf, -inf, inf, inf, False),
            (-inf, inf, -inf, None, True),
            (-inf, 77.98, -inf, None, True),
            (9.81, -inf, inf, inf, False),
            (9.81, inf, -inf, -inf, False),
            (1.234, -7.89, 8, 7.89, False),
            (7.62, -0, 7, None, True),
            (1.234, 5.678, -4, -5.678, False),
            (3.14, 0.0, 3, None, True),
        ):
            gd = infdate.GenericDate(base)
            with patch.object(gd, "_add_days") as mock_adder:
                if expected_self:
                    mock_adder.return_value = gd
                else:
                    mock_adder.return_value = infdate.GenericDate(
                        expected_result_ordinal
                    )
                #
                result = gd - delta
                with self.subTest(
                    "result",
                    base=base,
                    delta=delta,
                    expected_result_ordinal=expected_result_ordinal,
                ):
                    self.assertEqual(result.toordinal(), expected_result_ordinal)
                #
                if expected_call:
                    with self.subTest(
                        "._add_days() call with",
                        base=base,
                        delta=delta,
                        expected_call=expected_call,
                    ):
                        mock_adder.assert_called_with(expected_call)
                    #
                elif expected_self:
                    with self.subTest(
                        "self returned",
                        base=base,
                        delta=delta,
                        expected_self=expected_self,
                    ):
                        self.assertIs(result, gd)
                    #
                #
            #
        #

    def test_sub_date(self):
        """gd_instance1 - gd_instance2 capability"""
        for first, second, expected_result in (
            (inf, inf, nan),
            (inf, -inf, inf),
            (inf, 2.5, inf),
            (-inf, -inf, nan),
            (-inf, inf, -inf),
            (-inf, 77.98, -inf),
            (9.81, -inf, inf),
            (9.81, inf, -inf),
            (1.234, -7.89, 8),
            (7.62, -0, 7),
            (1.234, 5.678, -4),
            (3.14, 0.0, 3),
        ):
            gd1 = infdate.GenericDate(first)
            gd2 = infdate.GenericDate(second)
            result = gd1 - gd2
            with self.subTest(
                "result",
                first=first,
                second=second,
                expected_result=expected_result,
            ):
                if isnan(expected_result):
                    self.assertTrue(isnan(result))
                else:
                    self.assertEqual(result, expected_result)
                #
            #
        #

    def test_sub_stdlib_date(self):
        """gd_instance - stdlib_date capability"""
        for gd_ordinal, stdlib_date_ordinal, expected_result in (
            (inf, 981, inf),
            (-inf, 733981, -inf),
            (12, 1234, -1222),
            (762, 1, 761),
            (99999.99, 7777, 92222),
        ):
            gd_instance = infdate.GenericDate(gd_ordinal)
            stdlib_date = datetime.date.fromordinal(stdlib_date_ordinal)
            result = gd_instance - stdlib_date
            with self.subTest(
                "result",
                gd_ordinal=gd_ordinal,
                stdlib_date_ordinal=stdlib_date_ordinal,
                expected_result=expected_result,
            ):
                self.assertEqual(result, expected_result)
            #
        #

    def test_rsub_stdlib_date(self):
        """stdlib_date - gd_instance capability"""
        for stdlib_date_ordinal, gd_ordinal, expected_result in (
            (981, -inf, inf),
            (981, inf, -inf),
            (1234, -7.89, 1241),
            (762, -0, 762),
            (1234, 5.678, 1229),
            (314, 0.0, 314),
        ):
            stdlib_date = datetime.date.fromordinal(stdlib_date_ordinal)
            gd_instance = infdate.GenericDate(gd_ordinal)
            result = stdlib_date - gd_instance
            with self.subTest(
                "result",
                stdlib_date_ordinal=stdlib_date_ordinal,
                gd_ordinal=gd_ordinal,
                expected_result=expected_result,
            ):
                self.assertEqual(result, expected_result)
            #
        #


class InfinityDate(tb.VerboseTestCase):
    """InfinityDate class"""

    _icp = "inf_common_prefix"
    _ips = "inf_past_suffix"
    _ifs = "inf_future_suffix"

    def test_repr(self):
        """repr(id_instance) capability"""
        for params, expected_result in (
            ({}, "InfinityDate(past_bound=False)"),
            ({"past_bound": False}, "InfinityDate(past_bound=False)"),
            ({"past_bound": True}, "InfinityDate(past_bound=True)"),
        ):
            infd = infdate.InfinityDate(**params)
            with self.subTest(
                "representation", params=params, expected_result=expected_result
            ):
                self.assertEqual(repr(infd), expected_result)
            #
        #

    def test_strftime(self):
        """.strftime() method"""
        for past_bound, expected_result in (
            (False, "<inf>"),
            (True, "<-inf>"),
        ):
            infd = infdate.InfinityDate(past_bound=past_bound)
            with self.subTest(
                "strftime", past_bound=past_bound, expected_result=expected_result
            ):
                self.assertEqual(infd.strftime(""), expected_result)
            #
        #

    def test_replace(self):
        """.replace() method"""
        infd = infdate.InfinityDate()
        self.assertRaisesRegex(
            TypeError,
            r"^InfinityDate instances do not support .replace\(\)$",
            infd.replace,
            month=12,
        )

    def test_pretty(self):
        """.pretty() method"""
        infinite_past = infdate.InfinityDate(past_bound=True)
        infinite_future = infdate.InfinityDate()
        for kwargs, infinite_past_result, infinite_future_result in (
            ({}, "<-inf>", "<inf>"),
            ({self._icp: "never ever"}, "never ever", "never ever"),
            ({self._icp: "∝", self._ips: "⤒", self._ifs: "↥"}, "∝⤒", "∝↥"),
            (
                {self._ips: "never before", self._ifs: "never after"},
                "never before",
                "never after",
            ),
        ):
            with self.subTest(
                "infinite past", infinite_past_result=infinite_past_result, **kwargs
            ):
                self.assertEqual(infinite_past.pretty(**kwargs), infinite_past_result)
                #
            #
            with self.subTest(
                "infinite furture",
                infinite_future_result=infinite_future_result,
                **kwargs,
            ):
                self.assertEqual(
                    infinite_future.pretty(**kwargs), infinite_future_result
                )
                #
            #
        #

    def test_tonative(self):
        """.tonative() method"""
        infinite_past = infdate.InfinityDate(past_bound=True)
        infinite_future = infdate.InfinityDate()
        for exact, infinite_past_result, infinite_future_result in (
            (True, -inf, inf),
            (False, None, None),
        ):
            with self.subTest(
                "infinite past", exact=exact, infinite_past_result=infinite_past_result
            ):
                self.assertEqual(
                    infinite_past.tonative(exact=exact), infinite_past_result
                )
                #
            #
            with self.subTest(
                "infinite furture",
                exact=exact,
                infinite_future_result=infinite_future_result,
            ):
                self.assertEqual(
                    infinite_future.tonative(exact=exact), infinite_future_result
                )
                #
            #
        #


class RealDate(tb.VerboseTestCase):
    """RealDate class"""

    def test_attributes(self):
        """initinalization and attributes"""
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            rd = infdate.RealDate(year, month, day)
            with self.subTest("year attribute", rd=rd, year=year):
                self.assertEqual(rd.year, year)
            #
            with self.subTest("month attribute", rd=rd, month=month):
                self.assertEqual(rd.month, month)
            #
            with self.subTest("day attribute", rd=rd, day=day):
                self.assertEqual(rd.day, day)
            #
        #
        for invalid_year in (-327, 0, 10000):
            with self.subTest("value error", invalid_year=invalid_year):
                self.assertRaises(ValueError, infdate.RealDate, invalid_year, 1, 1)
            #
        #

    def test_proxied_methods(self):
        """Method proxied from datetime.date:
        self.timetuple = self.__wrapped_date_object.timetuple
        self.weekday = self.__wrapped_date_object.weekday
        self.isoweekday = self.__wrapped_date_object.isoweekday
        self.isocalendar = self.__wrapped_date_object.isocalendar
        self.ctime = self.__wrapped_date_object.ctime
        """
        rd = infdate.RealDate(2025, 6, 25)
        for method_name, expected_result in (
            ("timetuple", struct_time((2025, 6, 25, 0, 0, 0, 2, 176, -1))),
            ("weekday", 2),
            ("isoweekday", 3),
            ("isocalendar", (2025, 26, 3)),
            ("ctime", "Wed Jun 25 00:00:00 2025"),
        ):
            with self.subTest(method_name, expected_result=expected_result):
                if isinstance(expected_result, tuple):
                    self.assertTupleEqual(getattr(rd, method_name)(), expected_result)
                else:
                    self.assertEqual(getattr(rd, method_name)(), expected_result)
                #
            #
        #

    def test_repr(self):
        """repr(rd_instance) capability"""
        for year, month, day, expected_parentheses_content in (
            (1996, 6, 25, "1996, 6, 25"),
            (1, 1, 1, "1, 1, 1"),
            (9999, 12, 31, "9999, 12, 31"),
        ):
            rd = infdate.RealDate(year, month, day)
            with self.subTest(
                "representation",
                year=year,
                month=month,
                day=day,
                expected_parentheses_content=expected_parentheses_content,
            ):
                self.assertEqual(repr(rd), f"RealDate({expected_parentheses_content})")
            #
        #

    def test_bool(self):
        """bool(rd_instance) capabiliry"""
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            with self.subTest("bool", year=year, month=month, day=day):
                self.assertTrue(infdate.RealDate(year, month, day))
            #
        #

    # pylint: disable=protected-access ; required for testing

    def test_strftime(self):
        """.strftime() method"""
        for year, month, day, format_, expected_result in (
            (1996, 6, 25, "", "1996-06-25"),
            (1, 2, 3, "%m/%d/%y", "3/2/01"),
            (9999, 12, 31, "%d.%m.%y", "31.12.99"),
        ):
            rd = infdate.RealDate(year, month, day)
            with patch.object(rd, "_wrapped_date_object") as mock_date:
                mock_date.strftime.return_value = expected_result
                result = rd.strftime(format_)
                with self.subTest(
                    "result value",
                    rd=rd,
                    format_=format_,
                    expected_result=expected_result,
                ):
                    self.assertEqual(result, expected_result)
                #
                with self.subTest(
                    "mocked_call",
                    rd=rd,
                    format_=format_,
                    expected_result=expected_result,
                ):
                    self.assertListEqual(
                        mock_date.mock_calls,
                        [call.strftime(format_ or infdate.ISO_DATE_FORMAT)],
                    )
                #
            #
        #

    def test_replace(self):
        """.strftime() method"""
        for year, month, day, replace_args, expected_result in (
            (1996, 6, 25, {"month": 1}, infdate.RealDate(1996, 1, 25)),
            (1, 2, 3, {"day": 28}, infdate.RealDate(1, 2, 28)),
            (9999, 12, 31, {"year": 2023, "month": 7}, infdate.RealDate(2023, 7, 31)),
        ):
            with patch.object(infdate, "from_datetime_object") as mock_factory:
                rd = infdate.RealDate(year, month, day)
                mock_factory.return_value = expected_result
                result = rd.replace(**replace_args)
                with self.subTest(
                    "result value",
                    rd=rd,
                    replace_args=replace_args,
                    expected_result=expected_result,
                ):
                    self.assertEqual(result, expected_result)
                #
                internal_replace_args = {
                    "year": expected_result.year,
                    "month": expected_result.month,
                    "day": expected_result.day,
                }
                with self.subTest(
                    "mocked_call",
                    rd=rd,
                    replace_args=replace_args,
                    internal_replace_args=internal_replace_args,
                ):
                    mock_factory.assert_called_with(
                        rd._wrapped_date_object.replace(**internal_replace_args)
                    )
                #
            #
        #

    def test_pretty(self):
        """.pretty() method"""
        for year, month, day, fmt, expected_result in (
            (1996, 6, 25, "%d.%m.%Y", "25.06.1996"),
            (1, 2, 3, "%m/%d/%y", "02/03/01"),
            (9999, 12, 31, "%Y-%m", "9999-12"),
            (2025, 6, 25, "", "2025-06-25"),
        ):
            rd = infdate.RealDate(year, month, day)
            with self.subTest("result value", fmt=fmt, expected_result=expected_result):
                self.assertEqual(rd.pretty(fmt=fmt), expected_result)
            #
        #

    def test_tonative(self):
        """.tonative() method"""
        for year, month, day, fmt, expected_result in (
            (1996, 6, 25, "%d.%m.%Y", "25.06.1996"),
            (1, 2, 3, "%m/%d/%y", "02/03/01"),
            (9999, 12, 31, "%Y-%m", "9999-12"),
            (2025, 6, 25, "", "2025-06-25"),
        ):
            rd = infdate.RealDate(year, month, day)
            with self.subTest("result value", fmt=fmt, expected_result=expected_result):
                self.assertEqual(rd.tonative(fmt=fmt), expected_result)
            #
        #

    def test_random_date_within_limits(self):
        """The following relation
        infdate.INFINITE_PAST < infdate.REAL_MIN <= real_date_instance <= …
        … infdate.REAL_MAX < infdate.INFINITE_FUTURE
        should always be True
        """
        for iteration in range(1, 10000):
            random_date = random_deterministic_date()
            with self.subTest(
                "date within limits", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(
                    infdate.INFINITE_PAST
                    < infdate.REAL_MIN
                    <= random_date
                    <= infdate.REAL_MAX
                    < infdate.INFINITE_FUTURE
                )
            #
        #
