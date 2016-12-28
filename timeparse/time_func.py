import time
import datetime
import copy
import math
from calendar import monthrange
import time_define as td
import LunarSolarConverter as converter


def time_vector(year=None, month=None, day=None, hour=None, minute=None, second=None):
    return [year, month, day, hour, minute, second]

# mode: clear:set none,  cut: reshape
def keep_vector(v, unit, mode = "clear"):
    v = copy.deepcopy(v)
    if mode == "clear":
        st = int(unit + 1)
        ed = len(v)
        v[st:ed] = [None] * (ed - st)
        return v
    else:
        return v[0:int(unit+1)]


def accuracy(v):
    st = ed = None
    for i in xrange(len(v)):
        if v[i] == None: continue
        st = i
        break
    if st == None: return (None, None)

    for i in xrange(len(v)-1, st-1, -1):
        if v[i] == None: continue
        ed = i
        break
    return (st, ed)



def mkdatetime(ts): return datetime.datetime.fromtimestamp(ts)


def vec2timestamp(v): return time.mktime(vec2datetime(v).timetuple())



def datetime2vec(dt):
    tm = dt.timetuple()
    v = [tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec]
    return v


def vec2datetime(v):
    new_v = [unit_min(td.unit.year), unit_min(td.unit.month), unit_min(td.unit.day), unit_min(td.unit.hour), unit_min(td.unit.minute), unit_min(td.unit.second)]
    for i in xrange(len(v)):
        if v[i] == None: continue
        decimal = v[i] - int(v[i])
        new_v[i] = int(v[i])
        if decimal > 0 and i < td.unit.second:
            delta_v = int(unit2unit(decimal, i, i+1))
            new_v[i+1] = delta_v if new_v[i+1] == None else delta_v + new_v[i+1]
    return datetime.datetime(*new_v)



def unit2unit(v, st_unit, ed_unit):
    st_second = td.time_unit_convert[st_unit]
    ed_second = td.time_unit_convert[ed_unit]
    return float(v) * float(st_second) / float(ed_second)


def vec2second(v):
    sum = 0
    for i in xrange(td.unit.year, td.unit.second + 1, 1):
        if v[i] == None: continue
        sum += unit2unit(v[i], i, td.unit.second)
    return sum




def unit_range(unit): return td.time_unit_range[unit]

def unit_min(unit): return td.time_unit_range[unit][0]

def unit_max(unit): return td.time_unit_range[unit][1]

def unit_half(unit): return int(math.floor(td.time_unit_range[unit][1] / 2))

def lunar2solar(year, month, day): return converter.LunarToSolar(year, month, day)

def solar2lunar(year, month, day): return converter.SolarToLunar(year, month, day)

def lunar_month_days(year, month): return converter.LunarMonthDays(year, month)


def days_of_month(year, month, lunar):
    if lunar:
        return lunar_month_days(year, month)
    else:
        range = monthrange(int(year), int(month))
        return range[1]




# ============================================= advance functions ============================================= #


def get_datetime_unit(dt, unit):
    tm = dt.timetuple()
    if unit == td.unit.year: return tm.tm_year
    elif unit == td.unit.month: return tm.tm_mon
    elif unit == td.unit.day: return tm.tm_mday
    elif unit == td.unit.hour: return tm.tm_hour
    elif unit == td.unit.minute: return tm.tm_min
    elif unit == td.unit.second: return tm.tm_sec
    elif unit == td.unit.season: return tm.tm_mon / 4 + 1
    elif unit == td.unit.week: return tm.tm_wday + 1
    elif unit == td.unit.quarter: return float(tm.tm_min) / 15.0
    else: assert False




