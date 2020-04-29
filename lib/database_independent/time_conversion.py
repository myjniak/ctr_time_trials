import re


class TimeConversion:

    def __init__(self, time_record, value_on_error=300, decimals=3):
        self.value_on_error = value_on_error
        self.decimals = decimals
        if isinstance(time_record, int) or isinstance(time_record, float):
            self.number_as_float = float(time_record)
            self.number_as_str = self.float_to_str(time_record)
        else:
            self.number_as_float = self.str_to_float(time_record)
            self.number_as_str = self.float_to_str(self.as_float)

    @property
    def as_float(self):
        return self.number_as_float

    @property
    def as_str(self):
        return self.number_as_str

    @staticmethod
    def str_to_float(time_record, value_on_error=300):
        pattern = re.compile("(\d+)\D+(\d+)\D+(\d+)")
        regex_match = pattern.match(time_record)
        if regex_match is None:
            return value_on_error
        else:
            minutes, seconds, miliseconds = regex_match.groups()
            return 60*float(minutes) + float(seconds) + round(float(miliseconds)/10**len(miliseconds), 3)

    @staticmethod
    def float_to_str(time_in_seconds, decimals=3):
        minutes = int(time_in_seconds/60)
        seconds = int(time_in_seconds) - minutes*60
        seconds_as_str = ('0' if seconds <= 9 else '') + str(seconds)
        miliseconds = int(time_in_seconds*1000) - (minutes*60 + seconds)*1000
        ms_len = len(str(miliseconds))
        zeros_to_add = decimals - ms_len
        miliseconds_as_str = zeros_to_add*'0' + str(miliseconds)
        return str(minutes) + ":" + seconds_as_str + "." + miliseconds_as_str
