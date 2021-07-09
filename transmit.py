#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import argparse
import SoapySDR
import monarch
import signal
import sys

def embed_beacon(beacon, block, block_start, beacon_interval):
    assert(beacon_interval > beacon.size)

    # Block is large enough to contain multiple beacons or beginning / end of a beacon
    first_beacon_index = (block_start // beacon_interval) * beacon_interval
    block_end = block_start + block.size

    # The beacon prior to the current block does not reach into the current block:
    # Go to next beacon instead
    if first_beacon_index + beacon.size < block_start:
        first_beacon_index = first_beacon_index + beacon_interval

    for beacon_start in range(first_beacon_index, block_end, beacon_interval):
        beacon_end = beacon_start + beacon.size

        # if beacon is smaller than block length: just embed complete beacon
        if beacon_start >= block_start and beacon_end < block_end:
            block[beacon_start - block_start:beacon_end - block_start] = beacon

        # if beacon started before the current block and finishes in the block
        elif beacon_start < block_start and beacon_end < block_end:
            block[:beacon_end - block_start] = beacon[block_start - beacon_start:]

        # if beacon starts inside the current block, but does not finish
        elif beacon_start >= block_start and beacon_end > block_end:
            block[beacon_start - block_start:] = beacon[:block_end - beacon_start]

        # if beacon started before the current block and finishes after the current block
        elif beacon_start < block_start and beacon_end > block_end:
            block = beacon[block_start - beacon_start:block_end - beacon_end]

    return block


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description = "Generate Sigfox Monarch Beacon and transmit using SoapySDR")
    parser.add_argument("-r", "--rc", help = "Radio configuration (rc1, rc2, rc3, rc4, rc5, rc6 or rc7)", default = "rc1")
    parser.add_argument("-s", "--samplingrate", help = "Sampling rate for transmit Signal (Hz)", type = int, default = 2000000)
    parser.add_argument("-d", "--devicestring", help = "SoapySDR device string", default = "")
    parser.add_argument("-i", "--interval", help = "Interval in which Monarch beacon is transmitted (seconds)", type = float, default = 2 * 60)
    parser.add_argument("-g", "--gain", help = "Transmit Gain", type = int, default = 60)
    parser.add_argument("-o", "--offset", help = "Frequency offset from transmitter's center frequency", type = int, default = 100000)
    parser.add_argument("-m", "--mode", help = "Mode (normal / pattern1 / pattern2)", default = "normal")
    parser.add_argument("-p", "--stop", help = "Transmit beacon only once, then stop", action = "store_true", default = False)
    args = parser.parse_args()

    # Retrieve beacon and center frequency
    monarch_beacon = monarch.generate_beacon(args.samplingrate, args.rc, args.mode)
    monarch_freq = monarch.get_center_frequency(args.rc)

    # Mix beacon by frequency offset
    t_beacon = np.arange(monarch_beacon.size) / args.samplingrate
    monarch_beacon = np.multiply(monarch_beacon, np.exp(1.0j * 2 * np.pi * args.offset * t_beacon)).astype(np.complex64)

    # Configure SoapySDR transmitter
    transmitter = SoapySDR.Device(SoapySDR.KwargsFromString(args.devicestring))
    transmitter.setGain(SoapySDR.SOAPY_SDR_TX, 0, args.gain)
    transmitter.setSampleRate(SoapySDR.SOAPY_SDR_TX, 0, args.samplingrate)
    transmitter.setBandwidth(SoapySDR.SOAPY_SDR_TX, 0, args.samplingrate)
    transmitter.setFrequency(SoapySDR.SOAPY_SDR_TX, 0, monarch_freq - args.offset)
    txstream = transmitter.setupStream(SoapySDR.SOAPY_SDR_TX, SoapySDR.SOAPY_SDR_CF32)
    transmitter.activateStream(txstream)
    mtu = transmitter.getStreamMTU(txstream)

    print("Transmitting Sigfox Monarch beacon at " + str(monarch_freq) + " Hz, time interval " + str(args.interval) + " s")

    # Handle abort
    state = dict(running=True)
    def signal_handler(signum, _):
        state["running"] = False

    signal.signal(signal.SIGINT, signal_handler)

    block_start = 0
    while (not args.stop or block_start < len(monarch_beacon)) and state["running"]:
        block = embed_beacon(monarch_beacon, np.zeros(mtu, dtype = np.complex64), block_start, int(args.interval * args.samplingrate))
        status = transmitter.writeStream(txstream, [block], block.size, timeoutUs = 1000000)
        if status.ret != block.size:
            raise Exception("Expected writeStream() to consume all samples! %d" % status.ret)
        block_start = block_start + mtu

    transmitter.deactivateStream(txstream)
    transmitter.closeStream(txstream)

if __name__ == '__main__':
    main()
