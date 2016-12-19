# -*- coding: utf-8 -*-
import sys
import re
import math
import copy

import numpy as np

import time_define as td
from time_struct import *
import time_func as tf



class ChunkRegularization():

    # convert unit to int
    def unit_integralization(self, vector):
        int_vector = [None] * len(vector)
        for i in xrange(len(vector)):
            v = vector[i]
            if v == None: continue
            int_vector[i] = int(v)
            d = v - int(v)
            if d == 0: continue
            if i+1 >= len(vector):break
            vector[i+1] = int(tf.unit2unit(d, i, i+1))
        return int_vector


    # convert lunar
    def convert_lunar(self, vector, args):
        v = tf.lunar2solar(vector[0], vector[1], vector[2] or tf.unit_min(td.unit.month))
        solar_vector = copy.deepcopy(vector)
        solar_vector[0:3] = v[0:3]
        if vector[2] == None: solar_vector[2] = None
        return solar_vector


    # render each unit
    def render_units(self, vector, pos_span, args):
        vector = copy.deepcopy(vector)

        # year
        if vector[td.unit.year] == None: return vector
        cur_year = args.timecore.unit(td.unit.year)
        zeros = np.power(10, int(np.log(cur_year) / np.log(10)))
        if vector[td.unit.year] < zeros: vector[td.unit.year] += cur_year / int(zeros) * int(zeros)


        return vector





class TimeRegularization(ChunkRegularization):

    def regularize(self, time, args):
        # padding
        time = self.high_order_units_padding(time, args)

        # dropout directs
        vector, duration = self.dropout_directs(time, args)

        # integralization
        vector = self.unit_integralization(vector)
        duration = self.unit_integralization(duration) if duration else duration

        # convert lunar
        if time.lunar == True: vector = self.convert_lunar(vector, args)

        # render units
        vector = self.render_units(vector, time.pos_span, args)

        return vector, duration


    
    def high_order_units_padding(self, time, args):

        def padding_units_by_collector(t):
            # direct that relative to now is needn't padding
            # weekday without direct is needn't padding
            if (t.directs[0] and t.directs[0].relative == 0) or \
                (time.units[0] == td.unit.week and t.directs[0] == None): return t

            values = []; units = []; directs = []
            end_unit = int(math.ceil(time.units[0])) - 1
            for i in xrange(end_unit, -1, -1):
                v = args.collector.find_nearest_unit(time.pos_span, i)
                if v == None: break
                u_idx = v.unit_index(i)
                values.append(v.values[u_idx])
                units.append(i)
                directs.append(v.directs[u_idx])

            t = copy.deepcopy(time)
            values.reverse(); units.reverse(); directs.reverse()
            t.values = values + t.values
            t.units = units + t.units
            t.directs = directs + t.directs
            return t


        def padding_special_hour(t):
            # find special hour
            sp_hour = args.collector.find_nearest_special_hour(time.pos_span)
            if sp_hour == None or sp_hour.convert == None: return t

            # find hour index
            hour_idx = t.unit_index(td.unit.hour)
            if hour_idx == None: return t

            # convert
            (v_hour, next_day) = sp_hour.convert(t.values[hour_idx])
            t.values[hour_idx] = v_hour
            day_idx = t.unit_index(td.unit.day)
            if next_day and day_idx != None:
                d = t.directs[day_idx]
                if d == None or d.value > 0:
                    t.values[day_idx] += 1
                elif d.value == 0:
                    t.values[day_idx] += 1
                    d.value = 1
                else:
                    t.values[day_idx] -= 1
            return t


        def padding_units_by_preference(t):
            # direct that relative to now is needn't padding
            # convert week
            if (t.directs[0] and t.directs[0].relative == 0): return t
            values = args.padding(t.values[0], t.units[0], t.pos_span, args)
            values = [v for v in values if v != None]
            units = [i for i in xrange(len(values))]
            directs = [None] * len(values)

            for i in xrange(len(t.units)):
                unit = t.units[i]
                if unit <= len(values) - 1: continue
                values.append(t.values[i])
                units.append(t.units[i])
                directs.append(t.directs[i])

            t.values = values
            t.units = units
            t.directs = directs
            return t

        # copy time
        t = copy.deepcopy(time)
        t = padding_units_by_collector(t)
        t = padding_special_hour(t)
        t = padding_units_by_preference(t)
        return t



    def dropout_directs(self, time, args):

        def fill_vector(src, dst, start=None, end=None, overlap=False):
            start = start or 0
            end = end or len(src)
            for i in xrange(int(start), len(src), 1):
                if i >= end: break
                if src[i] == None: break
                if not overlap and dst[i] != None: continue
                dst[i] = src[i]

        curvector = args.timecore.vector(int(math.ceil(time.units[-1])))
        vector = tf.time_vector()
        duration = tf.time_vector()


        for i in xrange(len(time.units)):
            u, v, d = time.units[i], time.values[i], time.directs[i]

            # padding with preference
            if d == None:
                if u == td.unit.week:
                    assert False
                elif u == td.unit.quarter:
                    u = td.unit.minute
                    v = tf.unit2unit(v, td.unit.quarter, td.unit.minute)

                vec = args.padding(v, u, time.pos_span, args)
                fill_vector(vec, vector, end=u + 1)
                continue


            # dropout directs
            # relative to now
            if d.relative == 0:
                if u == td.unit.week:
                    start = args.timecore.weekday(v)
                    end = tf.delta_time(start, td.unit.day, 7 * d.value)
                    fill_vector(end, vector, end=u + 1)

                else:
                    vec = tf.delta_time(curvector, u, v * d.value)
                    fill_vector(vec, vector, end=u + 1)
                continue


            # relative to parent
            # week then create duration
            if u == td.unit.week:
                vec = tf.start_time_at_week(vector[0], vector[1], d.value * v)
                fill_vector(vec, vector, end=u + 1, overlap=True)
                duration[td.unit.day] = tf.unit2unit(1, td.unit.week, td.unit.day)


            # quarter then create duration
            elif u == td.unit.quarter:
                value = d.value * v * tf.unit2unit(1, td.unit.quarter, td.unit.quarter)
                vector[td.unit.second] = value
                duration[td.unit.second] = tf.unit2unit(1, td.unit.quarter, td.unit.quarter)


            # other units
            else:
                assert u != td.unit.year
                (min, max) = tf.unit_range_at_time(vector, u)
                if duration[u] != None: min, max = vector[u], vector[u]+duration[u]-1

                vector[u] = max + d.value * v + 1 if d.value < 0 else min + d.value * v - 1
                duration[u] = None


        if duration == tf.time_vector(): duration = None
        return vector, duration








