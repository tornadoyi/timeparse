import time
import datetime
import copy
import math
from calendar import monthrange
import time_define as td
import LunarSolarConverter as converter


def time_vector(year=None, month=None, day=None, hour=None, minute=None, second=None):
    return [year, month, day, hour, minute, second]


def accuracy(v):
    st = ed = None
    for i in xrange(len(v)):
        if v[i] == None: continue
        st = i
        break
    for i in xrange(len(v)-1, st, -1):
        if v[i] == None: continue
        ed = i
        break
    return (st, ed)


def time_keep(v, start, end):
    nv = time_vector()
    for i in xrange(start, end + 1, 1): nv[i] = v[i]
    return nv

def mkdatetime(ts): return datetime.datetime.fromtimestamp(ts)


def vec2timestamp(v): return time.mktime(vec2datetime(v).timetuple())


def get_datetime_unit(dt, unit):
    tm = dt.timetuple()
    if unit == td.unit.year: return tm.tm_year
    elif unit == td.unit.month: return tm.tm_mon
    elif unit == td.unit.day: return tm.tm_mday
    elif unit == td.unit.hour: return tm.tm_hour
    elif unit == td.unit.minute: return tm.tm_min
    elif unit == td.unit.second: return tm.tm_sec
    elif unit == td.unit.week: return tm.tm_wday + 1
    elif unit == td.unit.quarter: return float(tm.tm_min) / 15.0
    else: assert False


def datetime2vec(dt, unit = td.unit.second):
    unit = int(math.ceil(unit))
    tm = dt.timetuple()
    v = [tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec]
    return time_keep(v, 0, unit)


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


# get weekday in week some day is belong to
def weekday(someday, day):
    day = day - 1
    dt = vec2datetime(someday)
    delta = datetime.timedelta(days=day - dt.weekday())
    res = dt + delta
    return datetime2vec(res, td.unit.week)


def delta_time(v, unit, d):
    res = None
    if unit == td.unit.year:
        res = copy.deepcopy(v)
        res[unit] += d
    elif unit == td.unit.month:
        res = copy.deepcopy(v)
        sum = res[td.unit.month] + d
        m = sum % 12
        res[td.unit.month] = m == 0 and 12 or m
        dy = int(sum / 13.0)
        dy = sum <= 0 and dy - 1 or dy
        res[td.unit.year] += dy
    else:
        acc = accuracy(v)
        tm = vec2datetime(v)
        delta = None
        if unit == td.unit.day: delta = datetime.timedelta(days=d)
        elif unit == td.unit.hour: delta = datetime.timedelta(hours=d)
        elif unit == td.unit.minute: delta = datetime.timedelta(minutes=d)
        elif unit == td.unit.second: delta = datetime.timedelta(seconds=d)
        elif unit == td.unit.week: delta = datetime.timedelta(weeks=d)
        elif unit == td.unit.quarter: delta = datetime.timedelta(minutes=d*15)
        else: assert False
        res = datetime2vec(tm + delta, acc[-1])

    return res



def shift_time(v, shift):
    for i in xrange(shift):
        if shift[i] == None: continue
        v = delta_time(v, i, shift[i])
    return v



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



def days_of_month(year, month):
    range = monthrange(year, month)
    return range[1]


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


def unit_range_at_time(v, unit):
    (min, max) = unit_range(unit)
    if unit == td.unit.day: max = days_of_month(v[0], v[1])
    return (min, max)








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

def timevec_format_dict(v):
    d = {}
    if v[0] != None: d['year'] = v[0]
    if v[1] != None: d['month'] = v[1]
    if v[2] != None: d['day'] = v[2]
    if v[3] != None: d['hour'] = v[3]
    if v[4] != None: d['minute'] = v[4]
    if v[5] != None: d['second'] = v[5]
    return d





class TimeCore(object):
    def __init__(self):
        self._timestamp = time.time()

    def refresh_timestamp(self, ts = None):
        self._timestamp = ts and ts or time.time()

    @property
    def timestamp(self): return self._timestamp
    
    @property
    def datetime(self): return mkdatetime(self._timestamp)

    @property
    def strfdatetime(self): return time.strftime("%Y-%m-%d %H:%M:%S", self.datetime)


    def vector(self, unit = td.unit.second): return datetime2vec(self.datetime, unit)

    def weekday(self, day): return weekday(self.vector(), day)

    def unit(self, u): return get_datetime_unit(self.datetime, u)

