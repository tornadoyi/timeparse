# -*- coding: utf-8 -*-
import sys
import re
import math
import copy

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
            func = self._process_front.get(front.__class__)
            if not func: break
            times = func(args, this, front)
            if times == command_keep_2: break
            elif isinstance(times, TimeCell): return (command.delete, times, command.keep)
            else: return (times[1], times[0], command.keep)

        while do_back and len(self._process_back) > 0:
            func = self._process_back.get(back.__class__)
            if not func: break
            times = func(args, this, back)
            if times == command_keep_2: break
            elif isinstance(times, TimeCell): return (command.keep, times, command.delete)
            else: return (command.keep, times[0], times[1])


        while do_both and len(self._process_both) > 0:
            func = self._process_both.get( (front.__class__, back.__class__) )
            if not func: break
            times = func(args, this, front, back)
            if times == None: break
            elif isinstance(times, TimeCell): return (command.delete, times, command.delete)
            else:
                return (times[1], times[0], times[2])

        return command_keep_3



    def concat_cell_info(self, *cells):
        min = sys.maxint
        max = -1
        for c in cells:
            min = np.min( (min, c.pos_span[0]) )
            max = np.max((max, c.pos_span[1]))
        return cells[0].sentence, min, max




class digit_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Unit, self.unit_process) # 3年

    def unit_process(self, args, this, other):
        if not this.adjacent(other): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        if this.quantity or other.value == td.unit.week:
           return  Duration(str, (st, ed), [this.value], [other.value])

        else:
            return Time(str, (st, ed),  [this.value], [other.value])



class direct_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Unit, self.unit_process) # 上 周
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
        direct = TimeDirect(this.relative, v / value if v != 0 else 0)
        return Time(str, (st, ed), [value], [other.value], [direct])

    def time_back_process(self, args, this, other): return self._convert(args, this, other, True)

    def time_front_process(self, args, this, other): return self._convert(args, this, other, False)

    def duration_back_process(self, args, this, other): return self._convert(args, this, other, True)

    def duration_front_process(self, args, this, other): return self._convert(args, this, other, False)


    def _convert(self, args, this, other, this_first):
        # check
        if not this.adjacent(other): return command_keep_2
        if other.directs[0] != None: return command_keep_2
        info = this.info_with_front if this_first else this.info_with_back
        if info == None: return command_keep_2

        # prepare
        str, st, ed = self.concat_cell_info(this, other)


        # 上周三
        if (other.__class__, other.units[0], other.directs[0]) == (Time, td.unit.week, None):
            directs = copy.deepcopy(other.directs)
            d = this.info_with_unit
            directs[0] = TimeDirect(this.relative, d)
            return Time(str, (st, ed), other.values, other.units, directs)

        # span
        elif type(info) == tuple:
            d_st, d_ed = info

            # all number then create time
            if float('-inf') < d_st and d_ed < float('inf'):
                directs = copy.deepcopy(other.directs)
                if d_st == 0: directs[0] = TimeDirect(this.relative, d_ed)
                elif d_ed == 0: directs[0] = TimeDirect(this.relative, d_st)
                else: assert False # todo

                # week check
                if this_first and other.__class__ == Time and td.unit.week in other.units:
                    return Time(str, (st, ed), other.values, other.units, directs)
                else:
                    return Duration(str, (st, ed), other.values, other.units, directs)


            # -inf ~ x
            elif d_st == float('-inf') and d_ed < float('inf'):
                start = d_st#Time("", (0, 0), [], [])
                end = copy.deepcopy(other)
                end.directs[0] = TimeDirect(this.relative, d_ed)
                return StartEnd(str, (st, ed), start, end)

            # x ~ inf
            elif d_st > float('-inf') and d_ed == float('inf'):
                end = d_ed#Time("", (0, 0), [], [])
                start = copy.deepcopy(other)
                start.directs[0] = TimeDirect(this.relative, d_st)
                return StartEnd(str, (st, ed), start, end)

            else: assert False

        # time
        else:
            directs = copy.deepcopy(other.directs)
            d = info
            directs[0] = TimeDirect(this.relative, d)
            return Time(str, (st, ed), other.values, other.units, directs)




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



