#coding=utf-8

import sys
import option

from timeparse.ex_time import parse as time_parse


def demo(args):

    special_case = [
        u"5月份和这个月起安卓xiaomi的消消乐的dau和dnu呢",
    ]

    for case in special_case:
        print(case)
        times = time_parse(sentence=case, splits=None, pos=0, endpos=len(case), args=args)
        for t in times: print(t)
        print("")



def test(args):
    import autotest
    autotest.test(args)



if __name__ == '__main__':
    # parse args
    args = option.parse()

    if args.command == 'demo':
        demo(args)
    elif args.command == 'test':
        test(args)
    else:
        print("invalid command")


