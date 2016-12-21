#coding=utf-8

from ..command import *

cases = []

def add_case(sentence, *answers):
    cases.append((sentence, answers))


add_case(u"15年3月24日2点30分59秒", s_time([2015, 3, 24, 2, 30, 59]))