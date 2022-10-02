import datetime

import sqlite3

from energymon.energymon import EnergyStats


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

    def _get_all_current_power(self):
        with sqlite3.connect(self._dbpath) as conn:
            cur = conn.execute(
                """SELECT "when","current_power" FROM "energy_stats" ASC"""
            )
            return cur
                
    def _get_first_entry(self):
        with sqlite3.connect(self._dbpath) as conn:
            cur = conn.execute(
                """SELECT "when" FROM "energy_stats" ASC LIMIT 1"""
            )
            unix_time = cur.fetchone()[0]
            dt = datetime.datetime.fromtimestamp(unix_time)
            return dt

    def _get_graph_data(self):
        with sqlite3.connect(self._dbpath) as conn:
            cur = conn.execute(
                """SELECT "when","current_power" FROM "energy_stats" ASC"""
            )
            energy_pairs = cur.fetchall()
            timestaps, energies = zip(*energy_pairs)
            return timestaps, energies
