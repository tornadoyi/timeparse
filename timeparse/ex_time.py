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
    options = g_args.options or qdict()
    args = qdict()

    # collector
    args.collector = Collector()

    # timecore
    args.timecore = g_args.timecore

    # padding
    if options.padding == "history": args.padding = prefer.HistoryPadding()
    elif options.padding == "future": args.padding = prefer.FuturePadding()
    else: args.padding = prefer.RecentPadding()

    # fulltime
    args.fulltime = options.fulltime if options.fulltime != None else False

    # infinity
    args.infinity = prefer.Infinity(options.infinity if options.infinity != None else 0)

    return args






def print_times(times, title):
    print('============ {0} ============'.format(title))
    for t in times:
        print(t)
    print('=============================\n'.format(title))