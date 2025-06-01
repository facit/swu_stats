#!/usr/bin/env python3
"""melee_scraper.py
Scrape Melee.gg tournament standings and pairings.
This script fetches tournament data from Melee.gg, including standings and pairings,
and saves the results in CSV files. It can scrape either standings, pairings, or both.
Usage
-------
    python melee_scraper.py <tournament_url> [--mode standings|pairings|both]

If no mode is specified, it defaults to scraping standings.
The tournament URL should be the full link to the Melee.gg tournament page.

It will output two CSV files:
- `<tournament_id>_standings.csv` for standings data
- `<tournament_id>_pairings.csv` for pairings data
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import argparse
import re

# Setup Selenium with Chrome (headless for efficiency)
options = Options()
options.headless = True  # Set to False for debugging (see the browser)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

standings_data = []
matches_data = []

global driver, actions

# Custom Parsing Functions
def parse_misc(cell, players):
    return [cell.text.strip()]

def parse_player(cell, players):
    # Example: Extract player name, handle any extra details if needed
    try:
        player_container = cell.find_element(By.XPATH, ".//div[contains(@class, 'match-table-player-container')]/a")
        return [player_container.get_attribute("href").split("/")[-1].strip(), player_container.text.strip()]
    except NoSuchElementException:
        return ["", ""]

def parse_teams(cell, players):
    players = []
    try:
        player_containers = cell.find_elements(By.XPATH, ".//div[contains(@class, 'match-table-teams-container')]/div[contains(@class, 'match-table-team-container')]")
        player_container1 = player_containers[0]
        players += parse_player(player_container1, None)
        if(len(player_containers) > 1):
            player_container2 = player_containers[1]
            players += parse_player(player_container2, None)
        else:
            players += ["-", "-"]
        return players
    except NoSuchElementException:
        return ["", "", "", ""]
    
def parse_result(cell, players):
    match = re.match("(.+) won ([0-3]-[0-3]-[0-3])", cell.text.strip())
    if match:
        if players[1] == match.group(1):
            return match.group(2).split("-")
        elif players[3] == match.group(1):
            scores = match.group(2).split("-")
            score1 = scores[0]
            scores[0] = scores[1]
            scores[1] = score1
            return scores
    else:
        match = re.match("(.+) was assigned a bye", cell.text.strip())
        if match:
            return [2,0,0]
        else:
            match = re.match("([0-3]-[0-3]-[0-3]) Draw", cell.text.strip())
            if match:
                return match.group(1).split("-")
            
    return [0,0,0]
    
def parse_decklist(cell, players):
    try:
        player_container = cell.find_element(By.XPATH, ".//div[contains(@class, 'match-table-player-container')]/a")
    except NoSuchElementException:
        return ["-", "-", "-"]
    deck = player_container.text.strip().split(" - ")
    if len(deck) == 2:
        leader = deck[0]
        base = deck[1]
        deck_link = player_container.get_attribute("href")
        return [leader, base, deck_link]
    else:
        return ["-", "-", "-"]


def parse_decklists(cell, players):
    try:
        deck_data = []
        decks = cell.find_elements(By.XPATH, "./div[contains(@class, 'match-table-teams-container')]/div[contains(@class, 'match-table-team-container')]")
        deck_data += parse_decklist(decks[0], None)
        if (len(decks) > 1):
            deck_data += parse_decklist(decks[1], None)
        else:
            deck_data += ["-", "-", "-"]
        return deck_data
    except NoSuchElementException:
        return ["-", "-", "-","-", "-", "-"]

def parse_record(cell, players):
    raw_text = cell.text.strip()
    if "-" in raw_text:
        try:
            wins, losses, draws = map(int, raw_text.split("-"))
            return [wins, losses, draws]
        except ValueError:
            return [0, 0, 0]  # Default for invalid format
    return [0, 0, 0]  # Default if no standings_data

# Dictionary mapping column classes to parsing functions
standings_column_parsers = {
    "Rank-column": parse_misc,
    "Player-column": parse_player,
    "Decklists-column": parse_decklist,
    "MatchRecord-column": parse_record,
    "GameRecord-column": parse_record,
    "Points-column": parse_misc,
    "OpponentMatchWinPercentage-column": parse_misc,
    "TeamGameWinPercentage-column": parse_misc,
    "OpponentGameWinPercentage-column": parse_misc
}

matches_column_parsers = {
    "TableNumber-column": parse_misc,
    "Teams-column": parse_teams,
    "Decklists-column": parse_decklists,
    "ResultString-column": parse_result
}

# Function to forcefully close the cookie popup
def close_cookie_popup():
    try:
        # Attempt to click the "Necessary cookies only" button directly
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Necessary cookies only")]'))
        )
        cookie_button.click()
    except:
        print("No standard cookie button found. Trying forceful removal.")

    # Try removing the popup directly using JavaScript
    try:
        driver.execute_script("""
            document.querySelectorAll('.cookies__modal').forEach(el => {
                el.remove();
            });
        """)
    except Exception as e:
        print("Failed to remove cookie popup.")
        raise e

def split_standings_headers(headers):
    new_headers = []
    for header in headers:
        if header == "Players/Teams":
            new_headers.append("Username")
            new_headers.append("Players/Teams")
        elif header == "Decklist":
            new_headers.append("Leader")
            new_headers.append("Base")
            new_headers.append("Decklink")
        elif header == "Match Record":
            new_headers.append("Match Wins")
            new_headers.append("Match Losses")
            new_headers.append("Match Draws")
        elif header == "Game Record":
            new_headers.append("Game Wins")
            new_headers.append("Game Losses")
            new_headers.append("Game Draws")
        else:
            new_headers.append(header)
    return new_headers

def split_matches_headers(headers):
    new_headers = ["Round"]
    for header in headers:
        if header == "Players/Teams":
            new_headers.append("Player1_username")
            new_headers.append("Player1_displayname")
            new_headers.append("Player2_username")
            new_headers.append("Player2_displayname")
        elif header == "Decklists":
            new_headers.append("Player1_leader")
            new_headers.append("Player1_base")
            new_headers.append("Player1_decklink")
            new_headers.append("Player2_leader")
            new_headers.append("Player2_base")
            new_headers.append("Player2_decklink")
        elif header == "Result":
            new_headers.append("Player1_wins")
            new_headers.append("Player2_wins")
            new_headers.append("Draws")
        else:
            new_headers.append(header)
    return new_headers
    
# Function to extract table standings_data with fresh table capture
def extract_standings_table_data():
    new_data = None
    new_headers = None
    try:
        headerRow = driver.find_element(By.XPATH, "//div[@id='tournament-standings-table_wrapper']/div[contains(@class, 'dataTables_scroll')]/div[contains(@class, 'dataTables_scrollHead')]//thead/tr")
        new_headers = [th.text.strip() for th in headerRow.find_elements(By.TAG_NAME, "th")]

        new_data = []

        tbody = driver.find_element(By.XPATH, "//div[@id='tournament-standings-table_wrapper']/div[contains(@class, 'dataTables_scroll')]/div[contains(@class, 'dataTables_scrollBody')]//tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cell_texts = []
            found_columns = []
            for td_class, parser in standings_column_parsers.items():
                if td_class in found_columns:
                    continue
                try:
                    tmp_cell = row.find_element(By.XPATH, ".//td[contains(@class, '" + td_class + "')]")
                    cell = tmp_cell
                    cell_texts += parser(cell, None)
                    found_columns.append(td_class)
                except NoSuchElementException as e:
                    continue

            # If any cell is empty, we need to scroll more
            if any(cell == "" for cell in cell_texts):
                return None, None  # Incomplete rows detected

            new_data.append(cell_texts)

        return new_headers, new_data
    except Exception as e:
        # print("exception")
        # print(e)
        # return None, None
        raise e

# Function to extract table matches_data with fresh table capture
def extract_matches_table_data(round):
    new_data = None
    new_headers = None
    try:
        headerRow = driver.find_element(By.XPATH, "//div[@id='tournament-pairings-table_wrapper']/div[contains(@class, 'dataTables_scroll')]/div[contains(@class, 'dataTables_scrollHead')]//thead/tr")
        new_headers = [th.text.strip() for th in headerRow.find_elements(By.TAG_NAME, "th")]

        new_data = []

        tbody = driver.find_element(By.XPATH, "//div[@id='tournament-pairings-table_wrapper']/div[contains(@class, 'dataTables_scroll')]/div[contains(@class, 'dataTables_scrollBody')]//tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cell_texts = [str(round)]
            found_columns = []
            players = []
            for td_class, parser in matches_column_parsers.items():
                if td_class in found_columns:
                    continue
                try:
                    cell = row.find_element(By.XPATH, ".//td[contains(@class, '" + td_class + "')]")
                    res = parser(cell, players)
                    cell_texts += res
                    if td_class == "Teams-column":
                        players = res
                    found_columns.append(td_class)
                except NoSuchElementException as e:
                    continue

            # If any cell is empty, we need to scroll more
            if any(cell == "" for cell in cell_texts):
                return None, None  # Incomplete rows detected

            new_data.append(cell_texts)

        return new_headers, new_data
    except Exception as e:
        # print("exception")
        # print(e)
        #return None, None
        raise e

def load_standings_from_page(headers):
    global standings_data
    # Keep trying until all rows are fully loaded
    actions.move_to_element(driver.find_element(By.ID, "standings-round-selector-container")).perform()
    attempts = 0
    max_attempts = 30  # To prevent infinite loop
    new_headers = None
    new_data = None

    time.sleep(1)  # Allow time for the next page to load

    while attempts < max_attempts:
        new_headers, new_data = extract_standings_table_data()
        if new_headers and new_data:
            break

        # Use ActionsChains to scroll like a real user
        actions.scroll_by_amount(0, 100).perform()
        time.sleep(0.1)
        attempts += 1

    if new_data is not None:
        standings_data.extend(new_data)

    if headers == []:
        headers = new_headers
    
    if not new_data:
        driver.quit()
        exit(1)
        
    return headers

def load_matches_from_page(headers, round):
    global matches_data
    # Keep trying until all rows are fully loaded
    actions.move_to_element(driver.find_element(By.ID, "pairings-round-selector-container")).perform()
    attempts = 0
    max_attempts = 30  # To prevent infinite loop
    new_headers = None
    new_data = None

    time.sleep(1)  # Allow time for the next page to load

    while attempts < max_attempts:
        new_headers, new_data = extract_matches_table_data(round)
        if new_headers and new_data:
            break

        # Use ActionsChains to scroll like a real user
        actions.scroll_by_amount(0, 100).perform()
        time.sleep(0.1)
        attempts += 1

    if new_data is not None:
        matches_data.extend(new_data)

    if headers == []:
        headers = new_headers
    
    if not new_data:
        driver.quit()
        exit(1)
        
    return headers

# Function to check if a round has results
def check_standings_for_round_has_results():
    try:
        table_wrapper = driver.find_element(By.XPATH, './/*[@id="tournament-standings-table_wrapper"]')
        table_wrapper.find_element(By.XPATH, ".//*[contains(@class, 'dataTables_scroll')]//td[contains(@class, 'dataTables_empty')]")
        return False
    except NoSuchElementException:
        return True

def elementHasClass(element, className):
    classes = element.get_attribute("class")
    for c in classes.split(" "):
        if (c == className):
            return True
    
    return False

# Function to switch to the previous round if no results
def switch_standings_to_previous_round():
    selector_container = driver.find_element(By.ID, "standings-round-selector-container")
    active_button = selector_container.find_element(By.CLASS_NAME, "active")
    all_buttons = selector_container.find_elements(By.XPATH, "//div[@id='standings-round-selector-container']/button[contains(@class, 'round-selector')]")

    for i, button in enumerate(all_buttons):
        if button == active_button and i > 0:  # Find the button to the left
            previous_button = all_buttons[i - 1]
            driver.execute_script("arguments[0].click();", previous_button)
            time.sleep(3)  # Allow time for the page to load
            return True
    
    return False

def switch_standings_to_next_page():
    # Check for next page button
    try:
        next_button = driver.find_element(By.XPATH, "//div[@id='tournament-standings-table_wrapper']//*[contains(@class, 'paginate_button') and contains(@class, 'next')]")
        actions.move_to_element(next_button).perform()
        if "disabled" in next_button.get_attribute("class"):
            return -1
        next_button.click()
        time.sleep(2)  # Allow time for the next page to load
        driver.execute_script("window.scrollTo(0, 0)")  # Scroll down by 500 pixels
    except NoSuchElementException as e:
        return -1
    except ElementClickInterceptedException as e:
        return -1
        
#############################################################################################
# Function to check if a round has pairings
def check_matches_for_round_has_pairings():
    try:
        table_wrapper = driver.find_element(By.XPATH, './/*[@id="tournament-matches-table_wrapper"]')
        empty_row = table_wrapper.find_element(By.XPATH, ".//*[contains(@class, 'dataTables_scroll')]//td[contains(@class, 'dataTables_empty')]")
        return False
    except NoSuchElementException:
        return True

# Function to switch to the first round
def switch_matches_to_first_round():
    #selector_container = driver.find_element(By.ID, "pairings-round-selector-container")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//div[@id='pairings-round-selector-container']/button[contains(text(), 'Round 1')]"))).click()
    
    time.sleep(2)  # Allow time for the page to load
    return

# Function to switch to the next round if no results
def switch_matches_to_next_round():
    active_button = driver.find_element(By.XPATH, "//div[@id='pairings-round-selector-container']/button[contains(@class, 'round-selector') and contains(@class, 'active')]")
    all_buttons = driver.find_elements(By.XPATH, "//div[@id='pairings-round-selector-container']/button[contains(@class, 'round-selector')]")

    active_button_found = False
    for i, button in enumerate(all_buttons):
        if button == active_button:  # Find the button to the Right
            active_button_found = True
        elif active_button_found:
            actions.move_to_element(button).perform()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(button)).click()
            time.sleep(2)  # Allow time for the page to load
            return True
    return False

def switch_matches_to_next_page():
    # Check for next page button
    try:
        next_button = driver.find_element(By.XPATH, "//div[@id='tournament-pairings-table_paginate']//*[contains(@class, 'paginate_button') and contains(@class, 'next')]")
        actions.move_to_element(next_button).perform()
        if "disabled" in next_button.get_attribute("class"):
            return -1
        next_button.click()
        time.sleep(2)  # Allow time for the next page to load
        driver.execute_script("window.scrollTo(0, 0)")  # Scroll to top of page
    except NoSuchElementException as e:
        return -1
    except ElementClickInterceptedException as e:
        return -1

def switch_matches_to_first_page():
    # Check for page 1 button
    try:
        first_button = driver.find_element(By.XPATH, "//div[@id='tournament-pairings-table_paginate']/span/a[contains(@class, 'paginate_button')]")
        actions.move_to_element(first_button).perform()
        first_button.click()
        time.sleep(2)  # Allow time for the next page to load
    except NoSuchElementException as e:
        return -1
    except ElementClickInterceptedException as e:
        return -1
        
def scrape_tournament(url, mode="standings"):
    if mode is None:
        mode = "standings"

    global standings_data, matches_data
    standings_data = []
    matches_data = []

    print(f"Melee link: {url}")

    global driver, actions
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Initialize ActionChains for mouse scroll simulation
    actions = ActionChains(driver)

    driver.get(url)

    # Ensure the cookie popup is closed
    close_cookie_popup()

    # Wait for the main standings table to load using the precise XPath
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="tournament-standings-table"]'))
    )

    output_file = f"{url.split('/')[-1]}_{mode}.csv"

    if(mode == "standings" or mode == "both"):
        # Ensure we are on a round with results
        while not check_standings_for_round_has_results():
            output_file = f"{url.split('/')[-1]}_{mode}_incomplete.csv"
            time.sleep(1)
            if not switch_standings_to_previous_round():
                return
        # Switch to the last round if not already there
        # Check that the last button of parent with id standings-round-selector-container has class "active"
        selector_container = driver.find_element(By.ID, "standings-round-selector-container")
        all_buttons = selector_container.find_elements(By.XPATH, ".//button[contains(@class, 'round-selector')]")
        if all_buttons:
            last_button = all_buttons[-1]
            if not elementHasClass(last_button, "active"):
                #create that file if it doesn't exist and make it empty
                output_file = f"{url.split('/')[-1]}_{mode}_incomplete.csv"
        else:
            driver.quit()
            exit(1)

        headers = []
        page_number = 1
        while page_number != -1:
            headers = load_standings_from_page(headers)
            page_number = switch_standings_to_next_page()

        headers = split_standings_headers(headers)
        # Convert to DataFrame for easy handling
        try:
            df = pd.DataFrame(standings_data, columns=headers)
        except ValueError as e:
            print("Error creating DataFrame. Check if the headers match the data.")
            return

        # Save the standings_data to a CSV file (optional)
        df.to_csv(output_file, index=False)
        
        print("Saved standings as \"" + output_file + "\"")

    if(mode == "pairings" or mode == "both"):
        switch_matches_to_first_round()
        headers = []
        round_number = 1
        while round_number != -1:
            page_number = 1
            while page_number != -1:
                headers = load_matches_from_page(headers, round_number)
                page_number = switch_matches_to_next_page()
            if not switch_matches_to_next_round():
                break
            switch_matches_to_first_page()
            if not check_matches_for_round_has_pairings():
                round_number = -1
            else:
                round_number += 1

        headers = split_matches_headers(headers)
        
        # Convert to DataFrame for easy handling
        df = pd.DataFrame(matches_data, columns=headers)

        # Save the matches_data to a CSV file (optional)
        df.to_csv(output_file, index=False)
        
        print("Saved pairings as \"" + output_file + "\"")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Melee.gg Tournament Scraper")
    parser.add_argument("url", help="Melee.gg tournament URL")
    parser.add_argument("--mode", help="Scrape standings, pairings or both")
    args = parser.parse_args()

    scrape_tournament(args.url, args.mode)