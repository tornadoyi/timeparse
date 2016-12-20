# -*- coding: utf-8 -*-

import sys
import re
import math
import numpy as np

import time_define as td
from time_struct import *


class re_parser(object):
    def __init__(self):
        # (ex, action, parms)
        self._re = []

    def parse(self, sentence, splits, pos = None, endpos = None, args = None):
        entities = []
        for e in self.match(sentence, pos, endpos, args):
            # inert sort
            insert = False
            for i in xrange(len(entities)):
                item = entities[i]
                if e.pos_min > item.pos_min: continue
                entities.insert(i, e)
                insert = True
                break
            if not insert: entities.append(e)
        return entities

    def add_re(self, ex, action):
        ex = re.compile(ex, re.I)
        self._re.append((ex, action))

    def match(self, str, pos = None, endpos = None, args = None):
        if pos == None: pos = 0
        if endpos == None: endpos = len(str)
        for (ex, action) in self._re:
            iters = ex.finditer(str, pos, endpos)
            for it in iters:
                e = action(it, args)
                if not e: continue
                #print(action.im_class); print(e)
                yield e

    def parse_match(self, m): return m.string, m.start(), m.end()



class time_re(re_parser):

    def parse_digits(self, str, ex_dict = None):
        if str == None or len(str) == 0: return None
        sum = 0
        digit = 0
        min_unit = 0

        for s in str:
            d = td.property(s, td.wordtype.digit)
            if d == None:
                if ex_dict == None: break
                d = ex_dict.get(s, None)
                if d == None: break

            if (0 < d and d < 10) or \
                    (d == 0 and digit != 0):
                digit = digit * 10 + d
            else:
                if d == 0:
                    min_unit = 10
                else:
                    min_unit = d
                    sum += digit == 0 and d or digit * d
                    digit = 0

        if digit > 0:
            sum += min_unit == 0 and digit or digit * (min_unit / 10)

        return sum

    def parse_degree(self, s):
        if s == None or len(s) == 0: return None
        degree = 0
        for k in s:
            d = td.property(k, td.wordtype.degree)
            if d == None:
                print(u"can not find property for {0}".format(k))
                continue
            degree += d
        return degree

    def parse_direct(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.direct)


    def parse_special_hour(self, s): return None if s == None or len(s) == 0 else  td.property(s, td.wordtype.special_hour)

    def parse_relation(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.relation)

    def parse_unit(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.unit)

    def parse_quantity(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.quantity)

    def parse_calendar(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.calendar)

    def parse_holiday(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.holiday)

    def parse_season(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.season)

    def parse_lunar_month(self, s): return None if s == None or len(s) == 0 else td.property(s, td.wordtype.lunar_month)


# 8 / 3个半
class digit_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0})+)([{1}]?)([{2}]?)".format(
            td.split_texts(td.wordtype.digit),
            td.split_texts(td.wordtype.quantity),
            td.split_texts(td.wordtype.digit, 0.5))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        digit = self.parse_digits(m.group(1))
        quantity = self.parse_quantity(m.group(2)) != None
        half = self.parse_digits(m.group(3)) or 0

        value = digit + half
        return Digit(str, (st, ed), value, quantity)




# 年 / 月 / 日
class uint_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"([{0}]?)((?:{1})+)".format(
            td.split_texts(td.wordtype.quantity),
            td.split_texts(td.wordtype.unit))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        quantity = self.parse_quantity(m.group(1)) != None
        unit = self.parse_unit(m.group(2))

        return Unit(str, (st, ed), unit, quantity)


# 周三 周日
class week_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0}))((?:{1}))".format(
            td.split_texts(td.wordtype.unit, td.unit.week),
            td.split_texts(td.wordtype.digit))

        ex_sunday = u"((?:{0}))((?:{1}))".format(
            td.split_texts(td.wordtype.unit, td.unit.week),
            td.split_texts(td.wordtype.unit, td.unit.day))

        self.add_re(ex, self.process)
        self.add_re(ex_sunday, self.sunday)


    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        unit = self.parse_unit(m.group(1))
        digit = self.parse_digits(m.group(2))

        return Time(str, (st, ed), UD(unit, digit, weekday=True))


    def sunday(self, m, args):
        # check
        str, st, ed = self.parse_match(m)
        return Time(str, (st, ed), UD(td.unit.week, 7, weekday=True))


