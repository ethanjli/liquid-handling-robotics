import argparse
import collections
import os
import re

import numpy as np
import matplotlib.pyplot as plt

PATTERNS = {
    'target': re.compile(r'^.*Moving to the ([-\d.]+) mark.*$'),
    'actual': re.compile(r'^.*at ([-\d.]+) mL mark.*$'),
    'converged': re.compile(r'^.*Converged at ([-\d.]+) mL mark.*$'),
    'stalled': re.compile(r'^.*Stalled at ([-\d.]+) mL mark.*$'),
}

def filter(lines):
    positioning_lines = [line for line in lines
                         if re.match(PATTERNS['target'], line)]
    return positioning_lines

def split_log_by_target(lines):
    split_lines = collections.defaultdict(list)
    for line in lines:
        target = float(re.match(PATTERNS['target'], line).group(1))
        split_lines[target].append(line)
    return split_lines

def extract(lines, pattern_name='actual', warn=True):
    actual_positions = []
    for line in lines:
        match = re.match(PATTERNS[pattern_name], line)
        if match:
            actual_positions.append(float(match.group(1)))
        elif warn:
            print('Ignored on-matching line: {}'.format(line))
    return actual_positions

def plot_positioning_hist(target_position, actual_positions, figtitle,
                          showfig=True, filename=None, formats=['pdf', 'png']):
    plt.figure()
    if isinstance(actual_positions, dict):
        num_total_items = sum(len(series) for series in actual_positions.values())
        for (name, series) in actual_positions.items():
            weights = np.zeros(len(series)) + 1. / num_total_items
            plt.hist(series, weights=weights, alpha=0.5, label=name)
        plt.legend()
    else:
        num_items = len(actual_positions)
        weights = np.zeros(num_items) + 1. / num_items
        plt.hist(actual_positions, weights=weights)
    plt.axvline(x=target_position, color='red')
    plt.title(figtitle)
    plt.ylabel('Relative Frequency')
    plt.xlabel('Actual position from position sensor (mL mark)')
    if filename is not None:
        for format in formats:
            print('Saving plot as {}.{}'.format(filename, format))
            plt.savefig(filename + '.{}'.format(format))
    if showfig:
        plt.show()
    plt.close()

def analyze(filename):
    with open(filename) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    positioning_lines = filter(lines)
    split_lines = split_log_by_target(positioning_lines)
    positioning_locations = {target: extract(lines)
                             for (target, lines) in split_lines.items()}
    positioning_lines = {target: filter(lines)
                         for (target, lines) in split_lines.items()}
    for (target, actual_positions) in positioning_locations.items():
        # Basic distribution
        figname = os.path.splitext(filename)[0] + 'plot_{}mL'.format(target)
        figtitle = ('Pipettor PID positioning to {} mL mark target'
                    .format(target))
        plot_positioning_hist(target, actual_positions, figtitle, filename=figname)
        # Converged vs. stalled distribution
        locations = {
            name: extract(positioning_lines[target], pattern_name=name, warn=False)
            for name in ['converged', 'stalled']
        }
        figname = os.path.splitext(filename)[0] + 'plot_{}mL_stalledconverged'.format(target)
        figtitle = ('Pipettor PID positioning to {} mL mark target, stalled vs. converged'
                    .format(target))
        plot_positioning_hist(target, locations, figtitle, filename=figname)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    analyze(args.filename)


if __name__ == '__main__':
    main()
