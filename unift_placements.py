import argparse
import glob
import csv
import re
import sys
import os
import pandas as pd

def parse_placement(placement_str):
    match = re.match(r"(\d+)(?:st|nd|rd|th)(?:-(\d+)(?:st|nd|rd|th))?", placement_str)
    if match:
        return int(match.group(1))
    return None

def load_placements(filename):
    placements = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            if ":" not in line:
                continue
            placement, player = line.strip().split(":", 1)
            placements.append((placement.strip(), player.strip()))
    return placements

def find_standings_file(base_id):
    candidates = [
        f"{base_id}_standings_incomplete.csv"
    ]
    for fname in candidates:
        if os.path.exists(fname):
            return fname
    return None

def unify_placements(placements_file, standings_file, output_file):
    placements = load_placements(placements_file)
    df = pd.read_csv(standings_file)

    # Build a set of all player names from placements for quick lookup (lowercase)
    placement_names = set(player_name.lower() for _, player_name in placements)
    # Build a set of all top cut ranks from placements
    top_cut_ranks = set(parse_placement(placement_str) for placement_str, _ in placements if parse_placement(placement_str) is not None)

    # Update ranks in the DataFrame
    for placement_str, player_name in placements:
        new_rank = parse_placement(placement_str)
        if new_rank is None:
            continue

        mask = (
            df["Username"].astype(str).str.strip().str.lower() == player_name.lower()
        ) | (
            df["Players/Teams"].astype(str).str.strip().str.lower() == player_name.lower()
        )
        matches = df[mask]
        if not matches.empty:
            df.loc[mask, "Rank"] = new_rank
        elif player_name != "":
            print(f"Warning: Could not match player '{player_name}' in standings.")

    # Check for extra people in the top cut
    for _, row in df.iterrows():
        try:
            rank = int(row["Rank"])
        except Exception:
            continue
        if rank in top_cut_ranks:
            username = str(row.get("Username", "")).strip()
            team = str(row.get("Players/Teams", "")).strip()
            # If neither username nor team is in placements, warn
            if (username.lower() not in placement_names) and (team.lower() not in placement_names):
                print(f"Warning: Extra player in top cut: Place {rank}, Username '{username}', Players/Teams '{team}'")

    df.to_csv(output_file, index=False)
    print(f"Unified placements written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unify placements with standings.")
    parser.add_argument("placements_file", nargs="?", help="Placements .txt file")
    parser.add_argument("--all", action="store_true", help="Process all *_placements.txt files in the current folder")
    args = parser.parse_args()

    if args.all:
        files = glob.glob("*_placements.txt")
        if not files:
            print("No *_placements.txt files found in the current folder.")
            sys.exit(1)
        for placements_file in files:
            base_id = placements_file.split("_")[0]
            standings_file = find_standings_file(base_id)
            if not standings_file:
                # print(f"Could not find standings file for base ID {base_id}")
                continue
            output_file = standings_file.replace(".csv", "_unified.csv")
            print(f"\nProcessing {placements_file} with {standings_file}...")
            unify_placements(placements_file, standings_file, output_file)
    else:
        if not args.placements_file:
            print("Usage: python unify_placements.py <placements.txt> [--all]")
            sys.exit(1)
        placements_file = args.placements_file
        base_id = placements_file.split("_")[0]
        standings_file = find_standings_file(base_id)
        if not standings_file:
            # print(f"Could not find standings file for base ID {base_id}")
            sys.exit(1)
        output_file = standings_file.replace(".csv", "_unified.csv")
        unify_placements(placements_file, standings_file, output_file)