class holiday_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Duration, self.duration_process)


    def duration_process(self, args, this, other):
        str, st, ed = self.concat_cell_info(this, other)

        # create startduration template
        template = this.to_start_duration()
        start = template.start
        duration = other

        # reverse duration direct
        direct = other.directs[0]
        if direct != None:# and direct.relative == 0:
            direct.value *= -1
            direct.relative = -1

        # back of days
        if direct != None and direct.value < 0:
            assert this.day > 0
            day_idx = start.unit_index(td.unit.day)
            start.values[day_idx] = this.day + this.duration - 1

        return StartDuration(str, (st, ed), start, duration)




class speical_hour_merger(merger):
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





class time_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Time, self.time_process) # 3月 4日
        self.add_back_process(Duration, self.duration_process) # 3月 前5天
        self.add_back_process(Digit, self.digit_process) # 8月15  l1 eat l0
        self.add_back_process(StartDuration, self.start_duration_process)  # 2016年 第一季度

    def time_process(self, args, this, other):
        if this.has_unit(other.units): return command_keep_2
        t = copy.deepcopy(this)
        t.merge(other)
        return t

    def duration_process(self, args, this, other):
        if this.has_unit(other.units): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        start = copy.deepcopy(this)
        duration = copy.deepcopy(other)
        direct = duration.directs[0]
        if direct != None:# and direct.relative == 0:
            direct.value *= -1
            direct.relative = -1

        return StartDuration(str, (st, ed), start=start, duration=duration)


    def digit_process(self, args, this, other):
        if not this.adjacent(other): return command_keep_2
        t = copy.deepcopy(this)
        if other.value == 0.5:
            t.values[-1] += other.value
        elif t.units[-1] < td.unit.second:
            t.add(other.value, t.units[-1]-1)
        else:
            return None

        str, st, ed = self.concat_cell_info(this, other)
        t.pos_span = (st, ed)
        return t


    def start_duration_process(self, args, this, other):
        if this.has_unit(other.start.units): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        start = copy.deepcopy(other.start)
        duration = copy.deepcopy(other.duration)
        start.merge(this)
        return StartDuration(str, (st, ed), start, duration)



class duration_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Duration, self.Duration_process) # 3个月零5天
        self.add_back_process(Time, self.Duration_process)  # 3个月零5天

    def Duration_process(self, args, this, other):
        if this.has_unit(other.units): return command_keep_2
        t = copy.deepcopy(this)
        t.merge(other)
        return t





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




class relation_start_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_both_process(Time, Duration, self.to_start_duration) #2015年 起 8个月
        self.add_both_process(Time, Time, self.to_start_duration)  # 5月 起 3天

    def to_start_duration(self, args, this, front, back):
        str, st, ed = self.concat_cell_info(this, front, back)
        return StartDuration(str, (st, ed), start=front, duration = back)





class start_duration_merger(merger):
    def __init__(self):
        merger.__init__(self)
        self.add_back_process(Time, self.expand_duration) # （5月前三天） 8小时
        self.add_back_process(Duration, self.reset_duration)  # （去年第一季度） 前三周

    def expand_duration(self, args, this, other):
        if not this.adjacent(other): return command_keep_2
        if this.duration.has_unit(other.units): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        t = copy.deepcopy(this)
        t.duration.merge(other)
        t.pos_span = (st, ed)
        return t

    def reset_duration(self, args, this, other):
        if not this.adjacent(other): return command_keep_2
        if this.duration.has_unit(other.units): return command_keep_2
        str, st, ed = self.concat_cell_info(this, other)
        start = copy.deepcopy(this.start)
        duration = copy.deepcopy(other)
        return StartDuration(str, (st, ed), start, duration)




class merge_manager():
    def __init__(self):
        self._map = {
            Digit: digit_merger(),
            Direct: direct_merger(),
            Calendar: calendar_merger(),
            Holiday: holiday_merger(),
            SpeicalHour: speical_hour_merger(),

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