# relation
class relation_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0})+)".format(td.split_texts(td.wordtype.relation))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        relation = self.parse_relation(m.group(1))

        if relation == td.relation.coo: return Relation_COO(str, (st, ed))
        elif relation == td.relation.span: return Relation_Span(str, (st, ed))
        elif relation == td.relation.start: return Relation_Start(str, (st, ed))
        return None




# Direct
class direct_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0})*)((?:{1}))".format(
            td.split_texts(td.wordtype.degree),
            td.split_texts(td.wordtype.direct))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        degree = self.parse_degree(m.group(1))
        direct = self.parse_direct(m.group(2))

        sum = 0 if degree == None else degree
        if direct[1] == None:
            return Direct(str, (st+len(m.group(1)), ed), direct)
        else:
            if direct[1] < 0: sum = sum * -1
            direct = list(direct)
            direct[1] += sum
            return Direct(str, (st, ed), direct)





# speical hour
class special_hour_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0})+)".format(td.split_texts(td.wordtype.special_hour))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        info = self.parse_special_hour(m.group(1))

        return SpeicalHour(str, (st, ed), *info)




# calendar
class calendar_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0})+)".format(td.split_texts(td.wordtype.calendar))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        calendar = self.parse_calendar(m.group(1))

        return Calendar(str, (st, ed), calendar == td.calendar.lunar)


# holiday
class holiday_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0})+)".format(td.split_texts(td.wordtype.holiday))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        (type, month, day, duration_day ) = self.parse_holiday(m.group(1))
        time = Holiday(str, (st, ed), month, day, duration_day, lunar=(type == td.calendar.lunar))
        return time


# seasons
class seasons_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex = u"((?:{0}))".format(td.split_texts(td.wordtype.season))
        self.add_re(ex, self.process)

    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        (start_month, end_month ) = self.parse_season(m.group(1))
        return Season(str, (st, ed), start_month, end_month)





