import copy
import math

import time_define as td
import time_func as tf
from time_struct import *






def transform_vector_by_modify_unit(v_seed, unit, value):
    vector = copy.deepcopy(v_seed)
    duration = None
    if unit == td.unit.week:
        v = tf.weekday_vector(v_seed, value)
        vector[0:td.unit.day + 1] = v[0:td.unit.day + 1]

    elif unit == td.unit.quarter or unit == td.unit.season:
        (min, max) = tf.unit_range(unit)
        tgt_unit = int(math.ceil(unit))
        delta = tf.unit2unit(1, unit, tgt_unit)

        # vector
        v0 = min if min == 0 else min - delta
        vector[tgt_unit] = v0 + delta * value

        # duration
        duration = tf.time_vector()
        duration[tgt_unit] = delta

    else:
        vector[unit] = value

    # cut
    vector = tf.keep_vector(vector, unit)

    return vector, duration




def transform_vector_at_the_number_of_unit(v_seed, unit, number):
    vector = duration = None


    if unit == td.unit.week:
        vector = tf.start_time_at_week(vector[0], vector[1], number)
        duration = tf.time_vector()
        duration[td.unit.day] = tf.unit2unit(1, td.unit.week, td.unit.day)

    else:
        transform_vector_by_modify_unit(v_seed, unit, )



# type: min max
def modify_vector(v, unit, value, type = "min"):
    v, d = transform_vector_by_modify_unit(v, unit, value)
    if d != None and type == "max":
        for i in xrange(d):
            if d[i] == None: continue
            v[i] += d[i] - 1

    return v



def shift_vector(v, unit, shift):
    # set start time by v
    dt = tf.vec2datetime(v)
    value = tf.get_datetime_unit(dt, unit)
    vector, duration = transform_vector_by_modify_unit(v, unit, value)

    # delta time
    vector = tf.delta_time(v, unit, shift)
    return v, duration




