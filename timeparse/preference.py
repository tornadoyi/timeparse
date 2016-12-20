import sys
import math
import copy

import numpy as np

import time_define as td
import time_func as tf
import time_algorithm as alg

class Prefer(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs): return self.do(*args, **kwargs)

    def do(self, *args, **kwargs): return None


# ============================================== Padding ============================================== #


class UnitPadding(Prefer):
    def __init__(self):
        Prefer.__init__(self)

    def get_choices(self, unit, value, pos_span, args):

        # current time
        cur = args.timecore.vector
        if unit == td.unit.year:
            t = tf.time_vector(year=value)
            return (t, t, t)

        # target time
        target = alg.modify_vector(cur, unit, value)


        # last and next time
        sp_hour = args.collector.find_nearest_special_hour(pos_span)
        last = next = None
        if unit == td.unit.week: #unit - int(unit) != 0:
            last = tf.delta_time(target, unit, -1)
            next = tf.delta_time(target, unit, 1)

        elif unit == td.unit.hour and value < 12 and sp_hour == None:
            last = target
            next = copy.deepcopy(target)
            next[td.unit.hour] = value + 12

        else:
            h_unit = int(math.ceil(unit)) - 1
            last = tf.delta_time(target, h_unit, -1)
            next = tf.delta_time(target, h_unit, 1)

        return (target, last, next)



class RecentPadding(UnitPadding):
    def do(self, value, unit, pos_span, args):
        choices = self.get_choices(value, unit, pos_span, args)

        # current time
        cur = args.timecore.timestamp

        # short and history
        padding = choices[0]
        distance = sys.maxint
        for v in choices:
            ts = tf.vec2timestamp(v)
            d = np.abs(ts - cur)
            if d > distance: continue
            padding = v
            distance = d

        return padding


class HistoryPadding(UnitPadding):
    def do(self, unit, value, pos_span, args):
        choices = self.get_choices( unit, value, pos_span, args)

        # current time
        cur = args.timecore.timestamp

        # short and history
        padding = choices[0]
        distance = sys.maxint
        for v in choices:
            ts = tf.vec2timestamp(v)
            if ts > cur: continue
            d = np.abs(ts - cur)
            if d > distance: continue
            padding = v
            distance = d

        return padding


class FuturePadding(UnitPadding):
    def do(self, unit, value, pos_span, args):
        choices = self.get_choices(unit, value, pos_span, args)

        # current time
        cur = args.timecore.timestamp

        # short and history
        padding = choices[0]
        distance = sys.maxint
        for v in choices:
            ts = tf.vec2timestamp(v)
            if ts < cur: continue
            d = np.abs(ts - cur)
            if d > distance: continue
            padding = v
            distance = d

        return padding




# ============================================== Infinity ============================================== #

class Infinity(Prefer):
    def __init__(self, delta):
        Prefer.__init__(self)
        self.delta = delta


    def do(self, start, end, args):
        v = None
        if start == float("-inf"):
            acc = tf.accuracy(end)
            v = tf.delta_time(end, acc[1], -1 * self.delta)

        elif end == float("inf"):
            acc = tf.accuracy(start)
            v = tf.delta_time(start, acc[1], 1 * self.delta)

        else: assert False

        return v