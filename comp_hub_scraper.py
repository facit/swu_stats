#!/usr/bin/env python3
"""comp_hub_scraper.py
Scrape SWU Competitive Hub tournaments and their results.
This script fetches tournament links from the SWU Competitive Hub website,
scrapes the tournament pages for results, and saves the data into a SQLite database.
It also downloads the Melee.gg links for each tournament and saves the results in text files.
Usage
-------
    python comp_hub_scraper.py [--date YYYY-MM-DD] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]

If `--date` is specified, it scrapes tournaments for that specific date.
If `--start-date` is specified, it scrapes tournaments from that date onwards.
If `--end-date` is specified, it scrapes tournaments up to that date.
If both `--start-date` and `--end-date` are specified, it scrapes tournaments within that range.

If no arguments are provided, it scrapes all tournaments listed on the SWU Competitive Hub website.
"""
import argparse
import os
import requests
import country_converter as coco
from bs4 import BeautifulSoup
import melee_scraper
import sqlite3
from datetime import datetime
from tqdm import tqdm

BASE_URL = "https://www.swu-competitivehub.com/tournaments-results/"

def parse_args():
    parser = argparse.ArgumentParser(description="Scrape SWU tournaments by date.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", type=str, help="Scrape tournaments for a specific date (YYYY-MM-DD)")
    group2 = parser.add_argument_group("date range")
    group2.add_argument("--start-date", type=str, help="Earliest date to scrape (YYYY-MM-DD)")
    group2.add_argument("--end-date", type=str, help="Last date to scrape (YYYY-MM-DD)")
    return parser.parse_args()

def fetch_tournament_links(url=BASE_URL, date=None, start_date=None, end_date=None):
    # Convert start_date and end_date to datetime.date if they are not None
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    tournament_links = []

    table = soup.find("table", id="tableTournaments")
    if not table:
        return tournament_links

    tbody = table.find("tbody")
    if not tbody:
        return tournament_links

    for row in tbody.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        row_date = cols[0].get_text(strip=True)
        row_name = cols[1].get_text(strip=True)
        row_location = cols[3].find("img")["alt"] if cols[2].find("img") else ""
        # convert location to iso2 format
        cc = coco.CountryConverter()
        row_location = cc.convert(names=row_location, to="ISO2")
        row_level = cols[4].get_text(strip=True)

        # Date filtering logic
        if date:
            if row_date != date:
                continue
        else:
            # Convert date string to datetime object for comparison 
            current_date = datetime.strptime(row_date, "%Y-%m-%d").date()

            if start_date and current_date < start_date:
                continue
            if end_date and current_date > end_date:
                continue
        link_tag = cols[1].find("a", href=True)
        if link_tag:
            link = link_tag["href"]
            if not link.startswith("http"):
                link = "https://www.swu-competitivehub.com" + link
            tournament_links.append({"link": link, "date": row_date, "name": row_name, "location": row_location, "level": row_level})

    return tournament_links

def scrape_tournament_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Get the href with id "link_text-238-135"
    melee_link_tag = soup.find("a", id="link_text-238-135")
    melee_link = melee_link_tag["href"] if melee_link_tag else None

    # Get results from table with id "tableResults"
    results = []
    table = soup.find("table", id="tableResults")
    if table:
        tbody = table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 4:
                    placement = cols[0].get_text(strip=True)
                    player = cols[3].get_text(strip=True)
                    results.append({"placement": placement, "player": player})

    return {"melee_link": melee_link, "results": results}

if __name__ == "__main__":
    args = parse_args()
    links = fetch_tournament_links(
        date=args.date,
        start_date=args.start_date,
        end_date=args.end_date
    )
    linkNumber = 1
    totalNumber = len(links)
    conn = sqlite3.connect("swu_meta.db")
    cursor = conn.cursor()

    for link in tqdm(links, desc="Tournaments", unit="tournament", bar_format='{l_bar}{bar:30}{r_bar}{bar:-30b}'):
        data = scrape_tournament_page(link["link"])
        filename = data['melee_link'].split("/")[-1] + "_placements.txt"
        if not os.path.exists(filename):
            # Add tournament information to sqlite database
            # We'll assume your DB identifies a tournament uniquely by date+name+location+level
            cursor.execute("""
            SELECT tournament_id
            FROM tournaments
            WHERE date = ? AND name = ?
            """, (link['date'], link['name']))

            if cursor.fetchone() is None:
                # Insert new tournament
                print(f" Processing {linkNumber}/{totalNumber}: {link['name']} on {link['date']}")
                cursor.execute("""
                INSERT INTO tournaments (date, level, location, name, link)
                VALUES (?, ?, ?, ?, ?)
                """, (link['date'], link['level'], link['location'], link['name'], data['melee_link']))
                conn.commit()

            with open(filename, "w", encoding="utf-8") as f:
                for result in data["results"]:
                    if result['placement'] and result['player']:
                        # Write each placement to the file
                        f.write(f"{result['placement']}: {result['player']}\n")

        if (data['melee_link'] and (data["melee_link"].startswith("https://melee.gg/") or data["melee_link"].startswith("https://www.melee.gg/"))):
            output_file = f"{data['melee_link'].split('/')[-1]}_standings.csv"
            if not os.path.exists(output_file) and not os.path.exists(f"{data['melee_link'].split('/')[-1]}_standings_incomplete.csv"):
                melee_scraper.scrape_tournament(data['melee_link'])
        else:
            print(f" Invalid Melee link: {data['melee_link']}")
