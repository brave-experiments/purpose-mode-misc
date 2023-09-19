#!/usr/bin/env python3

import statistics
import logging as log
import common as c


def was_toggled(ping1: dict, ping2: dict, feature: str) -> bool:
    """Return True if the feature was toggled during the two pings."""
    try:
        return ping1[feature] != ping2[feature]
    except KeyError:
        return False


def inc_toggles(pid: str, ping1: dict, ping2: dict):
    """Increment total # of toggles for features that were toggled."""
    toggles_per_feature = stats_per_pid.setdefault(pid, c.new_dict())

    for feature in toggles_per_feature.keys():
        toggles_per_feature[feature] += was_toggled(ping1, ping2, feature)


def toggle_stats():
    """Log statistics about the # of toggles."""
    all_toggles = []
    for _, toggles_per_feature in stats_per_pid.items():
        for _, num_toggles in toggles_per_feature.items():
            all_toggles.append(num_toggles)

    log.info("Median # of toggles: %.1f" % statistics.median(all_toggles))
    log.info("Mean # of toggles:   %.1f" % statistics.mean(all_toggles))


if __name__ == "__main__":
    # Map participant IDs to a toggles_per_feature dictionary, e.g.:
    # { "P1": {
    #     "TwitterAutoPlay": 3,
    #     "TwitterCompact": 1,
    #     ...
    #   },
    #   "P2": {
    #     ...
    #   }
    # }
    stats_per_pid = {}
    c.run_for_ping_tuples(inc_toggles)
    toggle_stats()

    print("pid,feature,num_toggles,last_toggle")
    for pid, toggles_per_feature in stats_per_pid.items():
        for feature, num_toggles in toggles_per_feature.items():
            print("%s,%s,%d" % (pid, feature, num_toggles))
