#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse
import monarch
import signal
import sys

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description = "Plot Sigfox Monarch Beacon")
    parser.add_argument("-r", "--rc", help = "Radio configuration (rc1, rc2, rc3, rc4 or rc6)", default = "rc1")
    parser.add_argument("-s", "--samplingrate", help = "Sampling rate for transmit Signal (Hz)", type = int, default = 2000000)
    args = parser.parse_args()

    # Retrieve beacon and center frequency
    monarch_beacon = monarch.generate_beacon(args.samplingrate, args.rc)

    # Plot time domain
    plt.plot(np.arange(len(monarch_beacon)) / args.samplingrate, np.abs(monarch_beacon))
    plt.xlabel("Time [s]")
    plt.show()

    plt.specgram(monarch_beacon, Fs = args.samplingrate, NFFT=1024, cmap = "viridis_r")
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [Hz]")
    plt.show()


if __name__ == '__main__':
    main()
