#!/usr/bin/env python3
"""remove_unknown_decks.py

Clean‑up script to purge decks that reference an "unknown" leader or base – i.e.
rows in `leaders` or `bases` where the `name` field is literally a single dash
("-"). Any corresponding decks are deleted, and their references in `results`
are set to NULL so that tournament results remain intact but no longer point to
invalid deck entries.

The entire operation occurs inside a single transaction with foreign‑key checks
enabled, making it safe to run repeatedly (idempotent).

Usage
-----
    python remove_unknown_decks.py [path/to/database.sqlite]

If no path is supplied, the script defaults to the file `mydb.sqlite` in the
current working directory.
"""
from __future__ import annotations

import sys
import sqlite3
from contextlib import closing
from typing import List

DEFAULT_DB = "swu_meta.db"


def _column_allows_null(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    """Return True iff the given column in *table* is nullable."""
    cur.execute(f"PRAGMA table_info({table});")
    for _cid, name, _type, notnull, _dflt, _pk in cur.fetchall():
        if name == column:
            return not notnull  # notnull==1 means NOT NULL constraint present
    raise RuntimeError(f"Column {column!r} not found in table {table!r}.")


def _placeholders(seq: List[int]) -> str:
    """Return a comma‑separated list of '?' placeholders of the same length as *seq*.

    If *seq* is empty returns SQL 'NULL' so IN (NULL) safely yields no rows.
    """
    return ",".join(["?"] * len(seq)) if seq else "NULL"


def main(db_path: str) -> None:
    with closing(sqlite3.connect(db_path)) as conn, conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        cur = conn.cursor()

        # 1. Identify unknown leaders & bases ---------------------------------
        cur.execute("SELECT leader_id FROM leaders WHERE name='-';")
        bad_leaders = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT base_id FROM bases WHERE name='-';")
        bad_bases = [row[0] for row in cur.fetchall()]

        if not bad_leaders and not bad_bases:
            print("No unknown leaders or bases found – nothing to do.")
            return

        # 2. Gather affected decks -------------------------------------------
        query = f"""
            SELECT deck_id FROM decks
            WHERE leader_id IN ({_placeholders(bad_leaders)})
               OR base_id   IN ({_placeholders(bad_bases)});
        """
        cur.execute(query, (*bad_leaders, *bad_bases))
        deck_ids = [row[0] for row in cur.fetchall()]

        if not deck_ids:
            print("No decks reference the unknown leaders/bases – nothing to do.")
            return

        # 3. Null‑out deck_id in results -------------------------------------
        if not _column_allows_null(cur, "results", "deck_id"):
            raise RuntimeError(
                "results.deck_id is NOT NULL – cannot set to NULL. \n"
                "Either make the column nullable or delete affected results first."
            )

        cur.execute(
            f"UPDATE results SET deck_id = NULL WHERE deck_id IN ({_placeholders(deck_ids)});",
            deck_ids,
        )
        updated_results = cur.rowcount

        # 4. Delete the bad decks -------------------------------------------
        cur.execute(
            f"DELETE FROM decks WHERE deck_id IN ({_placeholders(deck_ids)});",
            deck_ids,
        )
        deleted_decks = cur.rowcount

        # 5. Optionally remove orphan unknown leaders/bases -------------------
        # Only delete if they are no longer referenced by any deck.
        deleted_leaders = deleted_bases = 0
        if bad_leaders:
            cur.execute(
                f"""
                    DELETE FROM leaders
                     WHERE leader_id IN ({_placeholders(bad_leaders)})
                       AND leader_id NOT IN (SELECT leader_id FROM decks);
                """,
                bad_leaders,
            )
            deleted_leaders = cur.rowcount

        if bad_bases:
            cur.execute(
                f"""
                    DELETE FROM bases
                     WHERE base_id IN ({_placeholders(bad_bases)})
                       AND base_id NOT IN (SELECT base_id FROM decks);
                """,
                bad_bases,
            )
            deleted_bases = cur.rowcount

        conn.commit()

    # 6. Final summary --------------------------------------------------------
    print(f"Updated {updated_results} results rows (deck_id → NULL)")
    print(f"Deleted {deleted_decks} corrupted decks")
    if deleted_leaders or deleted_bases:
        print(
            f"Also removed {deleted_leaders} unknown leader(s) and "
            f"{deleted_bases} unknown base(s) that were no longer referenced."
        )


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB
    main(db_file)
