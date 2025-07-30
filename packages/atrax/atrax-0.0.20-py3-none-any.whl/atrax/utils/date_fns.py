from datetime import datetime, timedelta
from typing import Union, List, Optional, Literal

def parse_date(val, fmt: Optional[str] = None) -> datetime:
    """Parse a date string or datetime object into a datetime object."""
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        if fmt:
            return datetime.strptime(val, fmt)
        
        fallback_formats = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y"]
        for try_fmt in fallback_formats:
            try:
                return datetime.strptime(val, try_fmt)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(val)
        except ValueError:
            pass
    raise TypeError(f"Could not parse date: {val!r}. Provide a valid date string or datetime object")



def to_datetime(
    values: Union[str, datetime, List[Union[str, datetime]]],
    fmt: Optional[str] = None,
    errors: str = "raise"  # or 'coerce'
) -> Union[datetime, List[Optional[datetime]]]:
    """
    Convert a string, datetime, or list of them to datetime objects.

    Parameters:
        values (str | datetime | list): Input date(s) to convert.
        fmt (str, optional): Optional format string to use for parsing.
        errors (str): If 'raise', invalid parsing raises an error.
                      If 'coerce', invalid parsing returns None.

    Returns:
        datetime | list[datetime | None]: Parsed datetime(s).

    Examples:
        >>> to_datetime("2023-10-01")
        datetime.datetime(2023, 10, 1)

        >>> to_datetime(["2023-10-01", "2023/10/02"])
        [datetime.datetime(2023, 10, 1), datetime.datetime(2023, 10, 2)]

        >>> to_datetime("01-10-2023", fmt="%d-%m-%Y")
        datetime.datetime(2023, 10, 1)
    """
    
    fallback_formats = ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y")

    def parse_single(val) -> Optional[datetime]:
        if val in (None, "", "NaT"):
            return None if errors == "coerce" else _raise(val)
        try:
            return parse_date(val, fmt=fmt)
        except Exception:
            return None if errors == "coerce" else _raise(val)

    def _raise(val):
        raise ValueError(f"Cannot parse date: {val}")

    # Series support
    from atrax.Series.series import Series
    if isinstance(values, Series):
        try:
            values = list(values)  # if iterable
        except TypeError:
            values = values.data  # fallback if needed

    if values is None:
        if errors == 'coerce':
            return None
        else:
            raise TypeError("Cannot parse None value without errors='coerce'")
        
    # Single value
    if isinstance(values, (str, datetime)):
        return parse_single(values)

    # List of values
    elif isinstance(values, list):
        return [parse_single(v) for v in values]

    else:
        raise TypeError(f"Unsupported input type: {type(values)}")
    
def date_range(
    start: Union[str, datetime],
    end: Optional[Union[str, datetime]] = None,
    periods: Optional[int] = None,
    freq: Literal['D', 'H', 'T', 'min', 'S'] = 'D',
    fmt: Optional[str] = None
) -> list[datetime]:
    """Generate a list of datetime values."""
    start_dt = parse_date(start, fmt)

    delta_map = {
        'D': timedelta(days=1),
        'H': timedelta(hours=1),
        'T': timedelta(minutes=1),
        'min': timedelta(minutes=1),
        'S': timedelta(seconds=1)
    }

    if freq not in delta_map:
        raise ValueError(f"Unsupported frequency: {freq}. Supported: {list(delta_map.keys())}")

    delta = delta_map[freq]

    if end is not None:
        end_dt = parse_date(end, fmt)
        if start_dt > end_dt:
            raise ValueError("'start' must be before 'end'.")
        result = []
        current = start_dt
        while current <= end_dt:
            result.append(current)
            current += delta
        return result

    if periods is not None:
        if periods <= 0:
            raise ValueError("'periods' must be a positive integer.")
        return [start_dt + i * delta for i in range(periods)]

    raise ValueError("Either 'end' or 'periods' must be specified.")
