import argparse
import os
import requests
from bs4 import BeautifulSoup
import melee_scraper
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
        # Date filtering logic
        if date:
            if row_date != date:
                continue
        else:
            if start_date and row_date < start_date:
                continue
            if end_date and row_date > end_date:
                continue
        link_tag = cols[1].find("a", href=True)
        if link_tag:
            link = link_tag["href"]
            if not link.startswith("http"):
                link = "https://www.swu-competitivehub.com" + link
            tournament_links.append(link)

    return tournament_links

def scrape_tournament_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Get the href with id "link_text-238-135"
    melee_link_tag = soup.find("a", id="link_text-238-135")
    melee_link = melee_link_tag["href"] if melee_link_tag else None
    if melee_link == "https://www.youtube.com/watch?v=QV2Ba50-sp8":
        melee_link = "https://melee.gg/Tournament/View/270964"
    elif melee_link == "https://melee.gg/":
        melee_link = "https://melee.gg/Tournament/View/214500"

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

# Function to forcefully close the cookie popup
# def close_cookie_popup():
#     try:
#         # Attempt to click the "Necessary cookies only" button directly
#         cookie_button = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.XPATH, '//p[contains(text(), "Do not consent")]'))
#         )
#         cookie_button.click()
#         print("Cookie popup accepted (direct click).")
#     except:
#         print("No standard cookie button found. Trying forceful removal.")

#     # Try removing the popup directly using JavaScript
#     try:
#         driver.execute_script("""
#             document.querySelectorAll('.cookies__modal').forEach(el => {
#                 el.remove();
#             });
#         """)
#         print("Cookie popup forcefully removed.")
#     except Exception as e:
#         print("Failed to remove cookie popup.")
#         raise e

if __name__ == "__main__":
    args = parse_args()
    links = fetch_tournament_links(
        date=args.date,
        start_date=args.start_date,
        end_date=args.end_date
    )
    linkNumber = 1
    totalNumber = len(links)
    for link in tqdm(links, desc="Tournaments", unit="tournament", bar_format='{l_bar}{bar:30}{r_bar}{bar:-30b}'):
        data = scrape_tournament_page(link)
        filename = data['melee_link'].split("/")[-1] + "_placements.txt"
        if not os.path.exists(filename):
            for result in data["results"]:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(f"{result['placement']}: {result['player']}\n")

        if data['melee_link'] and (data["melee_link"].startswith("https://melee.gg/") or data["melee_link"].startswith("https://www.melee.gg/")):
            output_file = f"{data['melee_link'].split('/')[-1]}_standings.csv"
            if not os.path.exists(output_file) and not os.path.exists(f"{data['melee_link'].split('/')[-1]}_standings_incomplete.csv"):
                melee_scraper.scrape_tournament(data['melee_link'])
        else:
            print(f"Invalid Melee link: {data['melee_link']}")
