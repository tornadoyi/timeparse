# -*- coding: utf-8 -*-
import sys
import copy
import math

import numpy as np
from pyplus import  *

import time_define as td
import time_func as tf


class TimeCell():
    time_level = 0
    def __init__(self, sentence, pos_span):
        self._level = self.time_level
        self._sentence = sentence
        self.pos_span = tuple(pos_span)


    def __str__(self):
        cname = str(self.__class__).split('.')[-1]
        return u"{0}({1})".format(cname, self.word)

    @property
    def level(self): return self._level

    @property
    def sentence(self): return self._sentence

    @property
    def word(self): return self._sentence[self.pos_span[0]: self.pos_span[1]]

    @property
    def pos_min(self): return self.pos_span[0]

    @property
    def pos_max(self): return self.pos_span[1]

    def adjacent(self, cell): return (self.pos_span[0] == cell.pos_span[1]) or (self.pos_span[1] == cell.pos_span[0])

    def merge(self, other):
        min = np.min((self.pos_span[0], other.pos_span[0]))
        max = np.max((self.pos_span[1], other.pos_span[1]))
        self.pos_span = (min, max)

    def upgrade(self): pass


class Digit(TimeCell):
    def __init__(self, sentence, pos_span, value, quantity = False):
        TimeCell.__init__(self, sentence, pos_span)
        self._value = value
        self._quantity = quantity

    @property
    def value(self): return self._value

    @property
    def quantity(self): return self._quantity


class Unit(TimeCell):
    def __init__(self, sentence, pos_span, value, quantity = False):
        TimeCell.__init__(self, sentence, pos_span)
        self._value = value
        self._quantity = quantity

    @property
    def value(self): return self._value

    @property
    def quantity(self): return self._quantity


class Direct(TimeCell):
    def __init__(self, sentence, pos_span, value):
        TimeCell.__init__(self, sentence, pos_span)
        self._value = tuple(value)

    @property
    def value(self): return self._value

    @property
    def relative(self): return self._value[0]

    @property
    def info_with_unit(self): return self._value[1]

    @property
    def info_with_front(self): return self._value[2]

    @property
    def info_with_back(self): return self._value[3]



class SpeicalHour(TimeCell):
    def __init__(self, sentence, pos_span, start, end, convert):
        TimeCell.__init__(self, sentence, pos_span)
        self.convert = convert
        self.start = start
        self.end = end


class Calendar(TimeCell):
    def __init__(self, sentence, pos_span, lunar):
        TimeCell.__init__(self, sentence, pos_span)
        self.lunar = lunar


class Holiday(TimeCell):
    def __init__(self, sentence, pos_span, month, day, duration, lunar):
        TimeCell.__init__(self, sentence, pos_span)
        self.month = month
        self.day = day
        self.duration = duration
        self.lunar = lunar


    def upgrade(self):
        rel_dir = qdict(direct=-1, relative=td.method.number) if self.day < 0 else {}
        start = Time(self.sentence, self.pos_span, [UD(td.unit.month, self.month), UD(td.unit.day, self.day, **rel_dir)], self.lunar)
        duration = Duration(self.sentence, self.pos_span, UD(td.unit.day, self.duration, direct=1, relative=td.method.number))
        return StartDuration(self.sentence, self.pos_span, start, duration)



class Season(TimeCell):
    def __init__(self, sentence, pos_span, start_month, end_month):
        TimeCell.__init__(self, sentence, pos_span)
        self.start_month = start_month
        self.end_month = end_month


    def upgrade(self):
        start = Time(self.sentence, self.pos_span, UD(td.unit.month, self.start_month))
        duration = Duration(self.sentence, self.pos_span, UD(td.unit.month, self.end_month - self.start_month + 1))
        return StartDuration(self.sentence, self.pos_span, start, duration)



## ==================================================== TimeChunk ==================================================== ##

class UD(qdict):
    def __init__(self, unit, value, *args, **kwargs):
        qdict.__init__(self, unit=unit, value=value, *args, **kwargs)
        assert self.value != None
        assert self.unit != None

    def __str__(self):
        uv = other = ""
        # value unit
        uv = "{0}{1}".format(self.value, td.time_unit_desc[self.unit])
        if self.weekday: uv = "{0}{1}".format(td.time_unit_desc[self.unit], self.value)

        # direct
        if self.method != None: other += "{0}{1}".format(
            self.direct,
            "s" if self.method == td.method.shift else "d" if self.method == td.method.delta else "n")

        return "{0}({1})".format(uv, other) if len(other) > 0 else uv


