from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time

# Path to Edge WebDriver
driver_path = driver_path = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
service = Service(driver_path)

# Set up Edge WebDriver
driver = webdriver.Edge(service=service)

# Open the target URL
url = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
driver.get(url)

# Wait for the page to fully load
time.sleep(5)

# Scrape the desired data
try:
    # Example: Locate elements by their class name or XPath
    growth_elements = driver.find_elements(
        By.CLASS_NAME, "styles_percentage__8Q4qq styles_small__hHzAb")  # growth
    early_seed_elements = driver.find_elements(
        By.CLASS_NAME, "styles_percentage__8Q4qq styles_small__hHzAb")  # seed
    portfolio_elements = driver.find_elements(
        By.CLASS_NAME, "isrg1b0 _1q1e6zs43n _1q1e6zs3nk _1q1e6zsih _1q1e6zsk5 _1q1e6zsjv _1q1e6zs118 _1q1e6zs12c _1q1e6zs3ah")  # portfolio
    followonrate_elements = driver.find_elements(
        By.CLASS_NAME, "styles_percentage__8Q4qq styles_large__vi1FY")
    # Extract and print the text
    growth_data = [elem.text for elem in growth_elements]
    early_seed_data = [elem.text for elem in early_seed_elements]
    portfolio_data = [elem.text for elem in portfolio_elements]
    followonrate_data = [elem.text for elem in followonrate_elements]

    print("Growth Data:", growth_data)
    print("Early/Seed Data:", early_seed_data)
    print("Portfolio Data:", portfolio_data)
    print("Follow-On-Rate", followonrate_data)

except Exception as e:
    print("An error occurred:", e)

# Close the browser
driver.quit()
