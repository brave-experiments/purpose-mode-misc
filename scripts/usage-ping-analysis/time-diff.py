#!/usr/bin/env python3
#
# To verify the calculation:
# jq -s 'last(.[] | select(.enableIntervention == false)) | .TimeSpentOnYouTube' \
#   path/to/ping.json
# jq -s 'last(.[] | select(.enableIntervention == true)) | .TimeSpentOnYouTube' \
#   path/to/ping.json

from collections import namedtuple
from typing import Callable


import common as c

TimeSpent = namedtuple(
    "TimeSpent",
    ["total", c.FACEBOOK, c.LINKEDIN, c.TWITTER, c.YOUTUBE, c.OTHER],
    defaults=[0, 0, 0, 0, 0, 0],
)


def time_per_site(times_per_pid: dict) -> Callable:
    """For each pid, keep track of the time spent on a given site."""

    def inner(ping):
        pid = c.normalize(ping[c.UID])
        t = {}
        for site in c.SITES:
            try:
                t[site] = ping["TimeSpentOn%s" % site]
            except KeyError:
                t[site] = 0

        times_per_pid[pid] = TimeSpent(
            total=sum(t.values()),
            Facebook=t[c.FACEBOOK],
            LinkedIn=t[c.LINKEDIN],
            Twitter=t[c.TWITTER],
            YouTube=t[c.YOUTUBE],
            Other=t[c.OTHER],
        )

    return inner


def fmt(secs: int) -> str:
    """Convert # of seconds into H:MM format."""
    if secs == 0:
        return "\\zero{}"

    hours = int(abs(secs) / 60 / 60)
    minutes = int(abs(secs) / 60 % 60)
    prefix = ""
    if secs < 0:
        prefix = "-"
    return "%s%d:%02d" % (prefix, hours, minutes)


def print_diff(baseline: dict, intervention: dict):
    """Print the time-on-site differences between baseline and intervention."""

    for pid1, pid2 in sorted(zip(baseline, intervention)):
        assert pid1 == pid2

        diff_on = {}
        time_before, time_after = baseline[pid1], intervention[pid1]
        for site, before in time_before._asdict().items():
            # Subtract "before" time from "after" time as time is cumulative.
            after = time_after._asdict()[site] - before
            # Convert time difference to hours.
            if before < c.MIN_TIME_ON_SITE and after < c.MIN_TIME_ON_SITE:
                diff_on[site] = 0
            else:
                diff_on[site] = after - before

        print(
            "%s & %s & %s & %s & %s & %s & %s \\\\"
            % (
                pid1,
                fmt(diff_on["total"]),
                fmt(diff_on[c.FACEBOOK]),
                fmt(diff_on[c.LINKEDIN]),
                fmt(diff_on[c.TWITTER]),
                fmt(diff_on[c.YOUTUBE]),
                fmt(diff_on[c.OTHER]),
            )
        )


if __name__ == "__main__":
    baseline, intervention = {}, {}

    c.run_for_last_pings(time_per_site(baseline), phase=c.BASELINE_PHASE)
    c.run_for_last_pings(time_per_site(intervention), phase=c.INTERVENTION_PHASE)

    print_diff(baseline, intervention)
