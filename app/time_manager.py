"""!
@file time_manager.py
@brief Time conversion helpers for booking scheduling.
"""

from datetime import timedelta


class TimeManager:
    """!
    @brief Helper methods for time calculations in booking flows.
    
    @note Methods are implemented as static-style functions (no `self` usage).
    """
    def __init__(self):
        pass

    def time_to_timedelta(time_str):

        """!

        @brief Convert a time string into a timedelta.

        @param time_str Time in "HH:MM:SS" format.

        @return timedelta representing the given time offset.

        """
        h, m, s = map(int, time_str.split(":"))
        return timedelta(hours=h, minutes=m, seconds=s)

    def timedelta_to_time(td):

        """!

        @brief Convert a timedelta into an "HH:MM" string (24-hour, minutes precision).

        @param td Timedelta to format.

        @return Formatted time string (HH:MM).

        """
        total_seconds = int(td.total_seconds()) % (24 * 3600)

        total_minutes = total_seconds // 60  # truncate seconds

        h = total_minutes // 60
        m = total_minutes % 60

        return f"{h:02}:{m:02}"

    def get_end_time_from_start_time_and_duration(ts, ds):


        """!

        @brief Compute an end time from a start time and duration.

        @param ts Start time string in "HH:MM:SS".

        @param ds Duration string in "HH:MM:SS".

        @return timedelta representing the end time (start + duration).

        """
        start_td = TimeManager.time_to_timedelta(ts)
        duration_td = TimeManager.time_to_timedelta(ds)

        end_td = start_td + duration_td
        return end_td

    def get_duration_from_start_time_and_end_time(start_time_str, end_time_str):


        """!

        @brief Compute a duration from start and end times.

        @param start_time_str Start time string in "HH:MM:SS".

        @param end_time_str End time string in "HH:MM:SS".

        @return Duration string in "HH:MM:SS".

        """
        start_td = TimeManager.time_to_timedelta(start_time_str)
        end_td = TimeManager.time_to_timedelta(end_time_str)

        duration_td = end_td - start_td
        duration_td = TimeManager.timedelta_to_time(duration_td) + ":00"
        return duration_td
