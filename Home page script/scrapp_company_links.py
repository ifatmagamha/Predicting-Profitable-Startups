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

    def click_and_scrape_links(self):
        """Click on each clickable element, get the link and scrape required data."""
        try:
            links = []
            processed_indexes = set()  # Pour suivre les éléments déjà traités
        
            while True:
                # Relocaliser les éléments à chaque itération
                clickable_elements = self.driver.find_elements(By.CLASS_NAME, "styles_rowWrapper__PlI54.styles_clickable__hM_tW")
                print(f"Found {len(clickable_elements)} clickable elements.")

                for idx, elem in enumerate(clickable_elements):
                    # Sauter les éléments déjà traités
                    if idx in processed_indexes:
                        continue

                    try:
                        print(f"Processing element {idx + 1}/{len(clickable_elements)}")
                        # Faire défiler jusqu'à l'élément
                        self.driver.execute_script("arguments[0].scrollIntoView();", elem)
                        self.driver.execute_script("arguments[0].click();", elem)  # Cliquer via JavaScript
                        time.sleep(5)  # Attendre le chargement de la page

                        # Extraire le lien
                        try:
                            new_link = self.driver.find_element(By.CLASS_NAME, "styles_unstyled__MSx94").get_attribute('href')
                            links.append(new_link)
                            print(f"Found link: {new_link}")
                        except Exception as e:
                            print(f"Error extracting data: {e}")
                    
                        processed_indexes.add(idx)  # Marquer cet élément comme traité
                    except Exception as e:
                        print(f"Error clicking element {idx + 1}: {e}")

                    # Retourner à la page précédente
                    try:
                        self.driver.back()
                        time.sleep(3)  # Attendre que la page se recharge
                    except Exception as e:
                        print(f"Error navigating back: {e}")
                        return links  # Retourner les liens collectés jusqu'à présent
            
                # Vérifier s'il reste des éléments non traités
                if len(processed_indexes) >= len(clickable_elements):
                    break

            return links
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []


<<<<<<< Updated upstream:Home page script/scrapp_company_links.py
    def save_to_csv(self, data, filename="company_links2.csv"):
=======
    def save_to_csv(self, data, filename="company_linksRL.csv"):
>>>>>>> Stashed changes:scrapping/Home page script/scrapp_company_links.py
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
<<<<<<< Updated upstream:Home page script/scrapp_company_links.py
    URL ="https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all" 
    #"https://venture.angellist.com/v/gamha-islem-fatma/i/gamha-islem-fatma/syndicates/all"
    DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
=======
    DRIVER_PATH = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
    URL = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
    # URL = "https://venture.angellist.com/v/gamha-islem-fatma/i/gamha-islem-fatma/syndicates/all"
    # DRIVER_PATH = r"C:\Users\Fatma\Downloads\edgedriver_win64\msedgedriver.exe"
>>>>>>> Stashed changes:scrapping/Home page script/scrapp_company_links.py

    scraper = StartupScraper(DRIVER_PATH, URL)
    try:
        scraper.setup_driver()
        scraper.wait_for_login()
        scraper.click_load_more()  # Load all elements
        links = scraper.click_and_scrape_links()  # Scrape links
        if links:
            scraper.save_to_csv(links)
    finally:
        scraper.close_driver()
