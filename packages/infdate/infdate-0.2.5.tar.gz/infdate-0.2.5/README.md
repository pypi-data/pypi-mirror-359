# infdate

_Python module for date calculations implementing a concept of infinity_

## Module description

### Classes overview

    └── GenericDate
        ├── InfinityDate
        └── RealDate


The base class **GenericDate** should not be instantiated
but can be used as a type annotation. In fact, it should be preferred
over the other classes for that purpose.

**InfinityDate** can represent either past or future infinity.
The module-level constants **INFINITE_PAST** and **INFINITE_FUTURE**
contain the two possible **InfinityDate** instance variations.

**RealDate** instances represent real dates like the standard library’s
**[datetime.date]** class, with mostly equal or similar semantics.
The module -level constants **REAL_MIN** and **REAL_MAX** are the eqivalents
of **datetime.date.min** and **datetime.date.max** as **RealDate** instances.

For any **RealDate** instance, the following is **True**:

``` python
infdate.INFINITE_PAST < infdate.REAL_MIN <= real_date_instance <= infdate.REAL_MAX < infdate.INFINITE_FUTURE
```

### Module-level constants

*   **INFINITE_PAST** = **InfinityDate(**_past_bound_=`True`**)** → infinity before any date
*   **INFINITE_FUTURE** = **InfinityDate(**_past_bound_=`False`**)** → infinity after any date
*   **MIN** = **INFINITE_PAST**
*   **MAX** = **INFINITE_FUTURE**
*   **REAL_MIN** = **RealDate(**`1`, `1`, `1`**)** → the same date as **datetime.date.min**
*   **REAL_MAX** = **RealDate(**`9999`, `12`, `31`**)** → the same date as **datetime.date.max**
*   **MIN_ORDINAL** = `1` → the same value as **datetime.date.min.toordinal()**
*   **MAX_ORDINAL** = `3652059` → the same value as **datetime.date.max.toordinal()**
*   **RESOLUTION** = `1` → represents the lowest possible date difference: _one day_


### Module-level factory functions

The following factory methods from the **datetime.date** class
are provided as module-level functions:

*   **fromtimestamp()** (also accepting **-math.inf** or **math.inf**)
*   **fromordinal()** (also accepting **-math.inf** or **math.inf**)
*   **fromisoformat()**
*   **fromisocalendar()**
*   **today()**

Two additional factory functions are provided:

*   **fromdatetime()** to create a **RealDate** instance from a
    **datetime.date** or **datetime.datetime** instance
    (deprecated old name: _from_datetime_object()_).

*   **fromnative()** to create an **InfinityDate** or **RealDate**
    instance from a string, from **None**, **-math.inf** or **math.inf**
    (deprecated old name: _from_native_type()_).

    This can come handy when dealing with API representations of dates,
    eg. in GitLab’s [Personal Access Tokens API].


### Differences between the infdate module classes and datetime.date

Some notable difference from the **datetime.date** class, mainly due to the design decision to express date differences in pure numbers (ie. **float** because **math.inf** also is a float):

*   infdate module classes have no **max**, **min** or **resolution** attributes,
    but there are [module-level constants] serving the same purpose.

*   The **.toordinal()** method returns **int**, **math.inf**, or **-math.inf**.

*   Subtracting a date from an **InfinityDate** or **RealDate** always returns
    an **int**, **math.inf**, or **-math.inf** instead of a **datetime.timedelta** instance.

*   Likewise, you cannot add or subtract **datetime.timedelta** instances
    from an **InfinityDate** or **RealDate**, only **float** or **int**
    (support for adding and subtracting datetime.timedelta instances might be added in the future, [see the feature request]).


### Additional methods

*   **.pretty()** can be used to format **RealDate** instances with a format string like **.strftime()** (provided with the _fmt_ argument that defaults to the ISO format `%Y-%m-%d`),
    or to apply a custom format to **InfinityDate** classes using the _inf_common_prefix_, _inf_past_suffix_, and _inf_future_suffix_ arguments.

*   **.tonative()** is the inverse function of   the **fromnative()** constructor, returning a value tha can be used e.g. as a value for an API.

    For **InfinityDate** instances, it returns the **.toordinal()** result if the _exact_ argument is set `True`, or `None` if it is left at the default (`False`).
 
    For **RealDate** instances, this method works the same way as **.pretty()**, using the _fmt_ argument with the same default as above.


## Example usage

``` pycon
>>> import infdate
>>> today = infdate.today()
>>> today
RealDate(2025, 6, 30)
>>> print(f"US date notation: {today:%m/%d/%y}")
US date notation: 06/30/25
>>> today.ctime()
'Mon Jun 30 00:00:00 2025'
>>> today.isocalendar()
datetime.IsoCalendarDate(year=2025, week=27, weekday=1)
>>> yesterday = today - 1
>>> yesterday.ctime()
'Sun Jun 29 00:00:00 2025'
>>> today - yesterday
1
>>> infdate.INFINITE_PAST
InfinityDate(past_bound=True)
>>> infdate.INFINITE_FUTURE
InfinityDate(past_bound=False)
>>> infdate.INFINITE_FUTURE - today
inf
>>> infdate.INFINITE_FUTURE - infdate.INFINITE_PAST
inf
```

**InfinityDate** and **RealDate** instances can be compared with each other, and also with **datetime.date** instances.

Subtracting **InfinityDate** or **RealDate** and **datetime.date** instances from each other also works:

``` pycon
>>> from datetime import date
>>> stdlib_today = date.today()
>>> stdlib_today
datetime.date(2025, 6, 30)
>>> today == stdlib_today
True
>>> yesterday < stdlib_today
True
>>> yesterday - stdlib_today
-1
>>> stdlib_today - yesterday
1
>>> stdlib_today - infdate.INFINITE_PAST
inf
```


* * *
[datetime.date]: https://docs.python.org/3/library/datetime.html#date-objects
[Personal Access Tokens API]: https://docs.gitlab.com/api/personal_access_tokens/
[module-level constants]: #module-level-constants
[see the feature request]: https://gitlab.com/blackstream-x/infdate/-/issues/6
