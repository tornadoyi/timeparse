import argparse
from pyplus import *
from qa_bot.extractor.ex_time.time_func import TimeCore

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["test", "demo"], default = 'bot', help="choice command")

    parser.add_argument('--infinity', type=int, default=7, help="0: normal 1:clear context each step")
    parser.add_argument('--fulltime', type=str2bool, default=False)
    parser.add_argument('--padding', choices=['history', 'future', "recent"], type=str, default='recent')

    args = parser.parse_args()
    args = qdict(args)
    args.timecore = TimeCore()
    return args