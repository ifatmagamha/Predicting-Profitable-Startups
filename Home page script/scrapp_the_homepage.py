from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


class HomepageScraper:
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
            # Wait for the URL to indicate login success
            WebDriverWait(self.driver, 300).until(
                EC.url_contains("syndicates/all")
            )
            print("Login detected, proceeding to scrape homepage...")
        except Exception as e:
            print("Timeout while waiting for login.")
            raise e

    def scrape_homepage_script(self):
        """Scrape the entire HTML content of the homepage."""
        try:
            print("Waiting for the homepage content to load...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "html"))
            )
            # Get the page source (complete HTML)
            page_source = self.driver.page_source
            print("Successfully scraped the homepage.")
            return page_source
        except Exception as e:
            print("An error occurred while scraping the homepage:", e)
            return None

    def save_html_to_file(self, html_content, filename="homepage.html"):
        """Save the HTML content to a file."""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(html_content)
        print(f"HTML content saved to {filename}.")

    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()


# Main Execution
if __name__ == "__main__":
<<<<<<< Updated upstream:Home page script/scrapp_the_homepage.py
    URL = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
    DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
=======
    DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
    URL = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
    # URL = "https://venture.angellist.com/v/gamha-islem-fatma/i/gamha-islem-fatma/syndicates/all"
    # DRIVER_PATH = r"C:\Users\Fatma\Downloads\edgedriver_win64\msedgedriver.exe"
>>>>>>> Stashed changes:scrapping/Home page script/scrapp_the_homepage.py

    scraper = HomepageScraper(DRIVER_PATH, URL)

    try:
        scraper.setup_driver()
        scraper.wait_for_login()

        # Scrape the homepage script
        html_content = scraper.scrape_homepage_script()

        if html_content:
            # Save to file
            scraper.save_html_to_file(html_content)
    finally:
        scraper.close_driver()
