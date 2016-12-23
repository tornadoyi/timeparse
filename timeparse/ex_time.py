# -*- coding: utf-8 -*-
import re
import time
import sys
import math
import copy

import numpy as np
from pyplus import *

import time_define as td
import time_struct as ts
import time_re as tr
from time_func import *

import merge
from collector import Collector
import preference as prefer
from regularization import regularization as regular

reload(sys)
sys.setdefaultencoding('utf-8')




def parse(sentence, splits, pos, endpos, args):
    if args == None or args.timecore == None:
        raise Exception("extractor need timecore")

    # parse options
    args = parse_options(args)


    # split
    times = tr.parse(sentence, splits, pos, endpos, args)
    #print_times(times, "split")


    # merge cells
    times = merge.merge(times, args)
    #print_times(times, "merge")


    # regularization
    times = regular.regularize(times, args)
    #print_times(times, "regularization")


    return times




def parse_options(g_args):
    g_args = g_args or qdict()
    args = qdict()

    # collector
    args.collector = Collector()

    # timecore
    args.timecore = g_args.timecore

    # padding
    if g_args.padding == "history": args.padding = prefer.HistoryPadding()
    elif g_args.padding == "future": args.padding = prefer.FuturePadding()
    else: args.padding = prefer.RecentPadding()

    # fulltime
    args.fulltime = g_args.fulltime if g_args.fulltime != None else False

    # infinity
    args.infinity = prefer.Infinity(g_args.infinity if g_args.infinity != None else (0, 0, 0, 0, 0, 0))

    # ambiguous-direct
    args.ambiguous_direct = prefer.AmbiguousDirect(1 if args.ambiguous_direct == "future" else -1)

    return args






def print_times(times, title):
    print('============ {0} ============'.format(title))
    for t in times:
        print(t)
    print('=============================\n'.format(title))