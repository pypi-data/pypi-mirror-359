# -*- coding: utf-8 -*-

"""
infdate: a wrapper around the standard library’s datetime.date objects,
capable of representing past and future infinity
"""

import warnings

from datetime import date, datetime
from math import inf, trunc
from typing import final, overload, Any, Final, TypeVar


# -----------------------------------------------------------------------------
# Internal module constants:
# TypeVar for GenericDate
# -----------------------------------------------------------------------------

_GD = TypeVar("_GD", bound="GenericDate")

_INFINITY_FORMS = (-inf, inf)


# -----------------------------------------------------------------------------
# Public module constants:
# format strings
# -----------------------------------------------------------------------------

INFINITE_PAST_DATE_DISPLAY: Final[str] = "<-inf>"
INFINITE_FUTURE_DATE_DISPLAY: Final[str] = "<inf>"

ISO_DATE_FORMAT: Final[str] = "%Y-%m-%d"
ISO_DATETIME_FORMAT_UTC: Final[str] = f"{ISO_DATE_FORMAT}T%H:%M:%S.%fZ"


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class GenericDate:
    """Base Date object derived from an ordinal"""

    def __init__(self, ordinal: int | float, /) -> None:
        """Create a date-like object"""
        if ordinal in _INFINITY_FORMS:
            self.__ordinal = ordinal
        else:
            self.__ordinal = trunc(ordinal)
        #

    def toordinal(self: _GD) -> int | float:
        """to ordinal (almost like date.toordinal())"""
        return self.__ordinal

    def __lt__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: less"""
        return self.__ordinal < other.toordinal()

    def __le__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: less or equal"""
        return self < other or self == other

    def __gt__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: greater"""
        return self.__ordinal > other.toordinal()

    def __ge__(self: _GD, other: _GD, /) -> bool:
        """Rich comparison: greater or equal"""
        return self > other or self == other

    def __eq__(self: _GD, other, /) -> bool:
        """Rich comparison: equals"""
        return self.__ordinal == other.toordinal()

    def __ne__(self: _GD, other, /) -> bool:
        """Rich comparison: does not equal"""
        return self.__ordinal != other.toordinal()

    def __bool__(self: _GD, /) -> bool:
        """True only if a real date is wrapped"""
        return False

    def __hash__(self: _GD, /) -> int:
        """hash value"""
        return hash(f"date with ordinal {self.__ordinal}")

    def _add_days(self: _GD, delta: int | float, /):
        """Add other, respecting maybe-nondeterministic values
        (ie. -inf or inf)
        """
        # Check for infinity in either self or delta,
        # and return a matching InfinityDate if found.
        # Re-use existing objects if possible.
        for observed_item in (delta, self.__ordinal):
            for infinity_form in _INFINITY_FORMS:
                if observed_item == infinity_form:
                    if observed_item == self.__ordinal:
                        return self
                    #
                    return fromordinal(observed_item)
                #
            #
        #
        # +/- 0 corner case
        if not delta:
            return self
        #
        # Return a RealDate instance if possible
        return fromordinal(self.__ordinal + trunc(delta))

    def __add__(self: _GD, delta: int | float, /) -> _GD:
        """gd_instance1 + number capability"""
        return self._add_days(delta)

    __radd__ = __add__

    @overload
    def __sub__(self: _GD, other: int | float, /) -> _GD: ...
    @overload
    def __sub__(self: _GD, other: _GD | date, /) -> int | float: ...
    @final
    def __sub__(self: _GD, other: _GD | date | int | float, /) -> _GD | int | float:
        """subtract other, respecting possibly nondeterministic values"""
        if isinstance(other, (int, float)):
            return self._add_days(-other)
        #
        return self.__ordinal - other.toordinal()

    def __rsub__(self: _GD, other: _GD | date, /) -> int | float:
        """subtract from other, respecting possibly nondeterministic values"""
        return other.toordinal() - self.__ordinal

    def __repr__(self: _GD, /) -> str:
        """String representation of the object"""
        return f"{self.__class__.__name__}({repr(self.__ordinal)})"

    def __str__(self: _GD, /) -> str:
        """String display of the object"""
        return self.isoformat()

    def isoformat(self: _GD, /) -> str:
        """Date representation in ISO format"""
        return self.strftime(ISO_DATE_FORMAT)

    def strftime(self: _GD, fmt: str, /) -> str:
        """String representation of the date"""
        raise NotImplementedError

    def replace(self: _GD, /, year: int = 0, month: int = 0, day: int = 0) -> _GD:
        """Return a copy with year, month, and/or date replaced"""
        raise NotImplementedError

    def pretty(
        self: _GD,
        /,
        *,
        inf_common_prefix: str = "",
        inf_past_suffix: str = "",
        inf_future_suffix: str = "",
        fmt: str = ISO_DATE_FORMAT,
    ) -> str:
        """Return the date, pretty printed"""
        raise NotImplementedError

    def tonative(
        self: _GD,
        /,
        *,
        exact: bool = False,
        fmt: str = ISO_DATE_FORMAT,
    ) -> str | float | None:
        """Return the native equivalent of the date"""
        raise NotImplementedError


class InfinityDate(GenericDate):
    """Infinity Date object"""

    def __init__(self, /, *, past_bound: bool = False) -> None:
        """Store -inf or inf"""
        ordinal = -inf if past_bound else inf
        self.__is_past = past_bound
        super().__init__(ordinal)

    def __repr__(self, /) -> str:
        """String representation of the object"""
        return f"{self.__class__.__name__}(past_bound={self.toordinal() == -inf})"

    def strftime(self, fmt: str, /) -> str:
        """String representation of the date"""
        if self.__is_past:
            return INFINITE_PAST_DATE_DISPLAY
        #
        return INFINITE_FUTURE_DATE_DISPLAY

    __format__ = strftime

    def replace(self, /, year: int = 0, month: int = 0, day: int = 0):
        """Not supported in this class"""
        raise TypeError(
            f"{self.__class__.__name__} instances do not support .replace()"
        )

    def pretty(
        self,
        /,
        *,
        inf_common_prefix: str = "",
        inf_past_suffix: str = "",
        inf_future_suffix: str = "",
        # pylint:disable = unused-argument ; required by inheritance
        fmt: str = ISO_DATE_FORMAT,
    ) -> str:
        """Return the date, pretty printed"""
        if self.__is_past:
            pretty_result = f"{inf_common_prefix}{inf_past_suffix}"
        else:
            pretty_result = f"{inf_common_prefix}{inf_future_suffix}"
        #
        return pretty_result or self.isoformat()

    def tonative(
        self,
        /,
        *,
        exact: bool = False,
        fmt: str = ISO_DATE_FORMAT,
    ) -> str | float | None:
        """Return the native equivalent of the date"""
        if not exact:
            return None
        #
        return self.toordinal()


# pylint: disable=too-many-instance-attributes
class RealDate(GenericDate):
    """Real (deterministic) Date object based on date"""

    def __init__(self, year: int, month: int, day: int) -> None:
        """Create a date-like object"""
        self._wrapped_date_object = date(year, month, day)
        self.year = year
        self.month = month
        self.day = day
        super().__init__(self._wrapped_date_object.toordinal())
        self.timetuple = self._wrapped_date_object.timetuple
        self.weekday = self._wrapped_date_object.weekday
        self.isoweekday = self._wrapped_date_object.isoweekday
        self.isocalendar = self._wrapped_date_object.isocalendar
        self.ctime = self._wrapped_date_object.ctime

    def __bool__(self, /) -> bool:
        """True if a real date is wrapped"""
        return True

    def __repr__(self, /) -> str:
        """String representation of the object"""
        return f"{self.__class__.__name__}({self.year}, {self.month}, {self.day})"

    def strftime(self, fmt: str, /) -> str:
        """String representation of the date"""
        return self._wrapped_date_object.strftime(fmt or ISO_DATE_FORMAT)

    __format__ = strftime

    def replace(self, /, year: int = 0, month: int = 0, day: int = 0):
        """Return a copy with year, month, and/or date replaced"""
        internal_object = self._wrapped_date_object
        return from_datetime_object(
            internal_object.replace(
                year=year or internal_object.year,
                month=month or internal_object.month,
                day=day or internal_object.day,
            )
        )

    def pretty(
        self,
        /,
        *,
        inf_common_prefix: str = "",
        inf_past_suffix: str = "",
        inf_future_suffix: str = "",
        fmt: str = ISO_DATE_FORMAT,
    ) -> str:
        """Return the date, pretty printed"""
        return self.strftime(fmt)

    def tonative(
        self,
        /,
        *,
        exact: bool = False,
        fmt: str = ISO_DATE_FORMAT,
    ) -> str | float | None:
        """Return the native equivalent of the date"""
        return self.strftime(fmt)


# -----------------------------------------------------------------------------
# Private module functions
# -----------------------------------------------------------------------------


def _from_datetime_object(source: date | datetime, /) -> GenericDate:
    """Create a new RealDate instance from a
    date or datetime object (module-private function)
    """
    return RealDate(source.year, source.month, source.day)


# -----------------------------------------------------------------------------
# Public module constants continued:
# minimum and maximum dates and ordinals, resolution (one day)
# -----------------------------------------------------------------------------


INFINITE_PAST: Final[GenericDate] = InfinityDate(past_bound=True)
INFINITE_FUTURE: Final[GenericDate] = InfinityDate(past_bound=False)

MIN: Final[GenericDate] = INFINITE_PAST
MAX: Final[GenericDate] = INFINITE_FUTURE

REAL_MIN: Final[GenericDate] = _from_datetime_object(date.min)
REAL_MAX: Final[GenericDate] = _from_datetime_object(date.max)

MIN_ORDINAL: Final[int] = date.min.toordinal()
MAX_ORDINAL: Final[int] = date.max.toordinal()

RESOLUTION: Final[int] = 1


# -----------------------------------------------------------------------------
# Public module-level factory functions
# -----------------------------------------------------------------------------


def fromdatetime(source: date | datetime, /) -> GenericDate:
    """Create a new RealDate instance from a
    date or datetime object
    """
    return _from_datetime_object(source)


def from_datetime_object(source: date | datetime, /) -> GenericDate:
    """Create a new RealDate instance from a
    date or datetime object (deprecated function name)
    """
    warnings.warn(
        "outdated function name, please use fromdatetime() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return fromdatetime(source)


def fromnative(
    source: Any,
    /,
    *,
    fmt: str = ISO_DATETIME_FORMAT_UTC,
    past_bound: bool = False,
) -> GenericDate:
    """Create an InfinityDate or RealDate instance from string or another type,
    assuming infinity in the latter case
    """
    if isinstance(source, str):
        return _from_datetime_object(datetime.strptime(source, fmt))
    #
    if source == -inf or source is None and past_bound:
        return MIN
    #
    if source == inf or source is None and not past_bound:
        return MAX
    #
    raise ValueError(f"Don’t know how to convert {source!r} into a date")


def from_native_type(
    source: Any,
    /,
    *,
    fmt: str = ISO_DATETIME_FORMAT_UTC,
    past_bound: bool = False,
) -> GenericDate:
    """Create an InfinityDate or RealDate instance from string or another type,
    assuming infinity in the latter case (deprecated function name)
    """
    warnings.warn(
        "outdated function name, please use fromnative() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return fromnative(source, fmt=fmt, past_bound=past_bound)


def fromtimestamp(timestamp: float) -> GenericDate:
    """Create an InfinityDate or RealDate instance from the provided timestamp"""
    if timestamp in _INFINITY_FORMS:
        return INFINITE_PAST if timestamp == -inf else INFINITE_FUTURE
    #
    stdlib_date_object = date.fromtimestamp(timestamp)
    return _from_datetime_object(stdlib_date_object)


def fromordinal(ordinal: int | float) -> GenericDate:
    """Create an InfinityDate or RealDate instance from the provided ordinal"""
    if ordinal in _INFINITY_FORMS:
        return INFINITE_PAST if ordinal == -inf else INFINITE_FUTURE
    #
    new_ordinal = trunc(ordinal)
    if not MIN_ORDINAL <= new_ordinal <= MAX_ORDINAL:
        raise OverflowError("RealDate value out of range")
    #
    stdlib_date_object = date.fromordinal(new_ordinal)
    return _from_datetime_object(stdlib_date_object)


def fromisoformat(source: str, /) -> GenericDate:
    """Create an InfinityDate or RealDate instance from an iso format representation"""
    lower_source_stripped = source.strip().lower()
    if lower_source_stripped == INFINITE_FUTURE_DATE_DISPLAY:
        return INFINITE_FUTURE
    #
    if lower_source_stripped == INFINITE_PAST_DATE_DISPLAY:
        return INFINITE_PAST
    #
    return _from_datetime_object(date.fromisoformat(source))


def fromisocalendar(year: int, week: int, weekday: int) -> GenericDate:
    """Create a RealDate instance from an iso calendar date"""
    return _from_datetime_object(date.fromisocalendar(year, week, weekday))


def today() -> GenericDate:
    """Today as RealDate object"""
    return _from_datetime_object(date.today())
