#!/usr/bin/env python3

from collections import namedtuple

import common as c

times_per_pid = {}

TimeSpent = namedtuple(
    "TimeSpent",
    ["total", c.FACEBOOK, c.LINKEDIN, c.TWITTER, c.YOUTUBE, c.OTHER],
    defaults=[0, 0, 0, 0, 0, 0],
)


def time_per_site(ping):
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

    return times_per_pid


def print_latex():
    for pid, times in sorted(times_per_pid.items()):
        print(
            "%s & %d & %.1f & %.1f & %.1f & %.1f & %.1f \\\\"
            % (
                pid,
                times.total / 60 / 60,
                times.Facebook / times.total * 100,
                times.LinkedIn / times.total * 100,
                times.Twitter / times.total * 100,
                times.YouTube / times.total * 100,
                times.Other / times.total * 100,
            )
        )


if __name__ == "__main__":
    c.run_for_last_pings(time_per_site)
    print_latex()
