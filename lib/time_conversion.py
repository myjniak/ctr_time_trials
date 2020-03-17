from datetime import datetime, timedelta


class TimeConversion:

    @staticmethod
    def str_to_float(time_record, value_on_error=300):
        try:
            x = datetime.strptime(time_record, '%M:%S.%f')
        except ValueError:
            return value_on_error
        return x.minute * 60 + x.second + x.microsecond / 1000000

    @staticmethod
    def float_to_str(time_in_seconds):
        hh_mm_ss_msmsms = str(timedelta(seconds=time_in_seconds))[:-3]
        for i, char in enumerate(hh_mm_ss_msmsms):
            if char == "0" or char == ":":
                continue
            else:
                return hh_mm_ss_msmsms[i:]
