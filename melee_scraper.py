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

# Setup Selenium with Chrome (headless for efficiency)
options = Options()
options.headless = False  # Set to False for debugging (see the browser)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

parser = argparse.ArgumentParser(description="Melee.gg Tournament Scraper")
parser.add_argument("url", help="Melee.gg tournament URL")
parser.add_argument("output", help="Output CSV file")
args = parser.parse_args()

data = []

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Target tournament URL
# url = "https://melee.gg/Tournament/View/291842"
driver.get(args.url)

# Custom Parsing Functions
def parse_misc(cell):
    return [cell.text.strip()]

def parse_player(cell):
    # Example: Extract player name, handle any extra details if needed
    try:
        player_container = cell.find_element(By.XPATH, ".//div[contains(@class, 'match-table-player-container')]/a")
        return [player_container.get_attribute("href").split("/")[-1].strip(), cell.text.strip()]
    except NoSuchElementException:
        return ["", ""]

def parse_decklist(cell):
    # Example: Clean decklist text, remove unnecessary characters
    try:
        player_container = cell.find_element(By.XPATH, ".//div[contains(@class, 'match-table-player-container')]/a")
    except NoSuchElementException:
        return ["", "", ""]
    deck = player_container.text.strip().split(" - ")
    leader = deck[0]
    base = deck[1]
    deck_link = player_container.get_attribute("href")
    return [leader, base, deck_link]

def parse_record(cell):
    # Example: Parse match record "3-1" into a tuple (wins, losses)
    raw_text = cell.text.strip()
    if "-" in raw_text:
        try:
            wins, losses, draws = map(int, raw_text.split("-"))
            return [wins, losses, draws]
        except ValueError:
            return [0, 0, 0]  # Default for invalid format
    return [0, 0, 0]  # Default if no data

# Dictionary mapping column classes to parsing functions
column_parsers = {
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

# Function to forcefully close the cookie popup
def close_cookie_popup():
    try:
        # Attempt to click the "Necessary cookies only" button directly
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Necessary cookies only")]'))
        )
        cookie_button.click()
        print("Cookie popup accepted (direct click).")
    except:
        print("No standard cookie button found. Trying forceful removal.")

    # Try removing the popup directly using JavaScript
    try:
        driver.execute_script("""
            document.querySelectorAll('.cookies__modal').forEach(el => {
                el.remove();
            });
        """)
        print("Cookie popup forcefully removed.")
    except Exception as e:
        print("Failed to remove cookie popup.")
        raise e

# Ensure the cookie popup is closed
close_cookie_popup()

# Wait for the main standings table to load using the precise XPath
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="tournament-standings-table"]'))
)

# Initialize ActionChains for mouse scroll simulation
actions = ActionChains(driver)

def split_headers(headers):
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

# Function to extract table data with fresh table capture
def extract_table_data():
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
            for td_class, parser in column_parsers.items():
                try:
                    cell = row.find_element(By.XPATH, ".//td[contains(@class, '" + td_class + "')]")
                    cell_texts += parser(cell)
                except NoSuchElementException as e:
                    continue

            # If any cell is empty, we need to scroll more
            if any(cell == "" for cell in cell_texts):
                return None, None  # Incomplete rows detected

            new_data.append(cell_texts)

        return new_headers, new_data
    except Exception as e:
        return None, None

def press_next_button(page_number):
    # Check for next page button
    try:
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        for i in range(4):
            driver.execute_script("window.scrollBy(0, 500)")  # Scroll down by 500 pixels
            time.sleep(0.3)
        next_button = driver.find_element(By.XPATH, "//*[contains(@class, 'paginate_button') and contains(@class, 'next')]")
        if "disabled" in next_button.get_attribute("class"):
            return -1
        next_button.click()
        time.sleep(2)  # Allow time for the next page to load
        driver.execute_script("window.scrollTo(0, 0)")  # Scroll down by 500 pixels
        return page_number + 1
    except NoSuchElementException as e:
        return -1
    except ElementClickInterceptedException as e:
        return -1
        
def load_page(headers):
    # Keep trying until all rows are fully loaded
    attempts = 0
    max_attempts = 50  # To prevent infinite loop
    new_headers = None
    new_data = None

    time.sleep(2)  # Allow time for the next page to load

    while attempts < max_attempts:
        new_headers, new_data = extract_table_data()
        if new_headers and new_data:
            break

        # Use ActionsChains to scroll like a real user
        actions.move_to_element(driver.find_element(By.TAG_NAME, "body"))
        actions.scroll_by_amount(0, 50).perform()
        time.sleep(0.1)
        attempts += 1

    data.extend(new_data)
    if headers == []:
        headers = new_headers
    
    if not new_data:
        driver.quit()
        exit(1)
        
    return headers
        
# Function to check if a round has results
def check_round_has_results():
    try:
        print("Checking if the round has results...")
        table_wrapper = driver.find_element(By.XPATH, './/*[@id="tournament-standings-table_wrapper"]')
        empty_row = table_wrapper.find_element(By.XPATH, ".//*[contains(@class, 'dataTables_scroll')]//td[contains(@class, 'dataTables_empty')]")
        print("No results found in this round.")
        return False
    except NoSuchElementException:
        print("Results found in this round.")
        return True

# Function to switch to the previous round if no results
def switch_to_previous_round():
    print("Switching to the previous round...")
    selector_container = driver.find_element(By.ID, "standings-round-selector-container")
    active_button = selector_container.find_element(By.CLASS_NAME, "active")
    all_buttons = selector_container.find_elements(By.CLASS_NAME, "round-selector")

    for i, button in enumerate(all_buttons):
        if button == active_button and i > 0:  # Find the button to the left
            previous_button = all_buttons[i - 1]
            print(f"Switching to round: {previous_button.text}")
            previous_button.click()
            time.sleep(2)  # Allow time for the page to load
            return

def main():
    # Ensure we are on a round with results
    while not check_round_has_results():
        print("No results in current round. Switching to the previous round.")
        time.sleep(1)
        switch_to_previous_round()

    page_number = 1
    headers = []
    while True:
        headers = load_page(headers)
        new_page_number = press_next_button(page_number)
        if new_page_number == -1:
            break
        page_number = new_page_number

    # Close the browser
    driver.quit()

    headers = split_headers(headers)

    # Convert to DataFrame for easy handling
    df = pd.DataFrame(data, columns=headers)

    # Save the data to a CSV file (optional)
    df.to_csv(args.output, index=False)
    
    print("Saved melee file as \"" + args.output + "\"")

main()