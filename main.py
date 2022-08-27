#!/usr/bin/python3

import datetime
import logging
import sys

from energymon import EnergyMon, EnergyStats


class DebugEnergyStats:
    def __init__(self):
        self._last_print = datetime.datetime(1970, 1, 1)

    def print_periodic(self, stats: EnergyStats):
        if stats.when - self._last_print > datetime.timedelta(seconds=60):
            print(stats)
            self._last_print = datetime.datetime.now()


def main():
    logging.basicConfig(level=logging.INFO)
    device = sys.argv[1]
    mon = EnergyMon(device)
    debug_printer = DebugEnergyStats()
    mon.add_callback(debug_printer.print_periodic)
    logging.info(f"starting energy monitor at {device}")
    mon.loop_forever()


if __name__ == "__main__":
    main()
