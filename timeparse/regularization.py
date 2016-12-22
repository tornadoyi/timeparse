# -*- coding: utf-8 -*-
import sys
import re
import math
import copy

import numpy as np

import time_define as td
from time_struct import *
import time_func_ext as tf



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
            if  t[0].method == td.method.shift or \
                t[0].method == td.method.delta or \
                t[0].weekday == True: return t

            end_unit = int(math.ceil(time[0].unit)) - 1
            for i in xrange(end_unit, -1, -1):
                v = args.collector.find_nearest_unit(time.pos_span, i)
                if v == None: break
                u_idx = v.unit_index(i)
                t.add(v.datas[u_idx])

            return t


        def padding_special_hour(t):
            # find special hour
            sp_hour = args.collector.find_nearest_special_hour(time.pos_span)
            if sp_hour == None or sp_hour.convert == None: return t

            # find hour index
            hour_idx = t.unit_index(td.unit.hour)
            if hour_idx == None: return t

            # convert
            (v_hour, next_day) = sp_hour.convert(t[hour_idx].value)
            t[hour_idx].value = v_hour
            day_idx = t.unit_index(td.unit.day)
            if next_day and day_idx != None:
                method, direct = t[day_idx].method, t[day_idx].direct
                if method == td.method.none or direct > 0:
                    t[day_idx].value += 1
                elif direct == 0:
                    t[day_idx].value += 1
                    t[day_idx].direct = 1
                else:
                    t[day_idx].value -= 1
            return t


        def padding_units_by_preference(t):
            # direct that relative to now is needn't padding
            # convert week
            if t[0].method == td.method.shift or t[0].method == td.method.delta: return t
            values = args.padding(t[0].unit, t[0].value, t.pos_span, args)
            values = [v for v in values if v != None]
            units = [i for i in xrange(len(values))]

            for i in xrange(int(math.ceil(t[0].unit))):
                t.add(UD(units[i], values[i]))

            return t

        # copy time
        t = copy.deepcopy(time)
        t = padding_units_by_collector(t)
        t = padding_special_hour(t)
        t = padding_units_by_preference(t)
        return t



    def dropout_directs(self, time, args):

        curvector = args.timecore.vector
        vector = tf.time_vector()
        duration = tf.time_vector()

        def update_vectors(vec, dur, unit, overlap = False):

            def fill_vector(src, dst, start=None, end=None, overlap=False):
                if src == None or dst == None: return
                start = start or 0
                end = end or len(src)
                for i in xrange(int(start), len(src), 1):
                    if i >= end: break
                    if not overlap and dst[i] != None: continue
                    dst[i] = src[i]

            # update vector
            fill_vector(vec, vector, end=unit+1, overlap=overlap)

            # update duration
            if dur != None: fill_vector(dur, duration, unit+1)
            else: duration[0:int(unit+1)] = [None] * int(unit+1)


        for i in xrange(len(time.units)):
            unit, value, direct, method = time[i].unit, time[i].value, time[i].direct, time[i].method

            # absolute unit
            if method == td.method.none:
                if unit - int(unit) == 0:
                    vector[unit] = value
                else:
                    vec, dur = tf.transform_time_by_modify_unit(vector, unit, value)
                    update_vectors(vec, dur, unit)


            # relative to now
            elif method == td.method.shift:
                if time[i].weekday == True:
                    vec, dur = tf.shift_time(curvector, unit, shift=direct, weekday=value)
                else:
                    vec, dur = tf.shift_time(curvector, unit, shift=value*direct)
                update_vectors(vec, dur, unit)


            # relative to parent
            elif method == td.method.number:
                vec, dur = tf.transform_time_at_the_number_of_unit(vector, duration, unit, value*direct)
                update_vectors(vec, dur, unit, overlap=True)


            # delta time
            elif method == td.method.delta:
                vec = tf.delta_time(curvector, unit, value*direct)
                update_vectors(vec, None, unit)

            else: assert False

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
        for i in xrange(len(time.datas)):
            u, v, d = time[i].unit, time[i].value, time[i].direct
            if u - int(u) > 0:
                v = tf.unit2unit(v, u, int(u+1))
                u = int(u+1)

            vector[u] = v if vector[u] == None else vector[u] + v
            if d != None and  d < 0: negtive = True

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

        start, dur = tf.shift_time(args.timecore.vector, t[0].unit, shift=t[0].direct)
        if t[0].direct < 0: start = tf.start_duration_to_end(start, dur) if dur != None else start


        '''
        if t[0].unit == td.unit.week or t[0].unit == td.unit.season:
            vec, dur = tf.shift_time(args.timecore.vector, t[0].unit, shift=t[0].direct)
            start = tf.start_duration_to_end(vec, dur) if t[0].direct < 0 else vec

        else:
            start = tf.keep_vector(args.timecore.vector, int(math.ceil(unit)))
            start = tf.delta_time(start, t[0].unit, t[0].direct)
        '''

        duration = self.duration.regularize(t, args)
        return VectorTime(t.sentence, t.pos_span, start=start, duration=duration)


class StartEndRegularization(GroupRegularization):

    def regularize(self, t, args):
        start = end = None

        if t.start == float('-inf'):
            end, duration = self.time.regularize(t.end, args)
            inf_unit = tf.accuracy(end)[-1]
            end = args.timecore.padding(end)
            start = args.infinity(t.start, end, inf_unit, args)
            if duration: end = tf.shift_time(end, duration)


        elif t.end == float('inf'):
            start, _ = self.time.regularize(t.start, args)
            inf_unit = tf.accuracy(start)[-1]
            start = args.timecore.padding(start)
            end = args.infinity(start, t.end, inf_unit, args)

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