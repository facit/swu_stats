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

# Function to extract table data with fresh table capture
def extract_table_data():
    new_data = None
    new_headers = None
    try:
        table_wrapper = driver.find_element(By.XPATH, '//*[@id="tournament-standings-table_wrapper"]')
        dataTable = table_wrapper.find_element(By.XPATH, "//*[contains(@class, 'dataTables_scroll')]")
        tableHead = dataTable.find_element(By.XPATH, "//*[contains(@class, 'dataTables_scrollHead')]")
        headerRows = tableHead.find_elements(By.TAG_NAME, "tr")
        new_headers = [th.text.strip() for th in headerRows[0].find_elements(By.TAG_NAME, "th")]

        tableBody = dataTable.find_element(By.XPATH, "//*[contains(@class, 'dataTables_scrollBody')]")
        bodyRows = tableBody.find_elements(By.TAG_NAME, "tr")
        bodyRows = tableBody.find_elements(By.TAG_NAME, "tr")

        new_data = []

        for row in bodyRows[1:]:
            # Re-locate row cells to avoid stale reference
            cells = row.find_elements(By.TAG_NAME, "td")
            cell_texts = [cell.text.strip() for cell in cells]

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
        
def main():
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

    # Convert to DataFrame for easy handling
    df = pd.DataFrame(data, columns=headers)

    # Save the data to a CSV file (optional)
    df.to_csv(args.output, index=False)
    
    print("Saved melee file as \"" + args.output + "\"")

main()