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