import copy
import math

import numpy as np

import time_define as td
from time_func import *
from time_struct import *



def transform_time_by_modify_unit(v_seed, unit, value):
    vector = copy.deepcopy(v_seed)
    duration = None
    if unit == td.unit.week:
        v = weekday_vector(v_seed, value)
        vector[0:td.unit.day + 1] = v[0:td.unit.day + 1]

    elif unit == td.unit.season:
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

    elif unit == td.unit.quarter:
        vector[td.unit.minute] = unit2unit(value, unit, td.unit.minute)

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
        vector = start_time_at_week(v_seed[0], v_seed[1], number)
        duration = time_vector()
        duration[td.unit.day] = unit2unit(1, td.unit.week, td.unit.day)

    else:
        high_unit, reg_unit = int(unit-1), int(math.ceil(unit))
        vector, duration = transform_time_by_modify_unit(v_seed, unit, unit_min(unit))
        vector[reg_unit] = v_seed[reg_unit]

        if number < 0:
            for i in xrange(reg_unit+1):
                if v_seed[i] == None or condition[i] == None: continue
                vector[i] = v_seed[i] + condition[i] - 1

            vector = padding_max(vector, reg_unit)
            number += 1

        else:
            vector = padding_min(vector, reg_unit)
            number = np.max((number-1, 0))

        vector = delta_time(vector, unit, number)

    return vector, duration




def shift_time(v_seed, unit, shift, weekday = None):
    # set start time by v_seed
    vector = duration = None

    # weekday
    if unit == td.unit.week:
        if weekday != None:
            vector, _ = transform_time_by_modify_unit(v_seed, unit, weekday)
        else:
            vector, _ = transform_time_by_modify_unit(v_seed, unit, 1)
            duration = time_vector()
            duration[td.unit.day] = unit2unit(1, unit, td.unit.day)

    else:
        dt = vec2datetime(v_seed)
        value = get_datetime_unit(dt, unit)
        vector, duration = transform_time_by_modify_unit(v_seed, unit, value)

    # delta
    vector = delta_time(vector, unit, shift)

    return vector, duration





def start_duration_to_end(start, duration):
    sum = 0
    negtive = False
    for i in xrange(len(duration)):
        v = duration[i]
        if v == None: continue
        sum += unit2unit(math.fabs(v), i, td.unit.second)
        if v < 0: negtive = True

    if negtive: sum = -sum
    sum = sum if sum == 0 else sum - 1 if sum > 0 else sum + 1
    vector = delta_time(start, td.unit.second, sum)

    return vector