# -*- coding: utf-8 -*-
import sys
import copy
import math

import numpy as np

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
        day_direct = TimeDirect(td.relative.parent, -1) if self.day < 0 else None
        start = Time(self.sentence, self.pos_span, [td.unit.month, td.unit.day], [self.month, self.day], [None, day_direct], self.lunar)
        duration = Duration(self.sentence, self.pos_span, [td.unit.day], [self.duration], [TimeDirect(td.relative.parent, 1)])
        return StartDuration(self.sentence, self.pos_span, start, duration)




## ==================================================== TimeChunk ==================================================== ##

class TimeDirect():
    def __init__(self, relative = None, value = 0):
        self.relative = relative
        self.value = value

    @property
    def none(self): return self.relative == td.relative.none

    @property
    def now(self): return self.relative == td.relative.now

    @property
    def parent(self): return self.relative == td.relative.parent


    def __str__(self):
        if self.relative == td.relative.none: return "none"
        else: return u"{0}{1}".format(self.value, "p" if self.relative == td.relative.parent else "c" )



class TimeChunk(TimeCell):
    time_level = 1
    def __init__(self, sentence, pos_span, units, values, directs = None):
        TimeCell.__init__(self, sentence, pos_span)
        self.units = []
        self.values = []
        self.directs = []
        self.adds(units, values, directs or [TimeDirect()] * len(units))


    def __str__(self):
        v = u""
        for i in xrange(len(self.units)):
            v += u"{0}{1} ".format(self.values[i], td.time_unit_desc[self.units[i]])

        d = u""
        for i in xrange(len(self.directs)):
            d += u"{0} ".format(self.directs[i])

        return TimeCell.__str__(self) + "   " + "t:({0})  d:({1})".format(v, d)


    def adds(self, units, values, directs = None):
        if directs == None: directs = [TimeDirect()] * len(units)
        for i in xrange(len(units)): self.add(units[i], values[i], directs[i])


    def add(self, unit, value,  direct = None):

        for i in xrange(len(self.units)-1, -1, -1):
            u = self.units[i]
            if unit <= u: break
            if unit > u: continue
            self.units.insert(i, unit)
            self.values.insert(i, value)
            self.directs.insert(i, direct)
            return

        self.values.append(value)
        self.units.append(unit)
        self.directs.append(direct)


    def has_unit(self, unit):
        if type(unit) != list: return unit in self.units
        for u in unit:
            if u in self.units: return True
        return False


    def unit_index(self, unit): return self.units.index(unit) if self.has_unit(unit) else None

    def upgrade(self): self._level += 1


class Time(TimeChunk):
    def __init__(self, sentence, pos_span, units, values, directs = None, lunar = False):
        TimeChunk.__init__(self, sentence, pos_span, units, values, directs)
        self.lunar = lunar

    def __str__(self):
        s = TimeChunk.__str__(self)
        if self.lunar: s += "lunar"
        return s



class Duration(TimeChunk):
    def __init__(self, sentence, pos_span, units, values, directs = None):
        TimeChunk.__init__(self, sentence, pos_span, units, values, directs)



## ====================================================== Group ====================================================== ##



class TimeGroup(TimeCell):
    time_level = 2
    def __init__(self, sentence, pos_span):
        TimeCell.__init__(self, sentence, pos_span)


class StartEnd(TimeGroup):
    def __init__(self, sentence, pos_span, start, end):
        TimeGroup.__init__(self, sentence, pos_span)
        self._start = start
        self._end = end

    def __str__(self):
        s = TimeGroup.__str__(self)
        return u"{0}: start:[{1}]  ~  end:[{2}]".format(s, self._start, self._end)

    @property
    def start(self): return self._start

    @property
    def end(self): return self._end



class StartDuration(TimeGroup):
    def __init__(self, sentence, pos_span, start, duration):
        TimeGroup.__init__(self, sentence, pos_span)
        self._start = start
        self._duration = duration

    def __str__(self):
        s = TimeGroup.__str__(self)
        return u"{0}  start:[{1}]   duration:[{2}]".format(s, self._start, self._duration)

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