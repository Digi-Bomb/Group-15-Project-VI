from datetime import timedelta


class TimeManager:
    def __init__(self):
        pass

    def time_to_timedelta(time_str):
        h, m, s = map(int, time_str.split(":"))
        return timedelta(hours=h, minutes=m, seconds=s)

    def timedelta_to_time(td):
        total_seconds = int(td.total_seconds()) % (24 * 3600)

        total_minutes = total_seconds // 60  # truncate seconds

        h = total_minutes // 60
        m = total_minutes % 60

        return f"{h:02}:{m:02}"

    def get_end_time_from_start_time_and_duration(ts, ds):

        start_td = TimeManager.time_to_timedelta(ts)
        duration_td = TimeManager.time_to_timedelta(ds)

        end_td = start_td + duration_td
        return end_td
    
    def get_duration_from_start_time_and_end_time(start_time_str, end_time_str):

        start_td = TimeManager.time_to_timedelta(start_time_str)
        end_td = TimeManager.time_to_timedelta(end_time_str)

        duration_td = end_td - start_td
        duration_td = TimeManager.timedelta_to_time(duration_td) + ":00"
        return duration_td
