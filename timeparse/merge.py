# -*- coding: utf-8 -*-
import sys
import re
import math
import copy

from pyplus import *
import time_define as td
from time_struct import *


class command():
    delete = -1
    keep = 0

command_keep_2 = (command.keep, command.keep)
command_keep_3 = (command.keep, command.keep, command.keep)

command_delete_self_2 = (command.delete, command.keep)
command_delete_self_3 = (command.delete, command.keep, command.keep)



class merger():
    def __init__(self):
        self._process_front = {}
        self._process_back = {}
        self._process_both = {}

    def add_front_process(self, t, func): self._process_front[t] = func

    def add_back_process(self, t, func): self._process_back[t] = func

    def add_both_process(self, tf, tb, func): self._process_both[(tf, tb)] = func

    def do(self, args, front, this, back, do_front, do_back, do_both):

        while do_front and len(self._process_front) > 0:
            times = self.do_front(args, this, front)
            if times == command_keep_2: break
            elif isinstance(times, TimeCell): return (command.delete, times, command.keep)
            else: return (times[1], times[0], command.keep)

        while do_back and len(self._process_back) > 0:
            times = self.do_back(args, this, back)
            if times == command_keep_2: break
            elif isinstance(times, TimeCell): return (command.keep, times, command.delete)
            else: return (command.keep, times[0], times[1])


        while do_both and len(self._process_both) > 0:
            times = self.do_both(args, this, front, back)
            if times == None: break
            elif isinstance(times, TimeCell): return (command.delete, times, command.delete)
            else:
                return (times[1], times[0], times[2])

        return command_keep_3


    def do_front(self, args, this, other):
        func = self._process_front.get(other.__class__)
        if not func: return command_keep_2
        return func(args, this, other)

    def do_back(self, args, this, other):
        func = self._process_back.get(other.__class__)
        if not func: return command_keep_2
        return func(args, this, other)

    def do_both(self, args, this, front, back):
        func = self._process_both.get((front.__class__, back.__class__))
        if not func: return command_keep_3
        return func(args, this, front, back)

    def concat_cell_info(self, *cells):
        min = sys.maxint
        max = -1
        for c in cells:
            min = np.min( (min, c.pos_span[0]) )
            max = np.max((max, c.pos_span[1]))
        return cells[0].sentence, min, max



@singleton
class digit_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Unit, self.unit_process) # 3年
        self.add_front_process(Time, self.time_process)  # 3年

    def unit_process(self, args, this, other):
        if not this.adjacent(other): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        if this.quantity or other.value == td.unit.week:
           return  Duration(str, (st, ed), UD(other.value, this.value))

        else:
            return Time(str, (st, ed), UD(other.value, this.value))


    def time_process(self, args, this, other):
        if not this.adjacent(other): return command_keep_2
        if other[-1].method != td.method.none: return command_keep_2

        t = copy.deepcopy(other)
        if this.value == 0.5:
            if t[-1].unit != td.unit.hour: return command_keep_2
            t[-1].value += this.value

        else:
            t.add(UD(t[-1].unit+1, this.value))

        str, st, ed = self.concat_cell_info(this, other)
        t.pos_span = (st, ed)
        return t



