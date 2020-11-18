from datetime import timedelta
import re


class Time:

    def __init__(self, time_record, value_on_error="5:00.00", decimals=2):
        self.decimals = decimals
        self.value_on_error = value_on_error
        if isinstance(time_record, str):
            self.time_record = self.timedelta(time_record)
        elif isinstance(time_record, timedelta):
            self.time_record = time_record
        else:
            raise TypeError("Time class supports str or timedelta only")

    def timedelta(self, time_record):
        pattern = re.compile("(\d+)\D+(\d+)\D+(\d+)")
        regex_match = pattern.match(time_record)
        if regex_match is None:
            regex_match = pattern.match(self.value_on_error)
        minutes, seconds, decimals = regex_match.groups()
        zeros_to_add = 6 - len(decimals)
        decimals += zeros_to_add * "0"
        return timedelta(minutes=int(minutes), seconds=int(seconds), microseconds=int(decimals))

    def __str__(self):
        # minute times only
        h, m, s_ms = str(self.time_record).rsplit(":")
        m = str(int(m) + 60*int(h))
        if "." not in s_ms:
            decimals = self.decimals*"0"
            s_dec = ".".join([s_ms, decimals])
        else:
            s, ms = s_ms.split(".")
            decimals = ms[:self.decimals]
            s_dec = ".".join([s, decimals])
        time_as_str = ":".join([m, s_dec])
        return time_as_str

    def __float__(self):
        return self.time_record.total_seconds()

    def __add__(self, other):
        return Time(self.time_record + other.time_record,
                    value_on_error=self.value_on_error,
                    decimals=self.decimals)
