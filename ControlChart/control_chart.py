#!/usr/bin/env python
"""
Implement a time series control chart.

Copyright 2014 Daniel Couture (GNU GPLv3)

Usage:

    cat data | python{3} control_chart.py

Control Tests:

    [x] is < 3 sigma
    [x] is > 3 sigma
    [..] is 2/3 points > 2 sigma
    [..] is 2/3 points < 2 sigma
    [..] is 4/5 points > 1 sigma
    [..] is 4/5 points < 1 sigma
    [..] is 8/8 points > centerline
    [..] is 8/8 points < centerline

Centerline Shift Tests:

    [..] is 10/11 points > centerline
    [..] is 10/11 points < centerline
    [..] is 12/14 points > centerline
    [..] is 12/14 points < centerline
    [..] is 14/17 points > centerline
    [..] is 14/17 points < centerline
    [..] is 16/20 points > centerline
    [..] is 16/20 points < centerline

References:
    Implementing Six Sigma
    Smarter Solutions Using Statistical Methods
    Forrest W. Breyfogle III
    Second Edition, pp. 221
"""

import os
import sys
import numpy as np
from argparse import ArgumentParser


class Window(object):
    """
    Create a variable sized rolling window of data points.

    Usage::

        w = Window(4)
        for x in range(10):
            w.append(x)
        print("Rolling average for %s is %g" % (w, w.data.mean()))
        # Rolling average for [ 8.  9.  6.  7.] is 7.5

    :param n: size of the rolling window
    :type  n: int
    :param init: Initialize all entries to a value (np.nan by default)
    :type  init: numeric
    """
    def __init__(self, n, init=None):
        self.idx = 0
        self.n = n
        self.data = np.empty(n)
        if init is None:
            self.data.fill(np.nan)
        else:
            self.data.fill(init)

    def append(self, value):
        try:
            self.data[self.idx] = value
        except IndexError:
            self.idx = 0
            self.data[self.idx] = value
        self.idx += 1

    def __str__(self):
        return str(self.data)


def err_out(msg):
    """
    Helper function to write to stdout

    :param msg: message to write
    :type  msg: str
    """
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()


def test_3_sigma(options):
    """
    Create a test for a single value outside 3 standard deviations
    """
    lcl = options.m - 3 * options.s
    ucl = options.m + 3 * options.s

    def test(x):
        if x < lcl:
            err_out("%g is < 3 sigma" % x)
        elif x > ucl:
            err_out("%g is > 3 sigma" % x)
    return test


def test_2_sigma(options):
    """
    Create a test for 2 out of 3 values outside of 2 standard deviations
    """
    w = Window(3, init=options.m)
    lcl = options.m - 2 * options.s
    ucl = options.m + 2 * options.s

    def test(x):
        w.append(x)
        if np.sum(w.data > ucl) >= 2:
            err_out("%s is 2/3 points > 2 sigma" % w.data)
        elif np.sum(w.data < lcl) >= 2:
            err_out("%s is 2/3 points < 2 sigma" % w.data)
    return test


def test_1_sigma(options):
    """
    Create a test for 4 out of 5 values outside of 1 standard deviation
    """
    w = Window(5, init=options.m)
    lcl = options.m - 1 * options.s
    ucl = options.m + 1 * options.s

    def test(x):
        w.append(x)
        if np.sum(w.data > ucl) >= 4:
            err_out("%s is 4/5 points > 1 sigma" % w.data)
        elif np.sum(w.data < lcl) >= 4:
            err_out("%s is 4/5 points < 1 sigma" % w.data)
    return test


def test_cl_shift(options):
    """
    Create tests for centerline shifts

    8 out of 8 points are on one side of the mean
    >= 10 out of 11 points are on one side of the mean
    >= 12 out of 14 points are on one side of the mean
    >= 14 out of 17 points are on one side of the mean
    >= 16 out of 20 points are on one side of the mean
    """
    windows = [
        (8, Window(8, init=options.m)),
        (10, Window(11, init=options.m)),
        (12, Window(14, init=options.m)),
        (14, Window(17, init=options.m)),
        (16, Window(20, init=options.m)),
    ]
    cl = options.m

    def test(x):
        for n, w in windows:
            w.append(x)
            if np.sum(w.data > cl) >= n:
                err_out("%s is %g/%g points > centerline" %
                        (w.data, n, w.n))
            elif np.sum(w.data < cl) >= n:
                err_out("%s is %g/%g points < centerline" %
                        (w.data, n, w.n))
    return test


def control_chart(stream, options):
    """
    Run the control chart tests.  For each new value yielded by the stream,
    pass it to each of the tests for checking.

    :param stream: generator that yields the next value to test
    :type  stream: generator
    :param options: values for defining the tests (mean, standard deviation)
    :type  options: argparse.Namespace
    """
    tests = []
    tests.append(test_3_sigma(options))
    tests.append(test_2_sigma(options))
    tests.append(test_1_sigma(options))
    tests.append(test_cl_shift(options))

    for x in stream:
        for test in tests:
            test(x)
    return 0


def load_stream(input_stream):
    """
    Format the input stream to create numeric data points.

    :param input_stream: data generator.  Lines are excepted of str type
    :type  input_stream: generator (sys.stdin)
    """
    for line in input_stream:
        clean_line = line.strip()
        if not clean_line:
            # skip empty lines (ie: newlines)
            continue
        if clean_line[0] in ['"', "'"]:
            clean_line = clean_line.strip('"').strip("'")
        try:
            yield float(clean_line)
        except:
            err_out("invalid line %r" % line)


def parse_args():
    """
    Parse out testing arguments.
    """
    _, fname = os.path.split(__file__)
    usage = "cat data | python %s" % fname

    parser = ArgumentParser(usage=usage)
    parser.add_argument("-m", "--center", dest="m", required=True,
                        type=float, help="control chart centerline")
    parser.add_argument("-s", "--stdev", dest="s", required=True,
                        type=float, help="standard deviation")

    if sys.stdin.isatty():
        # if isatty() that means it's run without anything piped into it
        parser.print_usage()
        print("for more help use --help")
        sys.exit(1)
    return parser.parse_args()


def main():
    """
    Setup and run the tests from a stdin stream of data
    """
    options = parse_args()
    return control_chart(load_stream(sys.stdin), options)


if __name__ == "__main__":
    exit(main())
