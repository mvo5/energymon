#!/usr/bin/python3

import datetime
import logging
import sys

from energymon.energymon import EnergyMon, EnergyStats
from energymon.db import EnergyDatabase


class DebugEnergyStats:
    def __init__(self):
        self._last = datetime.datetime(1970, 1, 1)

    def log_periodic(self, stats: EnergyStats):
        if stats.when - self._last > datetime.timedelta(seconds=60):
            logging.info(stats)
            self._last = datetime.datetime.now()


def main():
    logging.basicConfig(level=logging.INFO)
    # TODO: add a way to pass serial_device
    mon = EnergyMon()
    # log stats to stdout for debugging
    debug_logger = DebugEnergyStats()
    mon.add_callback(debug_logger.log_periodic)
    # add a database
    db = EnergyDatabase("energy.db")
    mon.add_callback(db.store_periodic)
    logging.info(f"starting energy monitor")
    mon.loop_forever()


if __name__ == "__main__":
    main()
