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
        """Wait for me to log in :( so cute."""
        print("Please complete the login process manually.")
        input("Press Enter after you have successfully logged in...")

    def scrape_data(self):
        """Scrape the required data."""
        try:
            # i used webdriver to automate web browsers and interact with dynamic web pages
            # Wait for the table container to load :(
            WebDriverWait(self.driver, 20).until(
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
            ss = ["styles_gray__bdOHv"]
            dynamic_classes = [
                "styles_orange__OGK6l", "styles_gray__bdOHv",
                "styles_green__GmSPW", "styles_blue__HN_uy"
            ]  # dealflows has a lot of classes depend on their advancement in the process

            stages, dealflows = [], []
            for st in ss:
                # Scrape stages using class name in ss
                try:
                    stage_elements = self.driver.find_elements(
                        By.CLASS_NAME, st)
                    # remove medium because it is not a stage
                    stages.extend(
                        [elem.text for elem in stage_elements if elem.text != "Medium"])
                except Exception as e:
                    print(f"Error in stages: {e}")

            for dynamic_class in dynamic_classes:
                # Scrape dealflows using class name
                try:
                    # Find all elements with the class name that likely contains dealflow information
                    dealflow_elements = self.driver.find_elements(
                        By.CLASS_NAME, "styles_text__stjMD")

                    # Define the valid dealflow types
                    # to extract only the dealflows from the list because it give the stages too
                    valid_dealflows = ['High', 'Low', 'Medium', 'New']

                    # Filter and collect only the dealflows that match the valid ones
                    dealflows.extend(
                        [elem.text for elem in dealflow_elements if elem.text in valid_dealflows]
                    )

                except Exception as e:
                    print(
                        f"Error scraping dealflows for class {dynamic_class}: {e}")

            print(
                f"Found {len(stages)} stages and {len(dealflows)} dealflows.")

            # Return the collected data
            return {
                "companies": company_names,
                "stages": stages,
                "dealflows": dealflows,
            }

        except Exception as e:  # lets hope we dont reach this point
            print("An error occurred during scraping:", e)
            return None

    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()

    def save_to_csv(data, filename="scraped_data.csv"):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Header
            writer.writerow(["Company", "Stage", "Dealflow"])
            # Data
            for company, stage, dealflow in zip(data['companies'], data['stages'], data['dealflows']):
                writer.writerow([company, stage, dealflow])



# Using the StartupScraper class
if __name__ == "__main__":

    #DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe
    #URL = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
    DRIVER_PATH = r"C:\Users\Fatma\Downloads\edgedriver_win64\msedgedriver.exe"
    URL = "https://venture.angellist.com/v/gamha-islem-fatma/i/gamha-islem-fatma/syndicates/all"

    # Instance of StartupScraper
    scraper = StartupScraper(DRIVER_PATH, URL)

    try:
        # Set up the driver & scrape data
        scraper.setup_driver()
        scraper.wait_for_login()
        scraped_data = scraper.scrape_data()

        # Results
        if scraped_data:
            print("\nFinal Results:")
            print("COMPANIES: ", scraped_data["companies"])
            print("STAGES: ", scraped_data["stages"])
            print("DEALFLOWS: ", scraped_data["dealflows"])

    finally:
        # Close the driver
        scraper.close_driver()

# scraping description ,deals per month,founder.. if needed
# next part scraping the data to a csv file
