import argparse
import collections
import os
import re

import numpy as np
import matplotlib.pyplot as plt

PATTERNS = {
    'target': re.compile(r'^.*Moving to the ([-\d.]+) mark.*$'),
    'actual': re.compile(r'^.*at ([-\d.]+) mL mark.*$')
}

def filter_log(lines):
    positioning_lines = [line for line in lines
                         if re.match(PATTERNS['target'], line)]
    return positioning_lines

def split_log_by_target(lines):
    split_lines = collections.defaultdict(list)
    for line in lines:
        target = float(re.match(PATTERNS['target'], line).group(1))
        split_lines[target].append(line)
    return split_lines

def extract_actual(lines):
    actual_positions = []
    for line in lines:
        match = re.match(PATTERNS['actual'], line)
        if match:
            actual_positions.append(float(match.group(1)))
        else:
            print('Ignored on-matching line: {}'.format(line))
    return actual_positions

def plot_positioning_hist(target_position, actual_positions,
                          showfig=True, filename=None):
    plt.figure()
    weights = np.zeros(len(actual_positions)) + 1. / len(actual_positions)
    plt.axvline(x=target_position, color='red')
    plt.hist(actual_positions, weights=weights)
    plt.title('Pipettor PID positioning distribution with a target of {} mL mark'
              .format(target_position))
    plt.ylabel('Relative Frequency')
    plt.xlabel('Actual position from position sensor (mL mark)')
    if filename is not None:
        print('Saving plot as {}'.format(filename))
        plt.savefig(filename)
    if showfig:
        plt.show()
    plt.close()

def analyze(filename):
    with open(filename) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    positioning_lines = filter_log(lines)
    split_lines = split_log_by_target(positioning_lines)
    positioning_locations = {target: extract_actual(lines)
                             for (target, lines) in split_lines.items()}
    for (target, actual_positions) in positioning_locations.items():
        figname = os.path.splitext(filename)[0] + 'plot_{}mL'.format(target)
        plot_positioning_hist(target, actual_positions, filename=figname + '.pdf')
        plot_positioning_hist(target, actual_positions, filename=figname + '.png', showfig=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    analyze(args.filename)


if __name__ == '__main__':
    main()
