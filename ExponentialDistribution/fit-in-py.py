import sys
from scipy.stats import expon
import numpy as np

if sys.stdin.isatty():
    sys.stderr.write("usage: cat data.log | python %s\n" % __file__)
    exit(1)

x = np.array([float(line.strip()) for line in sys.stdin])

# shape, loc, scale
loc, scale = expon.fit(x, floc=0)
print("lambda")
print(1./scale)
# 0.278487310799 3.59082788057
