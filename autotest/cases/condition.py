#coding=utf-8

from ..command import *

cases = []

def add_case(sentence, *answers):
    cases.append((sentence, answers))

# ==================================== init args ==================================== #
args.infiity = 7
args.fulltime = False
args.padding = "recent"


# ==================================== merge condition ==================================== #

# digit
add_case(u"15年3月24日2点30分59秒", s_time([2015, 3, 24, 2, 30, 59]))


# direct
add_case(u"大后天", s_time([s_day(3)]))
add_case(u"上周", sd_time([s_week_st(-1)], [None, None, 7]))
add_case(u"前三周", sd_time([s_week_ed(-1)], [None, None, -21]))
add_case(u"上周三", s_time([s_weekday(3, -1)]))

#add_case(u"上周前", s_time([s_weekday(3, -1)]))