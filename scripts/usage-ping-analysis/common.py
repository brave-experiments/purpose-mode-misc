import json
import re
import os
import logging as log
import datetime
import sys
from typing import Callable

log.basicConfig(level=log.INFO)

UID = "uid"
ENABLED = "Enable"
TIMESTAMP = "timestamp"
INTERVENTION = "enableIntervention"
# We only consider sites at which the participant spent this many seconds.
MIN_TIME = 600
FACEBOOK = "Facebook"
LINKEDIN = "LinkedIn"
TWITTER = "Twitter"
YOUTUBE = "YouTube"
OTHER = "Other"
SITES = [FACEBOOK, LINKEDIN, TWITTER, YOUTUBE, OTHER]
# Participants must have spent at least six minutes on a site for us to analyze it.
MIN_TIME_ON_SITE = 60 * 6

BASELINE_PHASE = 0
INTERVENTION_PHASE = 1
FEATURES = set(
    [
        "FacebookAutoplay",
        "FacebookCompact",
        "FacebookDesaturate",
        "FacebookFeed",
        "FacebookInfinite",
        "FacebookNotif",
        "LinkedInAutoplay",
        "LinkedInCompact",
        "LinkedInDesaturate",
        "LinkedInFeed",
        "LinkedInInfinite",
        "LinkedInNotif",
        "TwitterAutoplay",
        "TwitterCompact",
        "TwitterDesaturate",
        "TwitterFeed",
        "TwitterInfinite",
        "TwitterNotif",
        "YouTubeAutoplay",
        #        "YouTubeComments": 0,
        "YouTubeCompact",
        "YouTubeDesaturate",
        "YouTubeFeed",
        "YouTubeInfinite",
        "YouTubeNotif",
    ]
)


def fmt_secs(secs: int) -> datetime.timedelta:
    """Turn the given seconds into a timedelta object."""
    return datetime.timedelta(seconds=secs)


def hamming_distance(l1, l2: list) -> int:
    """Return the Hamming distance between the two given lists."""
    assert len(l1) == len(l2)

    num_diff = 0
    for e1, e2 in zip(l1, l2):
        if e1 != e2:
            num_diff += 1
    return num_diff


def new_dict() -> dict:
    return {
        "FacebookAutoplay": 0,
        "FacebookCompact": 0,
        "FacebookDesaturate": 0,
        "FacebookFeed": 0,
        "FacebookInfinite": 0,
        "FacebookNotif": 0,
        "LinkedInAutoplay": 0,
        "LinkedInCompact": 0,
        "LinkedInDesaturate": 0,
        "LinkedInFeed": 0,
        "LinkedInInfinite": 0,
        "LinkedInNotif": 0,
        "TwitterAutoplay": 0,
        "TwitterCompact": 0,
        "TwitterDesaturate": 0,
        "TwitterFeed": 0,
        "TwitterInfinite": 0,
        "TwitterNotif": 0,
        "YouTubeAutoplay": 0,
        #        "YouTubeComments": 0,
        "YouTubeCompact": 0,
        "YouTubeDesaturate": 0,
        "YouTubeFeed": 0,
        "YouTubeInfinite": 0,
        "YouTubeNotif": 0,
    }


def get_arg_path() -> str:
    """Return the command line argument or exit."""
    if len(sys.argv) != 2:
        log.error("Usage: %s FILE_NAME" % sys.argv[0])
        exit(1)
    return sys.argv[1]


def run_for_ping_tuples(func: Callable, skip_baseline: bool = False):
    """Run the given function over two subsequent pings for all files in a directory."""
    for root, _, files in os.walk(get_arg_path()):
        for file in files:
            path = os.path.join(root, file)
            if not path.endswith("ping.json"):
                continue
            log.info("Analyzing %s." % path)
            _run_for_ping_tuples(path, func, skip_baseline)


def _run_for_ping_tuples(path: str, func: Callable, skip_baseline: bool = False):
    """Run the given function over two subsequent pings in the given file."""
    enabled_pings, disabled_pings, num_skipped = 0, 0, 0
    pid = pid_from_filename(path)
    first_ping, last_ping = get_first_ping(path), get_last_ping(path)

    with open(path, "r") as f:
        line = next(f)
        for next_line in f:
            ping1, ping2 = json.loads(line), json.loads(next_line)
            # Skip baseline pings if desired.
            if skip_baseline and ping1[INTERVENTION] == False:
                line = next_line
                num_skipped += 1
                continue
            # Ignore the first and last hour worth of pings because these were the
            # onboarding and offboarding sessions.
            if are_within_hour(first_ping, ping2) or are_within_hour(ping1, last_ping):
                num_skipped += 1
                continue
            # Skip pings if the extension was disabled.
            if not ping1[ENABLED] or not ping2[ENABLED]:
                disabled_pings += 1
                num_skipped += 1
                continue
            enabled_pings += 1
            func(pid, ping1, ping2)
            line = next_line

    log.info(
        "Ping file contained %d enabled and %d disabled pings. Skipped %d pings."
        % (enabled_pings, disabled_pings, num_skipped)
    )


def run_for_last_pings(func: Callable, phase: int = INTERVENTION_PHASE):
    """Run the given function over all last pings."""
    for root, _, files in os.walk(get_arg_path()):
        for file in files:
            p = os.path.join(root, file)
            if not p.endswith("ping.json"):
                continue
            log.info("Analyzing %s." % p)
            func(get_last_ping(p, phase))


def are_within_hour(r1: dict, r2: dict) -> bool:
    """Return True if the two given pings are within an hour from each other."""
    # Convert to timestamp in seconds.
    t1, t2 = r1[TIMESTAMP] / 1000, r2[TIMESTAMP] / 1000
    return int(abs(t2 - t1) / 60 / 60) == 0


def pid_from_filename(path: str) -> str:
    """Return the participant ID of the given file."""
    ping = get_last_ping(path)
    return normalize(ping[UID])


def get_first_ping(path: str) -> dict:
    """Return the first ping of the given ping.json file."""
    with open(path) as f:
        for line in f:
            return json.loads(line)
    return dict()  # Will never run.


def get_last_ping(path: str, phase: int = INTERVENTION_PHASE) -> dict:
    """Return the last ping of the given phase as JSON object."""
    pings = []
    with open(path) as f:
        line = next(f)
        for next_line in f:
            ping, next_ping = json.loads(line), json.loads(next_line)
            if phase == BASELINE_PHASE:
                if not ping[INTERVENTION] and next_ping[INTERVENTION]:
                    pings.append(next_ping)
            else:
                pings.append(next_ping)

    # Ignore the last hour worth of pings because that's when the offboarding
    # session took place.
    last_ping = pings[-1]
    for p in reversed(pings):
        if not are_within_hour(last_ping, p):
            return p
    return dict()  # Will never run.


# def first_ping(path, phase=BASELINE_PHASE):
#     """Return the first ping of the given phase as JSON object."""
#     with open(path) as f:
#         line = next(f)
#         if phase == BASELINE_PHASE:
#             return json.loads(line)

#         for next_line in f:
#             ping, next_ping = json.loads(line), json.loads(next_line)
#             if not ping[INTERVENTION] and next_ping[INTERVENTION]:
#                 return next_ping
#         assert False


def normalize(pid: str) -> str:
    """Return normalized pid, with underscores removed."""
    pid = re.sub(r"_.*", "", pid)
    for i in range(1, 10):
        if pid == "P%d" % i:
            pid = "P0%d" % i
    return pid
