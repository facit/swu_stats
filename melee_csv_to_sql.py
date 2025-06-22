#!/usr/bin/env python3
"""melee_csv_to_sql.py
This script processes CSV files containing tournament standings from Melee.gg
and inserts the data into a SQLite database. It handles tournament metadata,
decks, leaders, bases, and results. The CSV files are expected to be in a specific
format, with columns for player names, leaders, bases, deck links, and results.
Usage
-------
    python melee_csv_to_sql.py

It expects the CSV files to be located in a folder named `csv` in the current directory.
It will process all files matching the pattern `*_standings*.csv` in that folder.
The database file is named `swu_meta.db` by default, but you can change the `DB_FILE` variable
if your database file has a different name.
"""

import os
import sqlite3
import pandas as pd
import glob

DB_FILE = "swu_meta.db"  # Change if your DB file is named differently

def get_or_create(conn, table, where_clause, insert_dict):
    # Try to get the row, else insert and return the new id
    cur = conn.cursor()
    where = " AND ".join([f"{k}=?" for k in where_clause])
    cur.execute(f"SELECT rowid FROM {table} WHERE {where}", tuple(where_clause.values()))
    row = cur.fetchone()
    if row:
        return row[0]
    # Insert
    keys = ", ".join(insert_dict.keys())
    qmarks = ", ".join(["?"] * len(insert_dict))
    cur.execute(f"INSERT INTO {table} ({keys}) VALUES ({qmarks})", tuple(insert_dict.values()))
    conn.commit()
    return cur.lastrowid

def get_tournament_by_melee_id(conn,melee_id):
    cur = conn.cursor()
    # melee_id will be the last part of the link, so we can use that to find the tournament
    # The link will start with "https://melee.gg/Tournament/View/" or "https://www.melee.gg/Tournament/View/"" and end with the melee_id
    melee_link = f"https://melee.gg/Tournament/View/{melee_id}"
    cur.execute("SELECT tournament_id FROM tournaments WHERE link=?", (melee_link,))
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        melee_link = f"https://www.melee.gg/Tournament/View/{melee_id}"
        cur.execute("SELECT tournament_id FROM tournaments WHERE link=?", (melee_link,))
        row = cur.fetchone()
        if row:
            return row[0]
    return None

def insert_tournament(conn, name, date, link):
    print(f"Inserting tournament: {name} on {date} with link {link}")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO tournaments (name, date, link) VALUES (?, ?, ?)", (name, date, link))
    conn.commit()
    cur.execute("SELECT tournament_id FROM tournaments WHERE name=? AND date=? AND link=?", (name, date, link))
    return cur.fetchone()[0]

def get_player_by_name(conn, player_name):
    cur = conn.cursor()
    cur.execute("SELECT player_id FROM players WHERE name=?", (player_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    return None

def insert_player(conn, name):
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO players (name) VALUES (?)", (name,))
    conn.commit()
    cur.execute("SELECT player_id FROM players WHERE name=?", (name,))
    return cur.fetchone()[0]

def insert_leader(conn, name, subtitle):
    cur = conn.cursor()
    cur.execute("SELECT leader_id FROM leaders WHERE name=? AND subtitle=?", (name, subtitle))
    row = cur.fetchone()
    if row:
        return row[0]
    # If not, insert the new leader
    cur.execute("INSERT INTO leaders (name, subtitle) VALUES (?, ?)", (name, subtitle))
    conn.commit()
    cur.execute("SELECT leader_id FROM leaders WHERE name=? AND subtitle=?", (name, subtitle))
    return cur.fetchone()[0]

def insert_base(conn, name):
    cur = conn.cursor()
    # only insert if the base doesn't already exist
    # First check if the base exists
    cur.execute("SELECT base_id FROM bases WHERE name=?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    # If not, insert the new base
    cur.execute("INSERT INTO bases (name) VALUES (?)", (name,))
    conn.commit()
    cur.execute("SELECT base_id FROM bases WHERE name=?", (name,))
    return cur.fetchone()[0]

def insert_deck(conn, leader_id, base_id, decklink):
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO decks (leader_id, base_id, decklink) VALUES (?, ?, ?)", (leader_id, base_id, decklink))
    conn.commit()
    cur.execute("SELECT deck_id FROM decks WHERE leader_id=? AND base_id=? AND decklink=?", (leader_id, base_id, decklink))
    return cur.fetchone()[0]

def insert_result(conn, tournament_id, deck_id, result, player_id):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO results (tournament_id, deck_id, result, player_id) VALUES (?, ?, ?, ?)",
        (tournament_id, deck_id, result, player_id)
    )
    conn.commit()

def result_exists(conn, tournament_id, player_db_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM results WHERE tournament_id=? AND player_id=?", (tournament_id, player_db_id))
    return cur.fetchone() is not None

def process_csv(conn, csv_file):
    # print(f"Processing {csv_file}")
    df = pd.read_csv(csv_file)
    # Try to extract tournament info from filename or CSV
    melee_id = os.path.basename(csv_file).split("_")[0]

    # Check if the tournament is already in the database
    # To check this look for a tournament with a link column that matches the CSV filename
    # To match, the first part of the filename will match the last part of the link
    
    tournament_db_id = get_tournament_by_melee_id(conn, melee_id)
    if tournament_db_id is None:
        tournament_db_id = insert_tournament(conn, "", "", "")
    else:
        print(f"Tournament {melee_id} already exists in the database with ID {tournament_db_id}")

    # Iterate through the DataFrame rows and insert data into the database
    for _, row in df.iterrows():
        # Adjust these column names if your CSV differs!
        player_name = row.get("Username", row.get("Players/Teams", None))
        leader = row.get("Leader", None)
        base = row.get("Base", None)
        decklink = row.get("Decklink", None)
        result = row.get("Rank", None)

        if pd.isna(player_name) or pd.isna(result):
            continue

        player_db_id = get_player_by_name(conn, player_name)
        if player_db_id is None:
            player_db_id = insert_player(conn, player_name)

        # Check results table to make sure this result isn't already in the database
        if result_exists(conn, tournament_db_id, player_db_id):
            continue

        if leader is not None and leader != "-" and base is not None:
            leader_name = leader.strip().split(", ")[0]
            leader_subtitle = leader.strip().split(", ")[1]
            leader_id = None
            base_id = None
            if leader_name != "-" and leader_subtitle != "-" and base != "-":
                leader_id = insert_leader(conn, leader_name, leader_subtitle)
                base_id = insert_base(conn, base)
                deck_id = insert_deck(conn, leader_id, base_id, decklink)
        else:
            # If leader or base is missing, we can still insert the result but without deck info
            deck_id = None

        insert_result(conn, tournament_db_id, deck_id, int(result), player_db_id)

if __name__ == "__main__":
    conn = sqlite3.connect(DB_FILE)
    # Process all *_standings.csv and *_standings_unified.csv files
    for csv_file in glob.glob(os.path.join("csv", "*_standings*.csv")):
        process_csv(conn, csv_file)
    conn.close()