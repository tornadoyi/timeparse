#coding=utf-8

from ..command import *

cases = []

def add_case(sentence, *answers):
    cases.append((sentence, answers))

# ==================================== init args ==================================== #
args.infinity = (0, 0, 0, 0, 0, 0)
args.fulltime = False
args.padding = "recent"


# ==================================== merge condition ==================================== #

# digit
add_case(u"15年3月24日2点30分59秒", s_time([2015, 3, 24, 2, 30, 59]))

# digit-no unit
#add_case(u"2016大年初3", s_time([l2s([2016, 1, 3])]))


# direct
add_case(u"大后天", s_time([s_day(3)]))
add_case(u"大前年", s_time([s_year(-3)]))
add_case(u"上周", sd_time([s_week_st(-1)], vector(day=7) ))
add_case(u"下月", s_time([s_month(1)]))
add_case(u"后一个季度", sd_time([s_season_st(1)], vector(month=3) ))
add_case(u"上季度", sd_time([s_season_st(-1)], vector(month=3) ))
add_case(u"前一个季度", sd_time([s_season_ed(-1)], vector(month=-3) ))
add_case(u"前三周", sd_time([s_week_ed(-1)], vector(day=-21) ))
add_case(u"上周三", s_time([s_weekday(3, -1)]))
add_case(u"3周前", se_time([d_time(d_week(-3), day, -args.infinity[day])], [d_week(-3)]))
add_case(u"2季度后", se_time([d_time(d_season(2), day, args.infinity[month])], [d_season(2)]))
add_case(u"前3分钟", sd_time([s_minute(-1)], vector(minute=-3) ))
add_case(u"前3个小时", sd_time([s_hour(-1)], vector(hour=-3) ))
add_case(u"后3个月2天", sd_time([s_month(1)], vector(month=3, day=2) ))

#add_case(u"周三前", s_time([s_weekday(3, -1)]))


# solar
add_case(u"阴历2016年1月1日", s_time([l2s([2016, 1, 1])]))
add_case(u"2016年大年初3", s_time([l2s([2016, 1, 3])]))
add_case(u"2016年大年初3", s_time([l2s([2016, 1, 3])]))
add_case(u"2016年大年三十", sd_time([l2s([2016, 12, 30])], vector(day=1)))



# holiday
add_case(u"今年国庆前三天", sd_time([s_year(0), 10, 1], vector(day=3)) )