from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv


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
        """Wait for the user to complete the login process."""
        print("Please complete the login process manually.")
        try:
            WebDriverWait(self.driver, 300).until(EC.url_contains("syndicates/all"))
            print("Login detected, proceeding to scrape data...")
        except Exception as e:
            print("Timeout while waiting for login. Please try again.")
            raise e

    def click_load_more(self):
        """Click the 'Load More' button until no longer available."""
        while True:
            try:
                # Wait for the 'Load More' button to be clickable
                load_more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "styles_loadMoreButton__PXBu3"))
                )
                print("Clicking 'Load More' button...")
                load_more_button.click()
                time.sleep(2)  # Wait for the new content to load

            except Exception as e:
                print("No more 'Load More' button found or an error occurred.")
                print(f"Exception: {e}")
                break

    def scrape_data(self):
        """Scrape the required data."""
        try:
            print("Waiting for the table to load...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "styles_tableContainer__957m_"))
            )

            # Scrape company names
            company_elements = self.driver.find_elements(By.CLASS_NAME, "styles_text__lPwQ1")
            company_names = [elem.text for elem in company_elements]

            # Scrape stages
            stage_elements = self.driver.find_elements(By.CLASS_NAME, "styles_gray__bdOHv")
            stages = [elem.text for elem in stage_elements]

            # Scrape dealflows
            dealflow_elements = self.driver.find_elements(By.CLASS_NAME, "styles_text__stjMD")
            dealflows = [elem.text for elem in dealflow_elements if elem.text in ['High', 'Medium', 'Low', 'New']]

            print(f"Found {len(company_names)} companies, {len(stages)} stages, and {len(dealflows)} dealflows.")
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
            writer.writerow(["Company", "Stage", "Dealflow"])
            for company, stage, dealflow in zip(data["companies"], data["stages"], data["dealflows"]):
                writer.writerow([company, stage, dealflow])


# Main execution
if __name__ == "__main__":
    URL = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
    DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
    #URL = "https://venture.angellist.com/v/gamha-islem-fatma/i/gamha-islem-fatma/syndicates/all"
    # DRIVER_PATH = r"C:\Users\Fatma\Downloads\edgedriver_win64\msedgedriver.exe"

    scraper = StartupScraper(DRIVER_PATH, URL)

    try:
        scraper.setup_driver()
        scraper.wait_for_login()

        # Click "Load More" until the end of the list
        scraper.click_load_more()

        # Scrape the data
        data = scraper.scrape_data()

        if data:
            print("\nFinal Results:")
            print("COMPANIES:", len(data["companies"]))
            print("STAGES:", len(data["stages"]))
            print("DEALFLOWS:", len(data["dealflows"]))

            # Save the data to a CSV file
            scraper.save_to_csv(data)
            print("Data saved to scraped_data.csv")
    finally:
        # Close the browser only at the end
        scraper.close_driver()