class TimeChunk(TimeCell):
    time_level = 1
    def __init__(self, sentence, pos_span, datas = None):
        TimeCell.__init__(self, sentence, pos_span)
        self.datas = []
        self.add(datas or [])


    def __getitem__(self, item): return self.datas[item]

    def __str__(self):
        s_data = ""
        for d in self.datas: s_data += d.__str__() + " "
        return u"{0} {1}".format(TimeCell.__str__(self), s_data)

    @property
    def units(self): return [d.unit for d in self.datas]


    def add(self, datas):
        def _add(d):
            assert type(d) == UD
            for i in xrange(len(self.datas)):
                u = self.datas[i].unit
                assert d.unit != u
                if d.unit > u: break
                self.datas.insert(i, d)
                return

            self.datas.append(d)

        if type(datas) != list: datas = [datas]
        for d in datas: _add(d)


    def has_unit(self, unit):
        if type(unit) != list: return unit in [d.unit for d in self.datas]
        for u in unit:
            if u in [d.unit for d in self.datas]: return True
        return False


    def unit_index(self, unit):
        for i in xrange(len(self.datas)):
            d = self.datas[i]
            if d.unit == unit: return i
            if d.unit > unit: break
        return None

    def upgrade(self): self._level += 1


class Time(TimeChunk):
    def __init__(self, sentence, pos_span, datas = None, lunar = False):
        TimeChunk.__init__(self, sentence, pos_span, datas)
        self.lunar = lunar

    def __str__(self):
        s = TimeChunk.__str__(self)
        if self.lunar: s += "lunar"
        return s



class Duration(TimeChunk):
    def __init__(self, sentence, pos_span, datas = None):
        TimeChunk.__init__(self, sentence, pos_span, datas)



## ====================================================== Group ====================================================== ##



class TimeGroup(TimeCell):
    time_level = 2
    def __init__(self, sentence, pos_span):
        TimeCell.__init__(self, sentence, pos_span)

    def normalize_time(self, t):
        if isinstance(t, Time) or t == float("-inf") or t == float("inf"): return t
        elif isinstance(t, Duration): return Time(t.sentence, t.pos_span, t.datas)
        else: assert False


class StartEnd(TimeGroup):
    def __init__(self, sentence, pos_span, start, end):
        TimeGroup.__init__(self, sentence, pos_span)
        self._start = self.normalize_time(start)
        self._end = self.normalize_time(end)

    def __str__(self):
        s = TimeGroup.__str__(self)
        return u"{0}: {1}  ~  {2}".format(s, self._start, self._end)

    @property
    def start(self): return self._start

    @property
    def end(self): return self._end



class StartDuration(TimeGroup):
    def __init__(self, sentence, pos_span, start, duration):
        TimeGroup.__init__(self, sentence, pos_span)
        self._start = self.normalize_time(start)
        self._duration = duration

    def __str__(self):
        s = TimeGroup.__str__(self)
        return u"{0}  {1}  {2}".format(s, self._start, self._duration)

    @property
    def start(self): return self._start

    @property
    def duration(self): return self._duration



class Relation(TimeCell):
    time_level = 3
    def __init__(self, sentence, pos_span, type):
        TimeCell.__init__(self, sentence, pos_span)
        self._type = type

    @property
    def type(self): return self._type


class Relation_COO(Relation):
    def __init__(self, sentence, pos_span):
        Relation.__init__(self, sentence, pos_span, td.relation.coo)


class Relation_Span(Relation):
    def __init__(self, sentence, pos_span):
        Relation.__init__(self, sentence, pos_span, td.relation.span)


class Relation_Start(Relation):
    def __init__(self, sentence, pos_span):
        Relation.__init__(self, sentence, pos_span, td.relation.start)





## ====================================================== VectorTime ====================================================== ##

class VectorTime(TimeCell):
    def __init__(self, sentence, pos_span, start, end = None, duration = None):
        TimeCell.__init__(self, sentence, pos_span)
        self.start = start
        self.end = end or tf.time_vector()
        self.duration = duration or tf.time_vector()


    def __str__(self):
        s = u"("
        if tf.accuracy(self.start) != (None, None):
            s += tf.timevec_format(self.start)

        if tf.accuracy(self.end) != (None, None):
            s += ", "
            s += tf.timevec_format(self.end)

        if tf.accuracy(self.duration) != (None, None):
            s += ", "
            s += tf.timevec_format(self.duration, with_unit=True)

        s += u")"
        return s