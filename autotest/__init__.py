
from autotest import AutoTest
from recorder import Recorder

autotest = AutoTest()

def test(args):
    print("start test ...")
    recorder = Recorder(args)
    autotest.test_time_case(recorder, args)
    recorder.output(AutoTest.error_log, -1)

    print("test finish, cases: {0} errors: {1} accuracy: {2}%".format(
        recorder.case_count, recorder.failed_count, recorder.accuracy * 100.0))