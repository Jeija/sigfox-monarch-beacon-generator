#!/usr/bin/env python3

import numpy as np
import argparse

# Monarch beacon pattern and center frequency configuration 
delta_f1 = 16384 / 16
delta_f2 = 16384 / 13
delta_f3 = 16384 / 11

carriers = 12
duration_pattern1 = 0.362
duration_pattern2 = 0.038

rcs = {
    "rc1" : {
        "center" : 869505000,
        "pattern1" : delta_f1,
        "pattern2" : delta_f2
    },
    "rc2" : {
        "center" : 905180000,
        "pattern1" : delta_f1,
        "pattern2" : delta_f2
    },
    "rc3" : {
        "center" : 922250000,
        "pattern1" : delta_f1,
        "pattern2" : delta_f2
    },
    "rc4" : {
        "center" : 922250000,
        "pattern1" : delta_f2,
        "pattern2" : delta_f3
    },
    "rc5" : {
        "center" : 922250000,
        "pattern1" : delta_f1,
        "pattern2" : delta_f3
    },
    "rc6" : {
        "center" : 866250000,
        "pattern1" : delta_f1,
        "pattern2" : delta_f3
    },
    "rc7" : {
        "center" : 869160000,
        "pattern1" : delta_f2,
        "pattern2" : delta_f3
    },
}

def generate_beacon(samplingrate, rc, mode = "normal"):
    t_pattern1 = np.arange(0, duration_pattern1, 1 / samplingrate)
    t_pattern2 = np.arange(0, duration_pattern2, 1 / samplingrate)

    pattern1_carriers = np.arange(0, carriers * rcs[rc]["pattern1"], rcs[rc]["pattern1"])
    pattern2_carriers = np.arange(0, carriers * rcs[rc]["pattern2"], rcs[rc]["pattern2"])

    pattern1_carriers = pattern1_carriers - np.mean(pattern1_carriers)
    pattern2_carriers = pattern2_carriers - np.mean(pattern2_carriers)

    pattern1 = np.sum(np.exp(1.0j * 2 * np.pi * np.outer(pattern1_carriers, t_pattern1)), axis = 0)
    pattern2 = np.sum(np.exp(1.0j * 2 * np.pi * np.outer(pattern2_carriers, t_pattern2)), axis = 0)

    if mode == "normal":
        beacon = np.hstack([pattern1, pattern2])
    elif mode == "pattern1":
        beacon = pattern1
    elif mode == "pattern2":
        beacon = pattern2

    beacon = beacon / np.max(beacon)

    return beacon

def get_center_frequency(rc):
    return rcs[rc]["center"]
