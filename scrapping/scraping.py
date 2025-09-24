from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json

class StartupScraper:
    def __init__(self, driver_path, url):
        self.driver_path = driver_path
        self.url = url
        self.driver = None

    def setup_driver(self):
        """Set up the Selenium WebDriver."""
        service = Service(self.driver_path)
        self.driver = webdriver.Edge(service=service)
        self.driver.get(self.url)

    def wait_for_login(self):
        """Wait for manual login and confirm the correct page."""
        print("Please complete the login process manually.")
        input("Press Enter after you have successfully logged in...")

        # Verify if the user is on the correct page
        current_url = self.driver.current_url
        print(f"Current URL after login: {current_url}")
        if "syndicates/all" not in current_url:
            print("Redirecting to the target URL...")
            self.driver.get(self.url)
            time.sleep(5)

    def scrape_data(self):
        """Scrape the required data."""
        try:
            # Wait for the table container to load
            print("Waiting for the table to load...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "styles_tableContainer__957m_")
                )
            )

            # Scrape company names
            company_elements = self.driver.find_elements(
                By.CLASS_NAME, "styles_text__lPwQ1")
            company_names = [elem.text for elem in company_elements]
            print(f"Found {len(company_names)} companies.")

            # Handle dynamic parent classes for stages and dealflows
            stages, dealflows = [], []
            valid_dealflows = ['High', 'Low', 'Medium', 'New']

            # Scrape stages
            stage_elements = self.driver.find_elements(
                By.CLASS_NAME, "styles_gray__bdOHv")
            stages.extend([elem.text for elem in stage_elements if elem.text != "Medium"])

            # Scrape dealflows
            dealflow_elements = self.driver.find_elements(
                By.CLASS_NAME, "styles_text__stjMD")
            dealflows.extend(
                [elem.text for elem in dealflow_elements if elem.text in valid_dealflows]
            )

            print(f"Found {len(stages)} stages and {len(dealflows)} dealflows.")

            # Return the collected data
            return {
                "companies": company_names,
                "stages": stages,
                "dealflows": dealflows,
            }

        except Exception as e:
            print("An error occurred during scraping:", e)
            return None

    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()

    def save_to_csv(self, data, filename="scraped_data.csv"):
        """Save the scraped data to a CSV file."""
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Header
            writer.writerow(["Company", "Stage", "Dealflow"])
            # Data
            for company, stage, dealflow in zip(data['companies'], data['stages'], data['dealflows']):
                writer.writerow([company, stage, dealflow])


# Using the StartupScraper class
if __name__ == "__main__":
    URL = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
    DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
    #DRIVER_PATH = r"C:\Users\Fatma\Downloads\edgedriver_win64\msedgedriver.exe"


    # Instance of StartupScraper
    scraper = StartupScraper(DRIVER_PATH, URL)

    try:
        # Set up the driver & scrape data
        scraper.setup_driver()
        scraper.wait_for_login()
        scraped_data = scraper.scrape_data()

        # Results
        if scraped_data:
            print("\Final Results:")
            print("COMPANIES: ", scraped_data["companies"])
            print("STAGES: ", scraped_data["stages"])
            print("DEALFLOWS: ", scraped_data["dealflows"])

            # Save data to CSV
            scraper.save_to_csv(scraped_data)
            print("Data saved to scraped_data.csv")

    finally:
        # Close the driver
        scraper.close_driver()