from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class StartupScraper:
    def __init__(self, driver_path, url):
        self.driver_path = driver_path
        self.url = url
        self.driver = None

    def setup_driver(self):
        """Set up the Selenium WebDriver."""
        service = Service(self.driver_path)
        # i used webdriver to automate web browsers and interact with dynamic web pages
        self.driver = webdriver.Edge(service=service)
        self.driver.get(self.url)

    def wait_for_login(self):
        """Wait for me to login :( so cute"""
        print("Please complete the login process manually.")
        input("Press Enter after you have successfully logged in...")

    def scrape_data(self):
        """Scrape the required data."""
        try:
            # i put 20s therefore the page can load comfortably :)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "styles_text__lPwQ1"))
            )  # i used WebDriverWait to wait until find the class name to be met before proceeding further in the code

            # Scrape company names
            # find_elements like find_all in beautifulsoup
            company_elements = self.driver.find_elements(
                By.CLASS_NAME, "styles_text__lPwQ1")
            # In Selenium, elem.text is used to extract the visible text content of a web element
            company_names = [elem.text for elem in company_elements]

            # Scrape stages
            stage_elements = self.driver.find_elements(
                By.XPATH, "//div[@class='styles_small__lFw87 styles_gray__bdOHv']/following-sibling::div[@class='styles_text__stjMD']")
            stages = [elem.text for elem in stage_elements]

            # Scrape dealflow
            dealflow_elements = self.driver.find_elements(
                By.XPATH, "//div[@class='styles_small__lFw87 styles_orange__OGK6l']/following-sibling::div[@class='styles_text__stjMD']")
            dealflow = [elem.text for elem in dealflow_elements]
            # i used Xpath because stages and dealflow have the same class name therefore i tried to locate the div parent for both of them cause they have different class names
            # Return the collected data
            return {
                "companies": company_names,
                "stages": stages,
                "dealflows": dealflow,
            }

        except Exception as e:
            print("An error occurred during scraping:", e)
            return None

    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()


# Using the StartupScraper class
if __name__ == "__main__":
    DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
    URL = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"

    # instance of StartupScraper
    scraper = StartupScraper(DRIVER_PATH, URL)

    try:
        # Set up the driver & scrape data
        scraper.setup_driver()
        scraper.wait_for_login()
        scraped_data = scraper.scrape_data()

        # results
        if scraped_data:
            print("Companies: ", scraped_data["companies"])
            print("Stages: ", scraped_data["stages"])
            print("Dealflows: ", scraped_data["dealflows"])

    finally:
        # close the driver
        scraper.close_driver()
