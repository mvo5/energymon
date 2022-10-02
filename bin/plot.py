#!/usr/bin/python3

import sys

import matplotlib.dates
import matplotlib.pyplot as plt

from energymon.db import EnergyDatabase


def main():
    dbpath = sys.argv[1]
    db = EnergyDatabase(dbpath)
    raw_dates, energy = db._get_data()
    dates = matplotlib.dates.epoch2num(raw_dates)
    fig, ax = plt.subplots()
    ax.plot(dates, energy)
    ax.xaxis.set_major_locator(matplotlib.dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    plt.show()


if __name__ == "__main__":
    main()