@singleton
class direct_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Unit, self.unit_process) # 上 周
        self.add_back_process(SpecialHour, self.special_hour_process) # 昨 晚 / 今早

        self.add_back_process(Time, self.time_back_process) # 前 三周 / 上 周三
        self.add_front_process(Time, self.time_front_process)  # 三周前 / 周三前
        self.add_back_process(Duration, self.duration_back_process) # 前 三个月
        self.add_front_process(Duration, self.duration_front_process)  # 三个月 前


    def unit_process(self, args, this, other):
        # check
        if not this.adjacent(other): return command_keep_2
        if this.info_with_unit == None: return command_keep_2

        # concat
        v = this.info_with_unit
        str, st, ed = self.concat_cell_info(this, other)
        value = np.abs(v)
        return Time(str, (st, ed), UD(other.value, value, method=td.method.shift, direct=v / value if v != 0 else 0))



    def special_hour_process(self, args, this, other):
        unit = Unit(other.sentence, other.pos_span, td.unit.day)
        t = self.unit_process(args, this, unit)
        if t == None: return command_keep_2

        # save to collector
        args.collector.collect_special_hour(other)
        return t


    def time_back_process(self, args, this, other): return self._convert(args, this, other, True)

    def time_front_process(self, args, this, other): return self._convert(args, this, other, False)

    def duration_back_process(self, args, this, other): return self._convert(args, this, other, True)

    def duration_front_process(self, args, this, other): return self._convert(args, this, other, False)


    def _convert(self, args, this, other, this_first):
        def relative2method(r):
            if r == td.relative.parent:
                return td.method.number
            elif r == td.relative.now:
                return td.method.shift
            else:
                return td.method.none

        # check
        if not this.adjacent(other): return command_keep_2
        if other[0].method != td.method.none: return command_keep_2
        info = this.info_with_front if this_first else this.info_with_back
        if info == None: return command_keep_2

        # prepare
        str, st, ed = self.concat_cell_info(this, other)
        other = copy.deepcopy(other)

        # 上周三
        if (other.__class__, other[0].unit, other[0].weekday) == (Time, td.unit.week, True):
            other[0].method = td.method.shift
            other[0].direct = this.info_with_unit
            return Time(str, (st, ed), other.datas)

        # span
        elif type(info) == tuple:
            d_st, d_ed = info

            # all number then create time
            if float('-inf') < d_st and d_ed < float('inf'):
                if d_st == 0:
                    other[0].method = relative2method(this.relative)
                    other[0].direct = d_ed

                elif d_ed == 0:
                    other[0].method = relative2method(this.relative)
                    other[0].direct = d_st

                else:
                    other[0].method = relative2method(this.relative)
                    other[0].direct = args.ambiguous_direct(d_st, d_ed)

                # week check
                return Duration(str, (st, ed), other.datas)


            # -inf ~ x
            elif d_st == float('-inf') and d_ed < float('inf'):
                start = d_st
                other[0].method = td.method.delta
                other[0].direct = d_ed
                return StartEnd(str, (st, ed), start, other)

            # x ~ inf
            elif d_st > float('-inf') and d_ed == float('inf'):
                end = d_ed
                other[0].method = td.method.delta
                other[0].direct = d_st
                return StartEnd(str, (st, ed), other, end)

            else: assert False

        # time
        else:
            d = info
            other[0].method = relative2method(this.relative)
            other[0].direct = d
            return Time(str, (st, ed), other.datas)



@singleton
class calendar_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Time, self.process)
        self.add_back_process(Time, self.process)

    def process(self, args, this, other):
        str, st, ed = self.concat_cell_info(this, other)
        t = copy.deepcopy(other)
        t.lunar = this.lunar
        t.pos_span = (st, ed)
        return t



