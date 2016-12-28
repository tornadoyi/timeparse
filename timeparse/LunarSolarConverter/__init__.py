# -*- coding: utf-8 -*-
__author__ = 'isee15'

import LunarSolarConverter

converter = LunarSolarConverter.LunarSolarConverter()

def LunarToSolar(year, month, day, isleap = False):
    lunar = LunarSolarConverter.Lunar(year, month, day, isleap)
    solar = converter.LunarToSolar(lunar)
    return (solar.solarYear, solar.solarMonth, solar.solarDay)


def SolarToLunar(year, month, day):
    solar = LunarSolarConverter.Solar(year, month, day)
    lunar = converter.SolarToLunar(solar)
    return (lunar.lunarYear, lunar.lunarMonth, lunar.lunarDay)




def LunarMonthDays(year, month, isleap = False):
    converter = LunarSolarConverter.LunarSolarConverter
    days = converter.lunar_month_days[year - converter.lunar_month_days[0]]
    leap = LunarSolarConverter.GetBitInt(days, 4, 13)
    offset = 0
    loopend = leap
    if not isleap:

        if month <= leap or leap == 0:
            loopend = month - 1
        else:
            loopend = month

    days = LunarSolarConverter.GetBitInt(days, 1, 12 - loopend) == 1 and 30 or 29
    return days
