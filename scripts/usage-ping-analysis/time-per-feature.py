#!/usr/bin/env python3

import sys
import json
import logging as log
import statistics

import common as c

MS = 1000

total_secs = 0
time_per_site = {
    "Facebook": 0,
    "LinkedIn": 0,
    "Twitter": 0,
    "YouTube": 0,
}


def is_enabled(r1, r2, feature):
    """Return True if the feature is enabled for the two subsequent pings."""
    try:
        return r1[feature] == True and r2[feature] == True
    except KeyError:
        return False


def time_spent_on_site(site, r1, r2):
    """Return the seconds spent on the given site between the two given pings."""
    key = "TimeSpentOn%s" % site
    try:
        return r2[key] - r1[key]
    except KeyError:
        return 0


def feature_to_site(feature):
    """Map a feature name to the site the feature is used on."""
    for site in c.SITES:
        if feature.startswith(site):
            return site
    assert False  # We must never end up here.


def inc_time(pid, r1, r2):
    """Increment the time spent with each enabled feature."""

    # Fetch the given participant's times per feature.
    time_per_feature = stats_per_pid.setdefault(pid, c.new_dict())
    time_per_site = site_times_per_pid.setdefault(
        pid,
        {
            "Facebook": 0,
            "LinkedIn": 0,
            "Twitter": 0,
            "YouTube": 0,
            "Other": 0,
        },
    )

    # Determine the time that has passed since the two subsequent pings.  Skip
    # periods of long inactivity.
    sec_diff = (r2[c.TIMESTAMP] - r1[c.TIMESTAMP]) / MS
    if sec_diff > 65:
        return

    for site in c.SITES:
        time_per_site[site] += time_spent_on_site(site, r1, r2)

    for feature in time_per_feature.keys():
        site = feature_to_site(feature)
        sec_diff = time_spent_on_site(site, r1, r2)
        # If, say, LinkedInDesaturate was enabled during both subsequent pings
        # *and* the participant spent time on LinkedIn during these pings, we
        # increase the number of seconds that the user spent with the feature enabled.
        if is_enabled(r1, r2, feature):
            time_per_feature[feature] += sec_diff


def calc_pct_time(pid, feature):
    """Return the percentage of time that the feature was used on the site."""

    site_times = site_times_per_pid[pid]
    site = feature_to_site(feature)
    secs_on_site = site_times[site]

    time_per_feature = stats_per_pid[pid]
    secs_with_feature = time_per_feature[feature]

    if secs_on_site == 0:
        assert secs_with_feature == 0
        return 0

    # if secs_on_site < 3600:
    #     return -1

    return secs_with_feature / secs_on_site * 100


def site_from_features(time_per_feature: dict) -> str:
    for feature, _ in time_per_feature.items():
        return feature_to_site(feature)
    assert False


def print_latex():
    # Keep track of all percentages per feature.
    pcts_per_feature = {k: [] for k in c.new_dict().keys()}

    for pid, time_per_feature in sorted(stats_per_pid.items()):
        record = [c.normalize(pid)]

        prev_site = ""
        for feature, _ in time_per_feature.items():
            site = feature_to_site(feature)
            if site != prev_site:
                log.info("Now dealing with %s" % site)
                time_on_site = site_times_per_pid[pid][site]
                # If participant spent less than a minute on a site,
                # we don't analyze it.
                if time_on_site > c.MIN_TIME_ON_SITE:
                    hours = time_on_site / 60 / 60
                    log.info("%s = %.1f hours" % (c.fmt_secs(time_on_site), hours))
                    record.append("\n%.1f" % (hours))
                else:
                    record.append("\zero{}")
                prev_site = site

            if time_on_site > c.MIN_TIME_ON_SITE:
                pcts_per_feature[feature].append(calc_pct_time(pid, feature))
                record.append("%.0f" % calc_pct_time(pid, feature))
            else:
                pcts_per_feature[feature].append(0)
                record.append("\zero{}")

        record[-1] += " \\\\"
        print(" & ".join(record))
        print()
        record = []

    # Show the median and mean percentages.
    for feature, pcts in pcts_per_feature.items():
        log.info(
            "%20s median=%5.1f, mean=%5.1f"
            % (feature, statistics.median(pcts), statistics.mean(pcts))
        )


def print_csv():
    print("pid,feature,pct_time")
    for pid, time_per_feature in stats_per_pid.items():
        for feature, time in time_per_feature.items():
            print(
                "%s,%s,%.1f" % (c.normalize(pid), feature, calc_pct_time(pid, feature))
            )


if __name__ == "__main__":
    site_times_per_pid = {}
    stats_per_pid = {}
    c.run_for_ping_tuples(inc_time, skip_baseline=True)

    print_latex()
