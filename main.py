#coding=utf-8

import sys
import option

from timeparse.ex_time import parse as time_parse


def demo(args):
    cases = [

        u"5月前三天",
        u"三天后",
        u"昨天2点30分",
        u"2点半持续2小时",
        u"昨天5点到7点 8点到10点",
        u"昨天5点到7点再到10点",
        u"去年前9个月零7天",
        u"去年三月到五月6号",
        u"昨天五点半到后天10点",
        u"昨天五点一刻和下周三8点7分",
        u"明年的昨天",
        u"下下周三",
        u"大大大前天",
        u"上上个月5号",
        u"本月第一周第3天第5个小时第6分钟第8秒",
        u"中秋节的数据额",
        u"后天夜里11点",
        u"后天晚上2点",
        u"国庆节前三天的数据",
        u"国庆节后三天的数据",
        u"正月的数据额",
        u"明天开始我要请三天假",
        u"上上周",
        u"上周2",
        u"上上周2",

        u"阳历2016年第一季度",
        u"去年第一季度",
    ]

    special_case = [
        u"大年三十",
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


