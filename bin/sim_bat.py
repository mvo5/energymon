#!/usr/bin/python3

import datetime
import sys


from energymon.db import EnergyDatabase


class BatterySimulator:
    def __init__(self, dbpath, capacity=5*1000, cost_per_kw=0.35):
        self._db = EnergyDatabase(dbpath)
        # XXX: assume battery is full at the begnning for easier stats
        self._bat = capacity
        self._cap = capacity
        self._cost_per_kw = cost_per_kw
        self._energy_from_battery = 0
        self._energy_from_grid = 0
        # these stats are a bit useless
        self._n_full = 0
        self._n_empty = 0
    def simulate(self, ):
        cur = self._db._get_all_current_power()
        first_dt = last_dt = datetime.datetime.fromtimestamp(cur.fetchone()[0])
        bat_empty_or_full = False
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
                    bat_empty_or_full = False
                else:
                    if not bat_empty_or_full:
                        self._n_empty += 1
                        bat_empty_or_full = True
                    self._energy_from_grid += energy_per_time
            # energy availabe, store
            if energy_per_time < 0:
                if self._bat < self._cap:
                    self._bat += -1*energy_per_time
                    bat_empty_or_full = False
                else:
                    if not bat_empty_or_full:
                        self._n_full += 1
                        bat_empty_or_full = True
            last_dt = dt
        total_time = last_dt - first_dt
        bat_kw = self._energy_from_battery/1000
        # fugly, return sensible data instead
        print(f"Total {bat_kw:.2f} kWh taken from battery in {total_time}")
        print(f"Total taken from grid {self._energy_from_grid/1000:.2f} kWh")
        money = bat_kw*self._cost_per_kw
        print(f"Money {money:.2f}€")
        print(f"Total full: {self._n_full} empty: {self._n_empty}")


def main():
    dbpath = sys.argv[1]
    bat = BatterySimulator(dbpath)
    bat.simulate()


if __name__ == "__main__":
    main()
