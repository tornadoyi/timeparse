import copy
import math

import numpy as np

import time_define as td
from time_func import *
from time_struct import *

'''
def create_time_by_seed(v_seed, unit, value):
    units = values = None
    if unit == td.unit.week:
        values = weekday_vector(v_seed, value)
        values = keep_vector(values, unit, "cut")
        units = [i for i in xrange(td.unit.day+1)]


    else:
        units = []
        values = []
        for i in xrange(int(unit)):
            units.append(i)
            values.append(v_seed[i])

        units.append(unit)
        values.append(value)

    return (units, values)


def shift_time(v_seed, unit, shift):
    dt = vec2datetime(v_seed)
    value = get_datetime_unit(dt, unit)
    (units, values) = create_time_by_seed(v_seed, unit, value)

    # delta time
    vector = delta_time(v_seed, unit, shift)



def time2vector(time, end = None):
    end = end or len(time.datas)
    vector = time_vector()
    for i in xrange(end):
        d = time.datas[i]
        if d.unit - int(d.unit) > 0:
            low_unit = int(math.ceil(d.unit))
            unit_start = unit_min(d.unit)
            low_unit_start = unit_min(low_unit)
            delta = unit2unit(1, d.unit, low_unit)
            low_value = low_unit_start + delta * (d.value - unit_start)
            vector[low_unit] = low_value

        else:
            vector[d.unit] = d.value

    return vector

'''


def transform_time_by_modify_unit(v_seed, unit, value):
    vector = copy.deepcopy(v_seed)
    duration = None
    if unit == td.unit.week:
        v = weekday_vector(v_seed, value)
        vector[0:td.unit.day + 1] = v[0:td.unit.day + 1]

    elif unit == td.unit.quarter or unit == td.unit.season:
        low_unit = int(math.ceil(unit))
        unit_start = unit_min(unit)
        low_unit_start = unit_min(low_unit)
        delta = unit2unit(1, unit, low_unit)

        # vector
        low_value = low_unit_start + delta * (value - unit_start)
        vector[low_unit] = low_value

        # duration
        duration = time_vector()
        duration[low_unit] = delta

    else:
        vector[unit] = value

    # cut
    vector = keep_vector(vector, int(math.ceil(unit)))

    return vector, duration



# type: min max
def modify_time(v, unit, value, type = "min"):
    v, d = transform_time_by_modify_unit(v, unit, value)
    if d != None and type == "max":
        for i in xrange(d):
            if d[i] == None: continue
            v[i] += d[i] - 1

    return v



def transform_time_at_the_number_of_unit(v_seed, condition, unit, number):
    vector = duration = None


    if unit == td.unit.week:
        vector = start_time_at_week(vector[0], vector[1], number)
        duration = time_vector()
        duration[td.unit.day] = unit2unit(1, td.unit.week, td.unit.day)

    else:
        high_unit, reg_unit = int(unit-1), int(math.ceil(unit))
        vector, duration = transform_time_by_modify_unit(v_seed, unit, unit_min(unit))
        vector[reg_unit] = None

        if number < 0:
            for i in xrange(reg_unit+1):
                if v_seed[i] == None or condition[i] == None: continue
                vector[i] = v_seed[i] + condition[i] - 1

            vector = padding_max(vector, reg_unit)
            number += 1

        else:
            vector = padding_min(vector, reg_unit)
            number = np.max((number-1, 0))

        #number = number if number == 0 else number - 1 if number > 0 else number + 1
        vector = delta_time(vector, unit, number)

    return vector, duration





def shift_time(v_seed, unit, shift):
    # set start time by v
    dt = vec2datetime(v_seed)
    value = get_datetime_unit(dt, unit)
    vector, duration = transform_time_by_modify_unit(v_seed, unit, value)

    # delta time
    vector = delta_time(vector, unit, shift)
    return vector, duration




