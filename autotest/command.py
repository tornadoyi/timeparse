from pyplus import *

from timeparse import time_define as td
from timeparse import time_func_ext as tf
from timeparse import time_struct as ts

timecore = tf.TimeCore()
args = qdict(timecore = timecore, infinity=7, fulltime=False, padding="recent")

year = td.unit.year
month = td.unit.month
day = td.unit.day
hour = td.unit.hour
minute = td.unit.minute
second = td.unit.second


class cmd(object):
    def get_value(self, v): return v() if isinstance(v, cmd) else v



## ======================================== shift command ======================================== ##


class sft(cmd):
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __call__(self, args):
        value = self.get_value(self.value)
        vector = tf.delta_time(timecore.vector(), self.unit, value)
        return tf.keep_vector(vector, self.unit)

class s_year(sft):
    def __init__(self, value):
        sft.__init__(self, td.unit.year, value)

class s_month(sft):
    def __init__(self, value):
        sft.__init__(self, td.unit.month, value)

class s_day(sft):
    def __init__(self, value):
        sft.__init__(self, td.unit.day, value)

class s_hour(sft):
    def __init__(self, value):
        sft.__init__(self, td.unit.hour, value)

class s_minute(sft):
    def __init__(self, value):
        sft.__init__(self, td.unit.minute, value)

class s_second(sft):
    def __init__(self, value):
        sft.__init__(self, td.unit.second, value)



## ======================================== number command ======================================== ##



class number(cmd):
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __call__(self, args):
        (min, max) = tf.unit_range_at_time(args.curvector, self.unit)
        value = self.get_value(self.value)
        return min if value == 0 else min + value - 1 if value > 0 else max + value + 1

class n_year(number):
    def __init__(self, value):
        number.__init__(self, td.unit.year, value)

class n_month(number):
    def __init__(self, value):
        number.__init__(self, td.unit.month, value)

class n_day(number):
    def __init__(self, value):
        number.__init__(self, td.unit.day, value)

class n_hour(number):
    def __init__(self, value):
        number.__init__(self, td.unit.hour, value)

class n_minute(number):
    def __init__(self, value):
        number.__init__(self, td.unit.minute, value)

class n_second(number):
    def __init__(self, value):
        number.__init__(self, td.unit.second, value)




## ======================================== time command ======================================== ##

class create_time(cmd):
    def __init__(self, start, end, duration):
        self.start = start
        self.end = end
        self.duration = duration

    def __call__(self, args):
        start = self.excute(self.start)
        end = self.excute(self.end)
        duration = self.excute(self.duration)

        return ts.VectorTime("", (0, 0), start, end, duration)

    def excute(self, cmds):
        vector = tf.time_vector()
        unit = 0
        args = qdict(curvector = vector)
        for c in cmds:
            if isinstance(c, cmd):
                vec = c(args)
                for v in vec:
                    if v == None: break
                    vector[unit] = v
                    unit += 1

            else:
                vector[unit] = c
                unit += 1
        return vector


class s_time(create_time):
    def __init__(self, start):
        create_time.__init__(self, start, start, [])

class se_time(create_time):
    def __init__(self, start, end):
        create_time.__init__(self, start, end, [])

class sd_time(create_time):
    def __init__(self, start, duration):
        create_time.__init__(self, start, [], duration)


'''
# time struct
def create_time(st = None, ed = None, dur = None):
    start = st == None and None or en.TimeVector(st)
    end = ed == None and None or en.TimeVector(ed)
    duration = dur == None and None or en.TimeVector(dur)
    return en.Time(start=start, end=end, duration=duration, sentence="", pos_span=[0, 0])

def start(v): return create_time(st=v)
def end(v): return create_time(ed=v)
def duration(v): return create_time(dur=v)
def start_end(st, ed = None): return create_time(st=st, ed=ed or st)
def start_duration(st, dur): return create_time(st=st, dur=dur)

# time core
curtime = timecore.curtime_vector
curweekday = timecore.curweekday_vector

cursecond = lambda: curtime(unit=td.unit.second)
curminute = lambda: curtime(unit=td.unit.minute)
curhour = lambda: curtime(unit=td.unit.hour)
curday = lambda: curtime(unit=td.unit.day)
curmonth = lambda: curtime(unit=td.unit.month)
curyear = lambda: curtime(unit=td.unit.year)


# base functions
time = tf.time_vector
time_keep = tf.time_keep
delta_time = tf.delta_time
delta_curtime = lambda unit, d: delta_time(curtime(), unit, d)
delta_cursecond = lambda d: delta_time(cursecond(), td.unit.second, d)
delta_curminute = lambda d: delta_time(curminute(), td.unit.minute, d)
delta_curhour = lambda d: delta_time(curhour(), td.unit.hour, d)
delta_curday = lambda d: delta_time(curday(), td.unit.day, d)
delta_curmonth = lambda d: delta_time(curmonth(), td.unit.month, d)
delta_curyear = lambda  d: delta_time(curyear(), td.unit.year, d)


lunar2solar = tf.lunar2solar
solar2lunar = tf.solar2lunar

'''