from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import logging

# Suppress SSL certificate-related errors
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('selenium').setLevel(logging.ERROR)


def scrape_team_stats(url):
    # Set up Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    # Ignore SSL errors
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    # Set logging preferences to suppress INFO level logs
    chrome_options.add_argument("--log-level=3")

    # Update the path to match the location of the ChromeDriver
    service = ChromeService(executable_path="C:\\Users\\schin\\Downloads\\chromedriver-win64 (1)\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(url)
    # Wait until both tables are loaded
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "teams_standard_pitching")),
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "teams_standard_batting")),
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "teams_standard_fielding")),
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "team_output")),
        )
    except Exception as e:
        print("Tables not found:", e)
        driver.quit()
        return None, None, None, None
    
    # Get page source and parse with BeautifulSoup
    page_source = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find both tables
    pitching_table = soup.find('table', {'id': 'teams_standard_pitching'})
    batting_table = soup.find('table', {'id': 'teams_standard_batting'})
    fielding_table = soup.find('table', {'id': 'teams_standard_fielding'})
    WAA_table = soup.find('table', {'id': 'team_output'})
    
    if not pitching_table or not batting_table or not fielding_table or not WAA_table:
        print("Could not find one or both tables on the page")
        return None, None
    
    # Extract column headers
    pitching_columns = [
        'Tm', '#P', 'PAge', 'RA/G', 'W', 'L', 'W-L%', 'ERA', 'G', 'GS', 'GF', 'CG', 'tSho', 'cSho', 
        'SV', 'IP', 'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'SO', 'HBP', 'BK', 'WP', 'BF', 'ERA+', 'FIP', 
        'WHIP', 'H9', 'HR9', 'BB9', 'SO9', 'SO/W', 'LOB'
    ]

    batting_columns = [
        'Tm', '#Bat', 'BatAge', 'R/G', 'G', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 
        'RBI', 'SB', 'CS', 'BB', 'SO', 'BA', 'OBP', 'SLG', 'OPS', 'OPS+', 'TB', 'GDP', 
        'HBP', 'SH', 'SF', 'IBB', 'LOB'
    ]

    fielding_columns = [
        'Tm', '#Fld', 'RA/G', 'DefEff', 'G', 'GS', 'CG', 
        'Inn', 'Ch', 'PO', 'A', 'E', 'DP', 'Fld%', 'Rtot', 
        'Rtot/yr', 'Rdrs', 'Rdrs/yr', 'Rgood'
    ]

    WAA_columns = [
        'Rk', 'Total', 'All P', 'SP', 'RP', 'Non-P', 'C', 
        '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'OF (All)', 
        'DH', 'PH'
    ]

    
    # Extract data from pitching table
    pitching_stats = []
    for row in pitching_table.find_all('tr')[1:]:
        cols = row.find_all(['th', 'td'])
        if len(cols) == len(pitching_columns):
            pitching_stats.append({pitching_columns[i]: col.text.strip() for i, col in enumerate(cols)})
        else:
            print(f"Skipping row due to column mismatch in pitching table: {row}")
    
    # Extract data from batting table
    batting_stats = []
    for row in batting_table.find_all('tr')[1:]:
        cols = row.find_all(['th', 'td'])
        if len(cols) == len(batting_columns):  
            batting_stats.append({batting_columns[i]: col.text.strip() for i, col in enumerate(cols)})
        else:
            print(f"Skipping row due to column mismatch in batting table: {row}")

    # Extract data from fielding table
    fielding_stats = []
    for row in fielding_table.find_all('tr')[1:]:
        cols = row.find_all(['th', 'td'])
        if len(cols) == len(fielding_columns):
            fielding_stats.append({fielding_columns[i]: col.text.strip() for i, col in enumerate(cols)})
        else:
            print(f"Skipping row due to column mismatch in fielding table: {row}")
    
    WAA_stats = []
    for row in WAA_table.find_all('tr')[1:]:
        cols = row.find_all(['th', 'td'])
        if len(cols) == len(WAA_columns):
            WAA_stats.append({WAA_columns[i]: col.text.strip() for i, col in enumerate(cols)})
        else:
            print(f"Skipping row due to column mismatch in fielding table: {row}")
    
    return pitching_stats, batting_stats, fielding_stats, WAA_stats

def scrape_standings(standings_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    # Ignore SSL errors
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--log-level=3")

    service = ChromeService(executable_path="C:\\Users\\schin\\Downloads\\chromedriver-win64 (1)\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(standings_url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "expanded_standings_overall")),
        )
    except Exception as e:
        print("Standings table not found:", e)
        driver.quit()
        return None
    
    # Get page source and parse with BeautifulSoup
    page_source = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find the standings table
    standings_table = soup.find('table', {'id': 'expanded_standings_overall'})
    
    if not standings_table:
        print("Standings table not found")
        return None
    
    # Extract column headers from the standings table
    standings_columns = [
        'Rk', 'Tm', 'W', 'L', 'W-L%', 'GB', 'Strk', 'R', 'RA', 'Home', 'Road', 'ExInn', '1Run', 
        'vRHP', 'vLHP', 'last10', 'last20', 'last30', 'POff', 'PDef', 'PStrt', 'PLtng', 'RS', 'RA'
    ]

    # Extract data from the standings table
    standings_data = []
    for row in standings_table.find_all('tr')[1:]:
        cols = row.find_all(['th', 'td'])
        if len(cols) == len(standings_columns):  # Ensure the number of columns matches the expected number
            standings_data.append({standings_columns[i]: col.text.strip() for i, col in enumerate(cols)})
        else:
            print(f"Skipping row due to column mismatch in standings table: {row}")
    
    return standings_data

def main():
    url = "https://www.baseball-reference.com/leagues/majors/2023.shtml"
    standings_url = "https://www.baseball-reference.com/leagues/majors/2023-standings.shtml"

    # Scrape team pitching and batting stats
    pitching_stats, batting_stats, fielding_stats, WAA_stats = scrape_team_stats(url)
    if pitching_stats and batting_stats and fielding_stats and WAA_stats:
        # Convert to DataFrames
        pitching_stats_df = pd.DataFrame(pitching_stats)
        batting_stats_df = pd.DataFrame(batting_stats)
        fielding_stats_df = pd.DataFrame(fielding_stats)
        WAA_stats_df = pd.DataFrame(WAA_stats)

        # Save to CSV
        pitching_filename = "team_pitching_stats_2023.csv"
        pitching_stats_df.to_csv(pitching_filename, index=False)
        print(f"Team pitching stats saved to {pitching_filename}")

        batting_filename = "team_batting_stats_2023.csv"
        batting_stats_df.to_csv(batting_filename, index=False)
        print(f"Team batting stats saved to {batting_filename}")

        fielding_filename = "team_fielding_stats_2023.csv"
        fielding_stats_df.to_csv(fielding_filename, index=False)
        print(f"Team fielding stats saved to {fielding_filename}")

        WAA_filename = "team_WAA_stats_2023.csv"
        WAA_stats_df.to_csv(WAA_filename, index=False)
        print(f"Team WAA stats saved to {WAA_filename}")
    
    # Scrape standings
    standings_data = scrape_standings(standings_url)
    if standings_data:
        standings_df = pd.DataFrame(standings_data)
        standings_filename = "team_standings_2023.csv"
        standings_df.to_csv(standings_filename, index=False)
        print(f"Team standings saved to {standings_filename}")

if __name__ == "__main__":
    main()

