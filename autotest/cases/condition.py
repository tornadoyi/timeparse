#coding=utf-8

from ..command import *

cases = []

def add_case(sentence, *answers):
    cases.append((sentence, answers))

# ==================================== init args ==================================== #
args.infinity = (0, 0, 0, 0, 0, 0)
args.fulltime = False
args.padding = "recent"
args.ambiguous_direct = "history"


# ==================================== merge condition ==================================== #

# digit
add_case(u"15年3月24日2点30分59秒", s_time([2015, 3, 24, 2, 30, 59]))
add_case(u"今年8月15", s_time([s_year(0), 8, 15]) )
add_case(u"今天3点一刻", s_time([s_day(0), 3, 15]) )

# digit-no unit
#add_case(u"2016大年初3", s_time([l2s([2016, 1, 3])]))


# direct
add_case(u"大后天", s_time([s_day(3)]))
add_case(u"大前年", s_time([s_year(-3)]))
add_case(u"大大大前天", s_time([s_day(-5)]))
add_case(u"上周", sd_time([s_week_st(-1)], vector(day=7) ))
add_case(u"下下周三", s_time([s_weekday(3, 2)]))
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
add_case(u"去年第一季度", sd_time([s_year(-1), 1], vector(month=3) ))
add_case(u"明年的昨天", s_time([s_year(1), None, s_day(-1)]))
add_case(u"3天内", sd_time([s_day(-1)], vector(day=-3)))

#add_case(u"周三前", s_time([s_weekday(3, -1)]))


# lunar
add_case(u"阴历2016年1月1日", s_time([l2s([2016, 1, 1])]))
add_case(u"2016年大年初3", s_time([l2s([2016, 1, 3])]))
add_case(u"2016年大年初3", s_time([l2s([2016, 1, 3])]))
add_case(u"2016年大年三十", sd_time([l2s([2016, 12, 30])], vector(day=1)))



# holiday
add_case(u"今年国庆前三天", sd_time([s_year(0), 10, 1], vector(day=3)) )
add_case(u"今年国庆后三天", sd_time([s_year(0), 10, 7], vector(day=-3)) )
add_case(u"今年圣诞节", sd_time([s_year(0), 12, 25], vector(day=1)) )

add_case(u"今年正月的数据额", s_time(keep(l2s([s_year(0), 1, 1]), month)))

#add_case(u"今年过年", sd_time([l2s([s_year(1), 1, 1])], vector(day=7)) )


# special hour
add_case(u"今天下午3点", s_time([s_day(0), 15]) )
add_case(u"明天早上6点", s_time([s_day(1), 6]) )
add_case(u"昨天中午11点", s_time([s_day(-1), 11]) )
add_case(u"昨天中午1点", s_time([s_day(-1), 13]) )
add_case(u"昨天晚上11点", s_time([s_day(-1), 23]) )
add_case(u"昨晚1点", s_time([s_day(0), 1]) )
add_case(u"后天夜里11点", s_time([s_day(2), 23]) )



# time
add_case(u"今年3月倒数第二天", s_time([s_year(0), 3, 30]) )
add_case(u"今年3月前三天", sd_time([s_year(0), 3, 1], vector(day=3) ) )
add_case(u"去年中秋", sd_time([l2s([s_year(-1), 8, 15])], vector(day=3)) )
add_case(u"今天3点后5分钟", sd_time([s_day(0), 3, 59], vector(minute=-5) ) )
add_case(u"昨天2点30分", s_time([s_day(-1), 2, 30]))
add_case(u"今天下午2点半持续2小时", sd_time([s_day(0), 14, 30], vector(hour=2) ))
add_case(u"去年前9个月零7天", sd_time([s_year(-1), 1], vector(month=9, day=7) ))
add_case(u"上上个月5号", s_time([s_month(-2), 5]))
#add_case(u"本月第一周第3天第5个小时第6分钟第8秒", s_time([s_month(0), ]))




# duration
add_case(u"今年前3月零2天", sd_time([s_year(0), 1], vector(month=3, day=2) ) )
add_case(u"上季度第3天", s_time([s_season_st(-1), 3] ) )
add_case(u"16年3季度第二个月", s_time([2016, 8]) )
add_case(u"3天后", se_time([d_day(3)], [d_time(d_day(3), day, args.infinity[day])] ))



# span
add_case(u"昨天5点到7点 8点到10点", se_time([s_day(-1), 5], [s_day(-1), 7]), se_time([s_day(-1), 8], [s_day(-1), 10]) )
add_case(u"昨天5点到7点再到10点", se_time([s_day(-1), 5], [s_day(-1), 10]) )
add_case(u"昨天五点半到后天10点", se_time([s_day(-1), 5, 30], [s_day(2), 10]) )
add_case(u"昨天五点一刻和下周三8点7分", s_time([s_day(-1), 5, 15]), s_time([s_weekday(3, 1), 8, 7]) )
add_case(u"明天开始我要请三天假", sd_time([s_day(1)], vector(day=3)))
add_case(u"去年三月到五月6号", se_time([s_year(-1), 3], [s_year(-1), 5, 6]) )