# lunar 腊月 / w
class lunar_re(time_re):
    def __init__(self):
        time_re.__init__(self)
        ex_lunar_month = u"((?:{0})+)".format(td.split_texts(td.wordtype.lunar_month))
        ex_lunar_day = u"((?:{0})+)((?:{1})+)".format(
            td.split_texts(td.wordtype.lunar_day),
            td.split_texts(td.wordtype.digit))
        self.add_re(ex_lunar_month, self.process_lunar_month)
        self.add_re(ex_lunar_day, self.process_lunar_day)

    def process_lunar_month(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        month = self.parse_lunar_month(m.group(1))

        return Time(str, (st, ed), UD(td.unit.month, month), lunar=True)

    def process_lunar_day(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # parse
        day = self.parse_lunar_month(m.group(1))
        digit = self.parse_digits(m.group(2))

        return Time(str, (st, ed),  UD(td.unit.day, digit), lunar=True)



class format_re(time_re):
    colon = [u':', u'：']
    def __init__(self):
        time_re.__init__(self)
        delimiter = u".|\-|:|/|：|\\\|，|,"
        ex = u"([{0}]*)([{1}]*)" \
             u"([{0}]*)([{1}]*)" \
             u"([{0}]*)([{1}]*)" \
             u"([{0}]*)([{1}]*)" \
             u"([{0}]*)([{1}]*)" \
             u"([{0}]*)".format(
            td.split_texts(td.wordtype.digit),
            delimiter)
        self.add_re(ex, self.process)


    def process(self, m, args):
        # check
        str, st, ed = self.parse_match(m)

        # digits
        digits = []
        signs = []
        for i in xrange(1, 12, 2):
            d = self.parse_digits(m.group(i))
            if d == None: continue
            digits.append(d)
            if i < 11: signs.append(m.group(i+1))

        count = len(digits)
        if count < 2: return None
        if count == 4: return None

        # guess all unit possible
        units_matrix = []
        for d in digits: units_matrix.append( self.guess_valid_units(d) )

        # dfs
        def dfs(sort_unit_list, sort_unit, units_matrix, row):
            # find one
            if row >= len(units_matrix):
                sort_unit_list.append(sort_unit)
                return

            if len(sort_unit) == 0:
                for u in units_matrix[row]:
                    sort_unit = []
                    sort_unit.append(u)
                    dfs(sort_unit_list, sort_unit, units_matrix, row + 1)
            else:
                last_unit = sort_unit[-1]
                for u in units_matrix[row]:
                    if u - last_unit < 1: continue
                    if u - last_unit > 1: return
                    sort_unit.append(u)
                    dfs(sort_unit_list, sort_unit, units_matrix, row+1)

        # sort unit list
        sort_unit_list = []
        dfs(sort_unit_list, [], units_matrix, 0)

        # tv
        tv = None
        if len(sort_unit_list) == 0: tv = None
        elif len(sort_unit_list) == 1:
            tv = self.gen_time_vec(digits, sort_unit_list[0][0])
        else:
            # print("{0} > 1 possible".format(sort_unit_list))
            tv = self.gen_time_vec(digits, sort_unit_list[0][0])
            u_dict = {u[0]: None for u in sort_unit_list}
            # 8-9 or 08:09
            if count == 2:
                if u_dict.has_key(td.unit.hour) and (signs[0] in format_re.colon):
                    tv = self.gen_time_vec(digits, td.unit.hour)
                elif u_dict.has_key(td.unit.month):
                    tv = self.gen_time_vec(digits, td.unit.month)
            elif count == 3:
                if u_dict.has_key(td.unit.hour) and (signs[0] in format_re.colon):
                    tv = self.gen_time_vec(digits, td.unit.hour)
            elif count == 4:
                return None

        if tv == None: return None

        partime = Time(str, (st, ed), tv)
        return partime


    def guess_valid_units(self, v):
        if v > 59: return [td.unit.year]
        elif v > 31: return [td.unit.year, td.unit.minute, td.unit.second]
        elif v > 23: return [td.unit.year, td.unit.day, td.unit.minute, td.unit.second]
        elif v > 12: return [td.unit.year, td.unit.day, td.unit.hour, td.unit.minute, td.unit.second]
        else: return [td.unit.year, td.unit.month, td.unit.day, td.unit.hour, td.unit.minute, td.unit.second]

    def gen_time_vec(self, v, unit_start):
        datas = []
        for i in xrange(len(v)):
            datas.append(UD(unit_start + i, v[i]))
        return datas



class parser(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            orig = super(parser, cls)
            cls.__instance = orig.__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self._classes = []
        self._classes.append(digit_re())
        self._classes.append(uint_re())
        self._classes.append(week_re())
        self._classes.append(relation_re())
        self._classes.append(direct_re())
        self._classes.append(special_hour_re())
        self._classes.append(calendar_re())
        self._classes.append(holiday_re())
        self._classes.append(seasons_re())
        self._classes.append(lunar_re())
        self._classes.append(format_re())


    def parse(self, sentence, splits, pos=None, endpos=None, args=None):
        times = self.split(sentence, splits, pos, endpos, args)
        times = self.dropout_repeater(sentence, splits, times, pos, endpos, args)
        return times



    def split(self, sentence, splits, pos = None, endpos = None, args = None):
        entities = []
        for cls in self._classes:
            list = cls.parse(sentence, splits, pos, endpos, args)
            # inert sort
            for e in list:
                insert = False
                for i in xrange(len(entities)):
                    item = entities[i]
                    if e.pos_min > item.pos_min: continue
                    entities.insert(i, e)
                    insert = True
                    break
                if not insert: entities.append(e)

        return  entities


    def dropout_repeater(self, sentence, splits, times, pos, endpos, args):
        new_list = []
        for t in times:
            # first
            if len(new_list) == 0:
                new_list.append(t)
                continue

            # check conflict
            last_t = new_list[-1]

            # t and last_t is independent
            tpos, last_pos = t.pos_span, last_t.pos_span
            if last_pos[1] <= tpos[0]:
                new_list.append(t)
                continue

            # same span
            if tpos == last_pos:
                if t.level > last_t.level: new_list[-1] = t


            # last_t contain t
            elif last_pos[0] <= tpos[0] and tpos[1] <= last_pos[1]:
                continue

            # t contain last_t
            elif tpos[0] <= last_pos[0] and last_pos[1] <= tpos[1]:
                new_list[-1] = t

            # cross !!
            else:
                # match once
                st, ed = last_pos[1], tpos[1]
                find = False
                new_times = self.split(sentence, splits, st, ed, args)
                for new_t in new_times:
                    if new_t.pos_span != (st, ed): continue
                    new_list.append(new_t)
                    find = True
                    # print("cut-once: {0}".format(new_t))
                    break
                if find: continue

                # match again
                st, ed = last_pos[0], tpos[0]
                new_times = self.split(sentence, splits, st, ed, args)
                for new_t in new_times:
                    if new_t.pos_span != (st, ed): continue
                    new_list[-1] = new_t
                    new_list.append(t)
                    find = True
                    # print("cut-again: {0}".format(new_t))
                    break
                if find: continue

                # assert False

        return new_list


parse = parser().parse