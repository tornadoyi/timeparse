import codecs
import os
import importlib
import copy
import time
from collections import namedtuple

from pyplus import *
from timeparse.ex_time import parse as time_parse
import command


class AutoTest(object):
    test_log = "logs/test.log"
    error_log = "logs/error.log"
    case_path = "autotest/cases"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '__instance'):
            orig = super(AutoTest, cls)
            cls.__instance = orig.__new__(cls, *args, **kwargs)
        return  cls.__instance


    def load_test_module(self, dir):
        modules = []
        # import
        module_root_path = dir.replace('/', '.')
        for dirpath, dirnames, filenames in os.walk("{0}".format(dir)):
            for filename in filenames:
                if filename.find('__init__') >= 0 or filename.find('pyc') >= 0: continue
                name = filename.split('.')[0]
                if len(name) == 0: continue
                module = importlib.import_module('{0}.{1}'.format(module_root_path, name))
                modules.append(module)
                #print(module.__name__.split('.')[-1])
        return modules

    def read_module_args(self, module):
        args = {}
        for arg_name in dir(module):
            if arg_name.find('arg_') < 0: continue
            v = getattr(module, arg_name)
            args[arg_name] = v
        return args

    def merge_args(self, args, arg_dict):
        args = copy.deepcopy(args)
        for (k, v) in arg_dict.items():
            name = k.replace('arg_', '')
            setattr(args, name, v)
        return args



    def test_time_case(self, recorder, args):

        modules = self.load_test_module(AutoTest.case_path)
        for module in modules:
            module_name = module.__name__.split('.')[-1]
            cases = getattr(module, 'cases')
            if cases == None: continue
            for idx in xrange(len(cases)):
                (question, answers) = cases[idx]
                times = time_parse(question, None, 0, len(question), command.args)
                checks = []
                for answer in answers: checks.append(answer(command.args))

                result = True
                if len(times) != len(checks):
                    result = False

                else:
                    for i in xrange(len(times)):
                        t, c = times[i], checks[i]
                        if  (t.start != c.start) or \
                            (t.end != c.end) or \
                            (t.duration != c.duration):
                            result = False

                tag = u"{0}-{1}".format(module_name, idx)
                recorder.add_case(tag=tag, question=question, bot_answers=times,
                                  expect_answers=checks, result=result)
                recorder.progress(module_name, idx + 1, len(cases))

                '''
                cur_timestamp = time.time()
                (ts_st, ts_ed, ts_delta) = timestamps != None and timestamps or (cur_timestamp, cur_timestamp + 1, 1)
                ts = ts_st - ts_delta
                while ts < ts_ed:
                    # delta
                    ts += ts_delta
                    if ts >= ts_ed: break

                    # set same timestamp
                    args.timecore.refresh_timestamp(ts)
                    test_timecore.refresh_timestamp(ts)

                    # parse
                    times = time_parse(sentence=question, splits=None, pos=0, endpos=len(question), args=args)
                    check_times = func(*parms, **kwparms)
                    if type(check_times) != tuple: check_times = [check_times]

                    # length check
                    result = True
                    if len(times) != len(check_times):
                        result = False

                    # time check
                    else:
                        for i in xrange(len(times)):
                            t = times[i]
                            ck_t = check_times[i]
                            if t.similar(ck_t): continue
                            result = False
                            break

                    tag = u"{0}-{1}".format(module_name, idx)
                    recorder.add_case(tag=tag, timestamp=ts, question=question, bot_answers=times, expect_answers=check_times, result=result)
                    recorder.progress(module_name, idx+1, len(cases))
                '''