class DurationRegularization(ChunkRegularization):

    def regularize(self, time, args):
        vector = self.dropout_directs(time, args)
        vector = self.unit_integralization(vector)
        return vector



    def dropout_directs(self, time, args):
        vector = tf.time_vector()
        negtive = False
        for i in xrange(len(time.units)):
            u, v, d = time.units[i], time.values[i], time.directs[i]
            if u == td.unit.week:
                u = td.unit.day
                v = tf.unit2unit(v, td.unit.week, td.unit.day)
            elif u == td.unit.quarter:
                u = td.unit.minute
                v = tf.unit2unit(v, td.unit.quarter, td.unit.minute)

            vector[u] = v if vector[u] == None else vector[u] + v
            if d and d.value < 0: negtive = True

        if negtive:
            for i in xrange(len(vector)):
                if vector[i] == None: continue
                vector[i] *= -1
        return vector




class GroupRegularization():
    def __init__(self):
        self.time_reg = TimeRegularization()
        self.duration_reg = DurationRegularization()


    @property
    def time(self): return self.time_reg

    @property
    def duration(self): return self.duration_reg



class SingleTimeRegularization(GroupRegularization):

    def regularize(self, t, args):
        v, duration = self.time.regularize(t, args)
        if duration == None:
            return VectorTime(t.sentence, t.pos_span, start=v, end=v)
        else:
            return VectorTime(t.sentence, t.pos_span, start=v, duration=duration)



class SingleDurationRegularization(GroupRegularization):

    def regularize(self, t, args):
        unit = t.units[-1]
        start = args.timecore.vector(unit)
        start = tf.delta_time(start, unit, 1*t.directs[0].value)
        duration = self.duration.regularize(t, args)
        return VectorTime(t.sentence, t.pos_span, start=start, duration=duration)


class StartEndRegularization(GroupRegularization):

    def regularize(self, t, args):
        start = end = None

        if t.start == float('-inf'):
            end, duration = self.time.regularize(t.end, args)
            start = args.infinity(t.start, end, args)
            if duration: end = tf.shift_time(end, duration)


        elif t.end == float('inf'):
            start, _ = self.time.regularize(t.start, args)
            end = args.infinity(start, t.end, args)

        else:
            start, _ = self.time.regularize(t.start, args)
            end, duration = self.time.regularize(t.end, args)
            if duration: end = tf.shift_time(end, duration)


        return VectorTime(t.sentence, t.pos_span, start=start, end=end)



class StartDurationRegularization(GroupRegularization):

    def regularize(self, t, args):
        start, duration = self.time.regularize(t.start, args)
        duration = self.duration.regularize(t.duration, args)
        t =  VectorTime(t.sentence, t.pos_span, start=start, duration=duration)
        t = self.unit_align(t, args)
        return t


    def unit_align(self, t, args):
        # get accuracy
        start, duration = t.start, t.duration
        acc_st = tf.accuracy(start)
        acc_du = tf.accuracy(duration)
        if acc_st[1] >= acc_du[0]: return t

        # padding
        for i in xrange(acc_st[1]+1, acc_du[0]+1, 1):
            (min, max) = tf.unit_range_at_time(start, i)
            start[i] = min if duration[acc_du[0]] >= 0 else max

        return t





class RegularizationManager():
    def __init__(self):
        self._map = {
            Time:   SingleTimeRegularization(),
            Duration: SingleDurationRegularization(),
            StartEnd: StartEndRegularization(),
            StartDuration: StartDurationRegularization(),
        }


    def regularize(self, times, args):
        new_times = []
        for t in times:
            reg = self._map.get(t.__class__)
            assert reg != None
            t = reg.regularize(t, args)

            # padding low units
            if args.fulltime: self.low_units_padding(t)

            new_times.append(t)

        return new_times


    def low_units_padding(self, t):
        def padding(v, use_max):
            acc_v = tf.accuracy(v)
            # padding
            for i in xrange(acc_v[1] + 1, len(v), 1):
                (min, max) = tf.unit_range_at_time(v, i)
                v[i] = max if use_max == True else min


        if tf.accuracy(t.end) != (None, None): padding(t.end, use_max=True)

        if tf.accuracy(t.start) != (None, None):
            acc_du = tf.accuracy(t.duration)
            if acc_du != (None, None) and t.duration[acc_du[0]] < 0:
                padding(t.start, use_max=True)
            else:
                padding(t.start, use_max=False)

        return t




regularization = RegularizationManager()