@singleton
class holiday_merger(merger):
    def __init__(self):
        merger.__init__(self)

        self.add_back_process(Duration, self.duration_process) # 国庆 后三天
        self.add_back_process(Time, self.time_process)  # 国庆 倒数第三天



    def duration_process(self, args, this, other):
        if other[0].unit < td.unit.day: return command_keep_2

        str, st, ed = self.concat_cell_info(this, other)
        duration = copy.deepcopy(other)

        # gen duration
        if duration[0].method != td.method.none:
            duration[0].direct *= -1
            duration[0].method = td.method.number

        # gen start
        rel_dir = qdict(direct=-1, method=td.method.number) if this.day < 0 else {}
        year = [this.year] if this.year != None else []
        if duration[0].direct >= 0:
            start = Time(this.sentence, this.pos_span, year + [UD(td.unit.month, this.month), UD(td.unit.day, this.day, **rel_dir)], this.lunar)
        else:
            start = Time(this.sentence, this.pos_span, year + [UD(td.unit.month, this.month), UD(td.unit.day, this.day+this.duration-1, **rel_dir)], this.lunar)

        return StartDuration(str, (st, ed), start, duration)


    def time_process(self, args, this, other):
        if other[0].unit < td.unit.day : return command_keep_2

        str, st, ed = self.concat_cell_info(this, other)
        other = copy.deepcopy(other)

        day_idx = other.unit_index(td.unit.day)
        if day_idx != None and other.directs[day_idx].value < 0:
            assert this.day > 0
            end_day = this.day + this.duration - 1
            delta = other[day_idx].direct * other[day_idx].value
            other[day_idx].value = end_day + delta
            other[day_idx].direct = td.method.none

        rel_dir = qdict(direct=-1, method=td.method.number) if this.day < 0 else {}
        start = Time(this.sentence, this.pos_span, UD(td.unit.month, this.month, **rel_dir), this.lunar)
        start.add(other.datas)

        return start


@singleton
class special_hour_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Time, self.time_process)  # 下午 8点
        self.add_front_process(Time, self.time_process)  # 8点 下午的


    def time_process(self, args, this, other):
        if not other.has_unit(td.unit.hour): return command_keep_2

        # save to collector
        args.collector.collect_special_hour(this)

        # delete self
        return command_delete_self_2




@singleton
class time_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Time, self.time_process) # 3月 4日 / 3月 倒数第二天
        self.add_back_process(Duration, self.duration_process) # 3月 前5天

        self.add_back_process(Holiday, self.add_holiday_year)  # 去年 国庆

    def time_process(self, args, this, other):
        if this.has_unit(other.units): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        t = copy.deepcopy(this)
        t.add(other.datas)
        if other.lunar: t.lunar = other.lunar
        t.pos_span = (st, ed)
        return t


    def duration_process(self, args, this, other):
        if this.has_unit(other.units): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        start = copy.deepcopy(this)
        duration = copy.deepcopy(other)
        duration[0].direct *= -1
        duration[0].method = td.method.number

        return StartDuration(str, (st, ed), start=start, duration=duration)



    def add_holiday_year(self, args, this, other):
        if len(this.datas) > 1: return command_keep_2
        if this.datas[0].unit != td.unit.year: return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)

        holiday = copy.deepcopy(other)
        holiday.year = copy.deepcopy(this.datas[0])
        holiday.pos_span = (st, ed)
        return holiday





@singleton
class duration_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Duration, self.duration_process) # 3个月 零2个小时
        self.add_back_process(Time, self.duration_process)  # 3个月 零5天

    def duration_process(self, args, this, other):
        if this.has_unit(other.units): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        t = copy.deepcopy(this)
        t.add(other.datas)
        if other[0].direct != td.method.none:
            other[0].direct *= -1
            other[0].method = td.method.number

        t.pos_span = (st, ed)
        return t




@singleton
class relation_span_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_both_process(Time, Time, self.time_process) # 3月 到 5月
        self.add_both_process(StartEnd, Time, self.expand_start_end)  # （3月到5月）到 7月

    def time_process(self, args, this, front, back):
        str, st, ed = self.concat_cell_info(this, front, back)
        return StartEnd(str, (st, ed), start=front, end = back)

    def expand_start_end(self, args, this, front, back):
        str, st, ed = self.concat_cell_info(this, front, back)
        return StartEnd(str, (st, ed), start=front.start, end = back)



@singleton
class relation_start_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_both_process(Time, Duration, self.to_start_duration) #2015年 起 8个月
        self.add_both_process(Time, Time, self.to_start_duration)  # 5月 起 3天

    def to_start_duration(self, args, this, front, back):
        str, st, ed = self.concat_cell_info(this, front, back)
        duration = back if type(back) == Duration else Duration(back.sentence, back.pos_span, back.datas)
        return StartDuration(str, (st, ed), start=front, duration = duration)




