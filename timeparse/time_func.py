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
    if st == None: return (None, None)

    for i in xrange(len(v)-1, st, -1):
        if v[i] == None: continue
        ed = i
        break
    return (st, ed)



def mkdatetime(ts): return datetime.datetime.fromtimestamp(ts)


def vec2timestamp(v): return time.mktime(vec2datetime(v).timetuple())



def datetime2vec(dt, unit = td.unit.second):
    unit = int(math.ceil(unit))
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



def days_of_month(year, month):
    range = monthrange(year, month)
    return range[1]