def delta_time(v, unit = None, delta = None):

    def delta_unit(v, unit, d):
        d = d or 0
        res = v
        if unit == td.unit.year:
            res[unit] += d

        elif unit == td.unit.month:
            sum = res[td.unit.month] + d
            m = sum % 12
            res[td.unit.month] = m == 0 and 12 or m
            dy = int(sum / 13.0)
            dy = sum <= 0 and dy - 1 or dy
            res[td.unit.year] += dy

        elif unit == td.unit.season:
            num_month = unit2unit(1, td.unit.season, td.unit.month)
            res = delta_unit(res, td.unit.month, num_month * d)

        else:
            tm = vec2datetime(v)
            delta = None
            if unit == td.unit.day: delta = datetime.timedelta(days=d)
            elif unit == td.unit.hour: delta = datetime.timedelta(hours=d)
            elif unit == td.unit.minute: delta = datetime.timedelta(minutes=d)
            elif unit == td.unit.second: delta = datetime.timedelta(seconds=d)
            elif unit == td.unit.week: delta = datetime.timedelta(weeks=d)
            elif unit == td.unit.quarter: delta = datetime.timedelta(minutes=d*unit2unit(unit, td.unit.minute))
            else: assert False
            res = datetime2vec(tm + delta)

        return res

    v = copy.deepcopy(v)
    acc = accuracy(v)
    if type(delta) == list:
        for i in xrange(delta):
            if delta[i] == None: continue
            v = delta_unit(v, i, delta[i])
    else:
        v = delta_unit(v, unit, delta)

    v = keep_vector(v, acc[-1])

    return v




def timevec_format(v, with_unit = False):
    format = ""
    for i in xrange(len(v)):
        if v[i] == None: continue
        if len(format) > 0:
            if i < 3: format += "-"
            elif i == 3: format += " "
            else: format += ":"

        format += str(v[i]) if i == 0 else "%02d" % (v[i])
        if with_unit: format += td.time_unit_desc[i]
    return format


# ============================================= week ============================================= #


# get weekday in week some day is belong to
def weekday_vector(someday, day):
    day = day - 1
    dt = vec2datetime(someday)
    delta = datetime.timedelta(days=day - dt.weekday())
    res = dt + delta
    return datetime2vec(res)


def start_time_at_week(year, month, delta_week):
    if delta_week >= 0:
        t = datetime.datetime(year, month, 1).timetuple()
        delta_day = (7 - t.tm_wday) + 7 * (delta_week - 1)
        return delta_time([year, month, 1], td.unit.day, delta_day)
    else:
        max_day = days_of_month(year, month)
        t = datetime.datetime(year, month, max_day).timetuple()
        delta_day = -t.tm_wday + 7 * (delta_week + 1)
        return delta_time([year, month, max_day], td.unit.day, delta_day)


def unit_range_at_time(v, unit, lunar=False):
    (min, max) = unit_range(unit)
    if unit == td.unit.day:
        max = days_of_month(v[0], v[1], lunar)
    return (min, max)




# ============================================= padding ============================================= #

def padding(v, unit, max_unit, lunar=False):
    v = copy.deepcopy(v)
    for i in xrange(len(v)):
        if v[i] != None: continue
        (min, max) = unit_range_at_time(v, i, lunar)
        v[i] = max if max_unit else min
    return v

def padding_max(v, unit = td.unit.second, lunar=False): return padding(v, unit, True, lunar)

def padding_min(v, unit = td.unit.second, lunar=False): return padding(v, unit, False, lunar)



class TimeCore(object):
    def __init__(self):
        self._timestamp = time.time()

    def refresh_timestamp(self, ts=None):
        self._timestamp = ts and ts or time.time()

    @property
    def timestamp(self): return self._timestamp

    @timestamp.setter
    def timestamp(self, ts): self._timestamp = ts

    @property
    def datetime(self): return mkdatetime(self._timestamp)

    @property
    def strfdatetime(self): return time.strftime("%Y-%m-%d %H:%M:%S", self.datetime)

    @property
    def vector(self): return datetime2vec(self.datetime)

    def unit(self, u): return get_datetime_unit(self.datetime, u)

    def padding(self, v, unit = td.unit.second):
        v = copy.deepcopy(v)
        c = self.vector
        for i in xrange(len(c)):
            if v[i] != None: continue
            v[i] = c[i]
        return v