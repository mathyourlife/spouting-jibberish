import sys
import matplotlib.pyplot as plt
import numpy as np

if sys.stdin.isatty():
    sys.stderr.write("usage: cat data.log | python %s\n" % __file__)
    exit(1)

x = np.array([float(line.strip()) for line in sys.stdin])

plt.hist(x, bins=30, normed=True, alpha=0.5)
plt.savefig("plot-in-py.png")
