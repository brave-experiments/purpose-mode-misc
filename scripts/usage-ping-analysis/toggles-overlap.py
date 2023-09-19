#!/usr/bin/env python3

import logging as log
import common as c
from itertools import combinations_with_replacement


def last_pings(ping: dict):
    """Populate toggles_per_pid."""
    uid = ping[c.UID]
    to_delete = []
    for attr, _ in ping.items():
        if attr not in c.FEATURES:
            to_delete.append(attr)
    for attr in to_delete:
        ping.pop(attr)
    toggles_per_pid[uid] = ping


def print_csv():
    """Print the pair-wise Hamming distance between all usage pings."""

    print("hamming_distance")
    num_iterations = 0

    for pid1, pid2 in combinations_with_replacement(toggles_per_pid.keys(), 2):
        # Not interested in the distance between identical pings.
        if pid1 == pid2:
            continue
        log.info("Determining Hamming distance between %s and %s." % (pid1, pid2))

        l1 = list(toggles_per_pid[pid1].values())
        l2 = list(toggles_per_pid[pid2].values())
        print(c.hamming_distance(l1, l2))
        num_iterations += 1

    log.info(
        "Analyzed %d combinations of %d vectors."
        % (num_iterations, len(toggles_per_pid.values())),
    )


if __name__ == "__main__":
    toggles_per_pid = {}
    c.run_for_last_pings(last_pings)
    print_csv()