@singleton
class start_duration_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Time, self.expand_duration) # （5月前三天） 零8小时

    def expand_duration(self, args, this, other):
        # merge duration
        duration = duration_merger().do_back(args, this.duration, other)
        if not isinstance(duration, Duration): return command_keep_2

        str, st, ed = self.concat_cell_info(this, other)
        return StartDuration(str, (st, ed), start=copy.deepcopy(this.start), duration=duration)




@singleton
class merge_manager():
    def __init__(self):
        self._map = {
            Digit: digit_merger(),
            Direct: direct_merger(),
            Calendar: calendar_merger(),
            Holiday: holiday_merger(),
            SpecialHour: special_hour_merger(),

            Time: time_merger(),
            Duration: duration_merger(),


            Relation_Span: relation_span_merger(),
            Relation_Start: relation_start_merger(),

            StartDuration: start_duration_merger(),
        }


    def merge(self, times, args, start_level = 0):

        if start_level <= 0:
            times = self.do_level(times, args, run_func = lambda l: l == TimeCell.time_level)
            times = self.do_level(times, args, upgrade = lambda l: l == TimeCell.time_level)
            self.print_times(times, 'merge cells to chunk')

            # collect unit times
            args.collector.collect_unit_times(times)

        if start_level <= 1:
            times = self.do_level(times, args, run_func = lambda l: l <= TimeChunk.time_level)
            times = self.do_level(times, args, upgrade = lambda l: l == TimeChunk.time_level)
            times = self.do_level(times, args, clear_unused = lambda l: l == TimeCell.time_level or l == TimeChunk.time_level)
            self.print_times(times, 'merge chunks to group')


        if start_level <= 2:
            times = self.do_level(times, args, run_func = lambda l: l <= TimeGroup.time_level or l == Relation.time_level)
            times = self.do_level(times, args, clear_unused = lambda l: l < TimeGroup.time_level or l == Relation.time_level)
            self.print_times(times, 'deal level 2')

        return times


    def do_level(self, cells, args, run_func=None, upgrade=None, clear_unused=None):
        if run_func != None:
            while self.do_step(cells, args, run_func, do_back=True, do_both=True): continue  # self.print_times(cells, "step");
            while self.do_step(cells, args, run_func, do_front=True): continue

        # upgrade
        if upgrade != None:
            for i in xrange(len(cells)):
                cell = cells[i]
                if not upgrade(cell.level): continue
                new_cell = cell.upgrade()
                if new_cell != None: cells[i] = new_cell

        # clear unused level cells
        if clear_unused != None:
            for i in xrange(len(cells) - 1, -1, -1):
                cell = cells[i]
                if not clear_unused(cell.level): continue
                del cells[i]

        return cells


    def do_step(self, cells, args,  run_func, do_front=False, do_back=False, do_both=False):
        act = False
        i = 0
        while i < len(cells):
            # input
            front = None if i == 0 else cells[i - 1]
            current = cells[i]
            back = None if i >= len(cells) - 1 else cells[i + 1]

            # check level
            if not run_func(current.level): i += 1; continue

            # find merger
            merger = self._map.get(current.__class__)
            if merger == None: i += 1; continue

            # do
            res = merger.do(args, front, current, back, do_front, do_back, do_both)
            if res == command_keep_3: i += 1; continue

            # clear deleted cell
            k = i - 1
            next = k
            for cmd in res:
                if cmd == command.keep:
                    k += 1
                elif cmd == command.delete:
                    del cells[k]
                else:
                    cells[k] = cmd
                    next = k
                    k += 1

            i = np.max((0, next))
            act = True

        return act



    def print_times(self, times, title):
        #return
        print('------------ {0} -------------'.format(title))
        for t in times:
            print(t)
        print('------------------------------\n'.format(title))


merge = merge_manager().merge