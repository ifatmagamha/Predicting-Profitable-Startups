from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time


class StartupScraper:
    def __init__(self, driver_path, base_url):
        self.driver_path = driver_path
        self.base_url = base_url
        self.driver = None

    def setup_driver(self):
        """Set up the Selenium WebDriver."""
        service = Service(self.driver_path)
        self.driver = webdriver.Edge(service=service)
        self.driver.get(self.base_url)

    def wait_for_login(self):
        """Wait for manual login."""
        print("Please complete the login process manually.")
        input("Press Enter after you have successfully logged in...")

    def scrape_company_links(self):
        """Scrape the links to company pages from the homepage."""
        try:
            # Wait for company links to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "styles_text__lPwQ1"))
            )

            # Scrape all company links
            company_elements = self.driver.find_elements(By.CLASS_NAME, "styles_text__lPwQ1")
            company_links = [elem.text for elem in company_elements]

            print(f"Found {len(company_links)} company links.")
            return company_links

        except Exception as e:
            print("Error scraping company links:", e)
            return []


    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()


def save_to_csv(data, filename="companies_data.csv"):
    """Save scraped data to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "stage", "dealflow", "revenue", "geography", "market"])
        writer.writeheader()
        writer.writerows(data)


# Using the StartupScraper class
if __name__ == "__main__":
    DRIVER_PATH = r"C:\Users\Fatma\Downloads\edgedriver_win64\msedgedriver.exe"
    BASE_URL = "https://venture.angellist.com/v/gamha-islem-fatma/i/gamha-islem-fatma/syndicates/all"

    scraper = StartupScraper(DRIVER_PATH, BASE_URL)

    try:
        # Set up the driver & log in manually
        scraper.setup_driver()
        scraper.wait_for_login()

        # Scrape all company links
        company_links = scraper.scrape_company_links()

    finally:
        scraper.close_driver()
