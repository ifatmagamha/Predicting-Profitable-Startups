from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

class StartupScraper:
    def __init__(self, driver_path, url):
        self.driver_path = driver_path
        self.url = url
        self.driver = None

    def setup_driver(self):
        service = Service(self.driver_path)
        self.driver = webdriver.Edge(service=service)
        self.driver.get(self.url)

    def wait_for_login(self):
        print("Please complete the login process manually.")
        WebDriverWait(self.driver, 300).until(EC.url_contains("syndicates/all"))
        print("Login detected, proceeding to scrape data...")

    def click_and_scrape_links(self):
        """Click on each clickable element, get the link and scrape required data."""
        try:
            # Find all clickable elements on the homepage
            clickable_elements = self.driver.find_elements(By.CLASS_NAME, "styles_rowWrapper__PlI54.styles_clickable__hM_tW")
            links = []
        
            for idx, elem in enumerate(clickable_elements):
                print(f"Processing element {idx + 1}/{len(clickable_elements)}")

                try:
                    # Click the clickable element to navigate
                    elem.click()
                    time.sleep(5)  # Wait for the page to load
                
                    # Debugging: Save a screenshot of the current page
                    self.driver.save_screenshot(f"page_{idx + 1}.png")
                
                    # Attempt to find the link
                    try:
                        new_link = self.driver.find_element(By.CSS_SELECTOR, 'a.styles_unstyled__MSx94').get_attribute('href')
                        links.append(new_link)
                        print(f"Found link: {new_link}")
                    except Exception as e:
                        print(f"Error extracting data from clicked link: {e}")
                
                except Exception as e:
                    print(f"Error clicking element {idx + 1}: {e}")
            
                # Go back to the homepage
                try:
                    self.driver.back()
                    time.sleep(3)  # Wait for the page to reload
                except Exception as e:
                    print(f"Error navigating back: {e}")
                    break

            return links
        except Exception as e:
            print(f"Error during clicking and scraping: {e}")
            return []

    def scrape_links(self):
        links = []
        clickable_elements = self.driver.find_elements(By.CLASS_NAME, "styles_rowWrapper__PlI54.styles_clickable__hM_tW")
        
        for elem in clickable_elements:
            try:
                # Ouvrir l'élément dans un nouvel onglet
                link = elem.get_attribute("href")
                self.driver.execute_script(f"window.open('{link}', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                
                # Attendre et récupérer le lien
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.styles_unstyled__MSx94'))
                )
                new_link = self.driver.find_element(By.CSS_SELECTOR, 'a.styles_unstyled__MSx94').get_attribute('href')
                links.append(new_link)
                print(f"Found link: {new_link}")
                
            except Exception as e:
                print(f"Error scraping link: {e}")
            
            # Fermer l'onglet et revenir
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

        return links

    def save_to_csv(self, data, filename="scraped_data.csv"):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Link"])
            writer.writerows([[link] for link in data])
        print(f"Data saved to {filename}")

    def close_driver(self):
        if self.driver:
            self.driver.quit()

# Main execution
if __name__ == "__main__":
    URL = "https://venture.angellist.com/v/gamha-islem-fatma/i/gamha-islem-fatma/syndicates/all"
    DRIVER_PATH = r"C:\Users\Fatma\Downloads\edgedriver_win64\msedgedriver.exe"

    scraper = StartupScraper(DRIVER_PATH, URL)
    try:
        scraper.setup_driver()
        scraper.wait_for_login()
        links = scraper.click_and_scrape_links()
        if links:
            scraper.save_to_csv(links)
    finally:
        scraper.close_driver()
