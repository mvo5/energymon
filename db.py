import datetime

import sqlite3

from energymon import EnergyStats


class EnergyDatabase:
    def __init__(self, dbpath: str):
        self._last = datetime.datetime(1970, 1, 1)
        self._conn = sqlite3.connect(dbpath)
        self._dbpath = dbpath
        with sqlite3.connect(self._dbpath) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS "energy_stats"
                (
                  [when] INTEGER PRIMARY KEY,
                  [total_power_in] INTEGER NOT NULL,
                  [total_power_out] INTEGER NOT NULL,
                  [current_power] INTEGER NOT NULL
                );
                """
            )

    def store_periodic(self, stats: EnergyStats):
        if stats.when - self._last > datetime.timedelta(seconds=60):
            self._last = datetime.datetime.now()
            with sqlite3.connect(self._dbpath) as conn:
                conn.execute(
                    """
                    INSERT INTO "energy_stats"
                    (
                      "when", "current_power", "total_power_in", "total_power_out"
                    )
                    VALUES (?, ?, ?, ?);
                    """,
                    (
                        int(stats.when.timestamp()),
                        stats.current_power,
                        stats.total_power_in,
                        stats.total_power_out,
                    ),
                )
