#!/usr/bin/env python3

import logging as log
import common as c

first_ping_per_pid = {}


def was_toggled(r1, r2, feature):
    """Return True if the feature was toggled during the two pings."""
    try:
        return r1[feature] != r2[feature]
    except KeyError:
        return False


def inc_toggles_per_day(pid, r1, r2):
    # Map the day of the study to the number of toggles on that day.
    toggles_per_day = stats_per_pid.setdefault(pid, {n: 0 for n in range(7)})

    if pid not in first_ping_per_pid.keys():
        first_ping_per_pid[pid] = r1[c.TIMESTAMP]

    for feature in c.FEATURES:
        if was_toggled(r1, r2, feature):
            # Determine the number of days that have passed since the first
            # recorded ping.
            offset = (r2[c.TIMESTAMP] - first_ping_per_pid[pid]) / 1000
            day = int(offset / 60 / 60 / 24)
            try:
                toggles_per_day[day] += 1
            except KeyError:  # Some participants were in phase 2 for > 7 days.
                pass


def print_csv(stats_per_pid):
    """Print results as CSV in long format."""

    print("pid,day,num_toggles")
    for pid, toggles_per_day in sorted(stats_per_pid.items()):
        for day, num_toggles in toggles_per_day.items():
            print("%s,%d,%d" % (pid, day + 1, num_toggles))


def print_table(stats_per_pid):
    """Print results as LaTeX table rows."""

    for pid, toggles_per_day in sorted(stats_per_pid.items()):
        row = [pid]
        for day, num_toggles in toggles_per_day.items():
            row.append(fmt_num(num_toggles))
        print(" & ".join(row) + " \\\\")


def fmt_num(num):
    if num > 0:
        return str(num)
    else:
        return "\zero{}"


if __name__ == "__main__":
    # Map participant IDs to the number of toggles per day, e.g.:
    # { "P1": {
    #     0: 15,
    #     1: 3,
    #     ...
    #   },
    #   ...
    # }
    stats_per_pid = {}
    c.run_for_ping_tuples(inc_toggles_per_day, skip_baseline=True)

    print_table(stats_per_pid)
