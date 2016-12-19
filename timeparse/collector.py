# -*- coding: utf-8 -*-
import sys
import re
import math
import copy

import time_define as td
from time_struct import *

class Collector(object):
    def __init__(self):
        self._units = {}
        self._lunars = []
        self._special_hours = []


    def collect_special_hour(self, t): self._add_item(self._special_hours, t)

    def collect_unit_times(self, times):
        for t in times:
            # save time and lunar
            if t.__class__ == Time:
                self._add_time(t)
                if t.lunar: self._add_item(self._lunars, t)


    def find_nearest_unit(self, pos_span, unit):
        array = self._units.get(unit)
        if array == None: return None
        return self._find_nearest(array, pos_span)

    def find_nearest_lunar(self, pos_span): return self._find_nearest(self._lunars, pos_span)

    def find_nearest_special_hour(self, pos_span): return self._find_nearest(self._special_hours, pos_span)

    def _find_nearest(self, array, pos_span):
        distance = sys.maxint
        nearest = None
        for item in array:
            span = item.pos_span
            d = None
            if pos_span[0] <= span[0]:
                d = np.abs(pos_span[1] - span[0])
            else:
                d = np.abs(pos_span[0] - span[1])
            if d > distance: break
            d = distance
            nearest = item
        return nearest


    def _add_time(self, time):
        for i in xrange(len(time.units)):
            unit = time.units[i]
            array = self._units.get(unit)
            if array == None:
                array = []
                self._units[unit] = array
            self._add_item(array, time)



    def _add_item(self, array, item):
        for i in xrange(len(array)):
            if item.pos_span[0] >= array[i].pos_span[0]: continue
            array.insert(i, item)
            return
        array.append(item)



