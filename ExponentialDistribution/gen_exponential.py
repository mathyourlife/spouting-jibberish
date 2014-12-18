import numpy as np
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-l','--lambda',dest='lam',type=float)
parser.add_argument('-n','--count',dest='count',type=int)
args = parser.parse_args()

def exponential_distribution(lam, count):
    for _ in range(count):
        print(np.log(1 - np.random.rand()) / (-lam))

exponential_distribution(args.lam, args.count)
exit(0)
