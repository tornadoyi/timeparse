from time_func_base import *



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
        else:
            acc = accuracy(v)
            tm = vec2datetime(v)
            delta = None
            if unit == td.unit.day: delta = datetime.timedelta(days=d)
            elif unit == td.unit.hour: delta = datetime.timedelta(hours=d)
            elif unit == td.unit.minute: delta = datetime.timedelta(minutes=d)
            elif unit == td.unit.second: delta = datetime.timedelta(seconds=d)
            elif unit == td.unit.season: delta = datetime.timedelta(seconds=d*unit2unit(unit, td.unit.second))
            elif unit == td.unit.week: delta = datetime.timedelta(weeks=d)
            elif unit == td.unit.quarter: delta = datetime.timedelta(minutes=d*unit2unit(unit, td.unit.minute))
            else: assert False
            res = datetime2vec(tm + delta, acc[-1])

        return res

    v = copy.deepcopy(v)
    if type(delta) == list:
        for i in xrange(delta):
            if delta[i] == None: continue
            v = delta_unit(v, i, delta[i])
    else:
        v = delta_unit(v, unit, delta)

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
def weekday(someday, day):
    day = day - 1
    dt = vec2datetime(someday)
    delta = datetime.timedelta(days=day - dt.weekday())
    res = dt + delta
    return datetime2vec(res, td.unit.week)


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






class TimeCore(object):
    def __init__(self):
        self._timestamp = time.time()

    def refresh_timestamp(self, ts=None):
        self._timestamp = ts and ts or time.time()

    @property
    def timestamp(self): return self._timestamp

    @property
    def datetime(self): return mkdatetime(self._timestamp)

    @property
    def strfdatetime(self): return time.strftime("%Y-%m-%d %H:%M:%S", self.datetime)

    def vector(self, unit=td.unit.second): return datetime2vec(self.datetime, unit)

    def weekday(self, day): return weekday(self.vector(), day)

    def unit(self, u): return get_datetime_unit(self.datetime, u)