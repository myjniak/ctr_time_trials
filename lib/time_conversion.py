import re
from datetime import timedelta


class TimeConversion:

    @staticmethod
    def str_to_float(time_record, value_on_error=300):
        pattern = re.compile("(\d+)\D+(\d+)\D+(\d+)")
        regex_match = pattern.match(time_record)
        if regex_match is None:
            return value_on_error
        else:
            minutes, seconds, miliseconds = regex_match.groups()
            minutes = str(int(minutes))
            return minutes + ":" + seconds + "." + miliseconds

    @staticmethod
    def float_to_str(time_in_seconds):
        hh_mm_ss_msmsms = str(timedelta(seconds=time_in_seconds))[:-3]
        for i, char in enumerate(hh_mm_ss_msmsms):
            if char == "0" or char == ":":
                continue
            else:
                return hh_mm_ss_msmsms[i:]
