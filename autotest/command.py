from pyplus import *

from timeparse import time_define as td
from timeparse import time_func_ext as tf
from timeparse import time_struct as ts

timecore = tf.TimeCore()
args = qdict(timecore = timecore, infinity=[0, 0, 0, 0, 0, 0], fulltime=False, padding="recent")

year = td.unit.year
month = td.unit.month
day = td.unit.day
hour = td.unit.hour
minute = td.unit.minute
second = td.unit.second

def excute(cmds, args = None):
    args = args if args != None else qdict(curvector=tf.time_vector())
    vector = tf.time_vector()
    unit = 0
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

class cmd(object):
    def get_value(self, v, args):
        if isinstance(v, cmd):
            return v(args)
        elif type(v) == list:
            return excute(v, args)
        else:
            return copy.deepcopy(v)



## ======================================== shift command ======================================== ##


class sft(cmd):
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __call__(self, args):
        value = self.get_value(self.value, args)
        vector = tf.delta_time(timecore.vector, self.unit, value)
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


class s_weekday(cmd):
    def __init__(self, value, shift):
        self.value = value
        self.shift = shift

    def __call__(self, args):
        value = self.get_value(self.value, args)
        shift = self.get_value(self.shift, args)
        vector = tf.weekday_vector(timecore.vector, value)
        vector = tf.delta_time(vector, td.unit.week, shift)
        return tf.keep_vector(vector, td.unit.day)


class s_week(cmd):
    def __init__(self, value, weekday):
        self.value = value
        self.weekday = weekday

    def __call__(self, args):
        value = self.get_value(self.value, args)
        weekday = self.get_value(self.weekday, args)
        vector = tf.weekday_vector(timecore.vector, weekday)
        vector = tf.delta_time(vector, td.unit.week, value)
        return tf.keep_vector(vector, td.unit.day)


class s_week_st(s_week):
    def __init__(self, value):
        s_week.__init__(self, value, 1)


class s_week_ed(s_week):
    def __init__(self, value):
        s_week.__init__(self, value, 7)


class s_season(cmd):
    def __init__(self, value, end):
        self.value = value
        self.end = end

    def __call__(self, args):
        value = self.get_value(self.value, args)
        year = timecore.unit(td.unit.year)
        se = timecore.unit(td.unit.season)
        st_m = 1 + (se-1) * 3
        ed_m = st_m + 2
        month = ed_m if self.end else st_m
        return tf.delta_time(tf.time_vector(year=year, month=month), td.unit.season, value)


class s_season_st(s_season):
    def __init__(self, value):
        s_season.__init__(self, value, False)

class s_season_ed(s_season):
    def __init__(self, value):
        s_season.__init__(self, value, True)




## ======================================== number command ======================================== ##

class number(cmd):
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __call__(self, args):
        (min, max) = tf.unit_range_at_time(args.curvector, self.unit)
        value = self.get_value(self.value, args)
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



## ======================================== delta command ======================================== ##

class d_time(cmd):
    def __init__(self, vector, unit, value):
        self.vector = vector
        self.unit = unit
        self.value = value

    def __call__(self, args):
        value = self.get_value(self.value, args)
        vector = self.get_value(self.vector, args)
        return tf.delta_time(vector, self.unit, self.value)


class delta(cmd):
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __call__(self, args):
        value = self.get_value(self.value, args)
        return tf.delta_time(timecore.vector, self.unit, self.value)

class d_year(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.year, value)

class d_month(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.month, value)

class d_day(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.day, value)

class d_hour(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.hour, value)

class d_minute(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.minute, value)

class d_second(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.second, value)

class d_week(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.week, value)

class d_season(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.season, value)

class d_quarter(delta):
    def __init__(self, value):
        delta.__init__(self, td.unit.quarter, value)





## ======================================== time command ======================================== ##



class create_time(cmd):
    def __init__(self, start, end, duration):
        self.start = start
        self.end = end
        self.duration = duration

    def __call__(self, args):
        start = excute(self.start)
        end = excute(self.end)
        duration = excute(self.duration)

        return ts.VectorTime("", (0, 0), start, end, duration)


class s_time(create_time):
    def __init__(self, start):
        create_time.__init__(self, start, start, [])

class se_time(create_time):
    def __init__(self, start, end):
        create_time.__init__(self, start, end, [])

class sd_time(create_time):
    def __init__(self, start, duration):
        create_time.__init__(self, start, [], duration)




## ======================================== other command ======================================== ##
vector = tf.time_vector

class l2s(cmd):
    def __init__(self, vector):
        self.vector = vector

    def __call__(self, args):
        vector = self.get_value(self.vector, args)
        (y, m, d) = tf.lunar2solar(vector[0], vector[1], vector[2])
        vector[0] = y
        vector[1] = m
        vector[2] = d
        return vector

class s2l(cmd):
    def __init__(self, vector):
        self.vector = vector

    def __call__(self, args):
        vector = self.get_value(self.vector, args)
        (y, m, d) = tf.solar2lunar(vector[0], vector[1], vector[2])
        vector[0] = y
        vector[1] = m
        vector[2] = d
        return vector



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