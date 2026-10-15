import sys
import eda_state as estate

if 'micropython' in sys.implementation.name.lower():
    global utime
    import utime
else:
    from datetime import datetime


def get_timestamp_from_nanoseconds(ts):
    try:
        nanoseconds = int(ts) if isinstance(ts, str) else ts
        seconds = nanoseconds // 1_000_000_000  # Use float division
        if 'micropython' in sys.implementation.name.lower():  # pragma: no cover
            microseconds = (nanoseconds % 1_000_000_000) // 1000
            year, month, day, hour, minute, sec, _, _, _ = utime.localtime(seconds)
            timestamp = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{sec:02d}.{microseconds:03d}Z"
            return timestamp
        else:
            dt_object = datetime.fromtimestamp(seconds)
            return dt_object.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    except ValueError:
        raise ValueError(f"invalid value '{ts}' for time in nanoseconds")


def get_timestamp_from_seconds(ts):
    try:
        seconds = int(ts) if isinstance(ts, str) else ts
        if 'micropython' in sys.implementation.name.lower():  # pragma: no cover
            microseconds = 0
            year, month, day, hour, minute, sec, _, _, _ = utime.localtime(seconds)
            timestamp = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{sec:02d}.{microseconds:03d}Z"
            return timestamp
        else:
            dt_object = datetime.fromtimestamp(seconds)
            return dt_object.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    except ValueError:
        raise ValueError(f"invalid value '{ts}' for time in seconds")


def get_timestamp_from_mmddyyyy(ts):  # pragma: no cover
    """
    Standardizes a mmddyyyy timestamp string to have three digits of millisecond accuracy.
    Compatible with both Python and MicroPython.

    :param ts: A timestamp string in the format mmddyyyy.
    :return: The standardized timestamp string.
    """

    def parse_timestamp_python(ts):
        return datetime.strptime(ts, "%m%d%Y")

    def parse_timestamp_micropython(ts):  # pragma: no cover
        # Custom parsing for MicroPython
        if len(ts) != 8 or not ts.isdigit():
            raise ValueError(f"Invalid date format. Expected 'mmddyyyy'. Current value is '{ts}'")
        month = int(ts[0:2])
        day = int(ts[2:4])
        year = int(ts[4:8])
        hour = 0
        minute = 0
        second = 0
        microsecond = 0
        return utime.mktime((year, month, day, hour, minute, second, 0, 0)) + microsecond / 1e6

    if 'micropython' in sys.implementation.name.lower():  # pragma: no cover
        parsed_timestamp = parse_timestamp_micropython(ts)
        # Manually format the timestamp in MicroPython
        year, month, day, hour, minute, second, _, _, _ = utime.localtime(parsed_timestamp)
        ms = int(round((parsed_timestamp % 1) * 1000))
        return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{ms:03d}Z"
    else:
        parsed_timestamp = parse_timestamp_python(ts)
        return parsed_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def get_normalized_timestamp(ts):
    """
    Standardizes a timestamp string to have three digits of millisecond accuracy.
    Compatible with both Python and MicroPython.

    :param ts: A timestamp string.
    :return: The standardized timestamp string.
    """

    def parse_timestamp_python(ts):
        try:
            # from datetime import datetime
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:  # pragma: no cover
            try:
                return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                # remove the colon in the timezone offset
                ts_formatted = ts[:-3] + ts[-2:]
                try:
                    return datetime.strptime(ts_formatted, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    return datetime.strptime(ts_formatted, "%Y-%m-%dT%H:%M:%S.%f%z")

    def parse_timestamp_micropython(ts):  # pragma: no cover
        # Custom parsing for MicroPython
        parts = ts.split('T')
        date_parts = parts[0].split('-')
        time_parts = parts[1].split(':')
        seconds_parts = time_parts[2].split('.')
        year, month, day = map(int, date_parts)
        hour, minute = map(int, time_parts[:2])
        second = int(seconds_parts[0])
        microsecond = int(round(float('0.' + seconds_parts[1].rstrip('Z')) * 1e6, 3)) if '.' in time_parts[2] else 0
        return utime.mktime((year, month, day, hour, minute, second, 0, 0)) + microsecond / 1e6

    if 'micropython' in sys.implementation.name.lower():  # pragma: no cover
        parsed_timestamp = parse_timestamp_micropython(ts)
        # Manually format the timestamp in MicroPython
        year, month, day, hour, minute, second, _, _, _ = utime.localtime(parsed_timestamp)
        ms = int(round((parsed_timestamp % 1) * 1000))
        return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{ms:03d}Z"
    else:
        parsed_timestamp = parse_timestamp_python(ts)
        return parsed_timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def most_recent_timestamp(timestamps):
    """
    Returns the most recent timestamp from a list of timestamp strings.
    Timestamps can have varying millisecond granularities.
    Compatible with both Python and MicroPython.

    :param timestamps: List of timestamp strings.
    :return: The most recent timestamp string with three digits of millisecond accuracy.
    """
    if timestamps is None or len(timestamps) == 0:
        return None
    parsed_timestamps = [get_normalized_timestamp(ts) for ts in timestamps]
    most_recent = max(parsed_timestamps)
    return most_recent


def calculate_last_change(cr_name: str, curr_oper_state: str):
    key = f'last-state={cr_name}'
    prev_dict = estate.get_scratchpad_data(key=key)
    if prev_dict is None:
        prev_oper_state = None
    else:
        prev_oper_state = prev_dict['oper-state']
        prev_last_change = prev_dict['last_change']
    curr_time = get_current_timestamp()
    if prev_oper_state != curr_oper_state:
        last_change = get_normalized_timestamp(curr_time)
    else:
        last_change = prev_last_change
    curr_dict = {}
    curr_dict['oper-state'] = curr_oper_state
    curr_dict['last_change'] = last_change
    estate.set_scratchpad_data(key=key, data=curr_dict)
    return last_change


def get_current_timestamp():
    if 'micropython' in sys.implementation.name.lower():
        local_time_tuple = utime.localtime()
        year = local_time_tuple[0]
        month = local_time_tuple[1]
        day = local_time_tuple[2]
        hour = local_time_tuple[3]
        minute = local_time_tuple[4]
        second = local_time_tuple[5]
        ms = 0
        curr_time = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{ms:03d}Z"
    else:
        curr_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    return get_normalized_timestamp(curr_time)
