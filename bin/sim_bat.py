#!/usr/bin/python3

import datetime
import sys

import matplotlib.ticker
import matplotlib.dates

from energymon.db import EnergyDatabase


class RealConciseFormatter(matplotlib.ticker.Formatter):
    def __init__(self):
        self._last_day = datetime.datetime.fromtimestamp(0)
    def __call__(self, x, pos=0):
        dt = matplotlib.dates.num2date(x)
        if dt.date() != self._last_day.date():
            self._last_day = dt
            return dt.strftime("%Y-%m-%d")
        return dt.strftime("%H:%M")


class BatterySimulator:
    # cost_per_kwh=0.35€-0.10€
    def __init__(self, dbpath, capacity=5*1000, cost_per_kwh=0.25):
        self._db = EnergyDatabase(dbpath)
        # XXX: assume battery is full at the begnning for easier stats
        self._bat = capacity/2
        self._cap = capacity
        self._cost_per_kwh = cost_per_kwh
        self._energy_from_battery = 0
        self._energy_from_grid = 0
        self._energy_to_grid = 0
    def simulate(self):
        cur = self._db._get_all_current_power()
        first_dt = last_dt = datetime.datetime.fromtimestamp(cur.fetchone()[0])
        bat_cap = []
        time = []
        for row in cur:
            ts, energy = row[0], row[1]
            dt = datetime.datetime.fromtimestamp(ts)
            delta = dt-last_dt
            if delta.seconds > 3600:
                raise Exception("need deltas with less than 1h granularity")
            energy_per_time = energy/(3600/delta.seconds)
            # energy needed, see if battery can provide it
            if energy_per_time > 0:
                if self._bat > energy_per_time:
                    self._energy_from_battery += energy_per_time
                    self._bat -= energy_per_time
                else:
                    self._energy_from_grid += energy_per_time
            # energy availabe, store
            if energy_per_time < 0:
                if self._bat < self._cap:
                    self._bat += -1*energy_per_time
                    bat_empty_or_full = False
                else:
                    self._energy_to_grid += energy_per_time
            time.append(dt)
            bat_cap.append(self._bat)
            last_dt = dt
        total_time = last_dt - first_dt
        bat_kw = self._energy_from_battery/1000
        # fugly, return sensible data instead
        print(f"Total {bat_kw:.2f} kWh taken from battery in {total_time}")
        print(f"Total taken from grid {self._energy_from_grid/1000:.2f} kWh")
        print(f"Total given to grid {self._energy_to_grid/1000:.2f} kWh")
        money = bat_kw*self._cost_per_kwh
        print(f"Money {money:.2f}€")
        return time, bat_cap


def main():
    dbpath = sys.argv[1]
    bat = BatterySimulator(dbpath)
    dates, energy = bat.simulate()

    import matplotlib.dates
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    fig.set_figwidth(200)
    ax.plot(dates, energy)
    loc = matplotlib.dates.HourLocator(interval=2)
    ax.xaxis.set_major_locator(loc)
    fmt = RealConciseFormatter()
    ax.xaxis.set_major_formatter(fmt)
    fig.autofmt_xdate()
    plt.show()


if __name__ == "__main__":
    main()
