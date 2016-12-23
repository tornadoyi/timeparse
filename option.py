import argparse
from pyplus import *
from timeparse.time_func import TimeCore

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def parse_vector(v):
    splits = v.split("-")
    v = [None] * 6
    for i in xrange(len(splits)):
        v[i] = int(splits[i])
    return v

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["test", "demo"], default = 'bot', help="choice command")

    parser.add_argument('--infinity', type=parse_vector, help="set infinit value for each unit")
    parser.add_argument('--fulltime', type=str2bool, default=False)
    parser.add_argument('--padding', choices=['history', 'future', "recent"], type=str, default='recent')
    parser.add_argument('--ambiguous-direct', choices=['history', 'future'], type=str, default='history')

    args = parser.parse_args()
    args = qdict(args)
    args.timecore = TimeCore()
    return args