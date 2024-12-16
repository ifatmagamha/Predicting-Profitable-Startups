import unittest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraping import StartupScraper

class TestStartupScraperWithCookies(unittest.TestCase):

    @patch("scraping.webdriver.Edge")
    @patch("scraping.Service")
    def test_load_cookies_and_navigate(self, mock_service, mock_edge):
        # Arrange
        mock_driver = MagicMock()
        mock_edge.return_value = mock_driver
        scraper = StartupScraper("dummy_path", "dummy_url")

        # Mock cookies to load
        mock_cookies = [
            {"name": "session_id", "value": "abc123", "domain": ".angellist.com"},
            {"name": "auth_token", "value": "token456", "domain": ".angellist.com"},
        ]

        # Mock file operations for cookies
        with patch("builtins.open", unittest.mock.mock_open(read_data=b"mocked_cookies")) as mock_file, \
                patch("pickle.load", return_value=mock_cookies) as mock_pickle_load:

            # Act
            scraper.setup_driver()
            scraper.driver = mock_driver  # Replace driver with mock
            scraper.load_cookies_and_navigate()

            # Assert
            mock_file.assert_called_once_with(
                "cookies.pkl", "rb")  # Ensure cookie file is read
            mock_pickle_load.assert_called_once()  # Ensure cookies are loaded
            mock_driver.get.assert_any_call(
                "https://venture.angellist.com")  # Called to set cookies
            mock_driver.add_cookie.assert_any_call(
                mock_cookies[0])  # Check cookie 1 is added
            mock_driver.add_cookie.assert_any_call(
                mock_cookies[1])  # Check cookie 2 is added
            # Final navigation to target URL
            mock_driver.get.assert_any_call("dummy_url")
        print("test_load_cookies_and_navigate: OK")  # OK message

    @patch("scraping.webdriver.Edge")
    def test_setup_driver(self, mock_edge):
        # Arrange
        mock_service = MagicMock()
        scraper = StartupScraper("dummy_path", "dummy_url")

        # Act
        scraper.setup_driver()

        # Assert
        mock_edge.assert_called_once_with(service=mock_service)
        mock_edge.return_value.get.assert_called_once_with("dummy_url")
        print("test_setup_driver: OK")  # OK message

    def test_scrape_data_structure(self):
        # Arrange
        scraper = StartupScraper("dummy_path", "dummy_url")
        scraper.driver = MagicMock()

        # Mock scraped data
        mock_company_elements = [
            MagicMock(text=f"Company {i}") for i in range(5)]
        mock_stage_elements = [
            MagicMock(text="Seed"), MagicMock(text="Series A")]
        mock_dealflow_elements = [
            MagicMock(text="High"), MagicMock(
                text="Medium"), MagicMock(text="Low")
        ]
        scraper.driver.find_elements.side_effect = [
            mock_company_elements,  # Companies
            mock_stage_elements,  # Stages
            mock_dealflow_elements,  # Dealflows
        ]

        # Act
        data = scraper.scrape_data()

        # Assert
        self.assertEqual(len(data["companies"]), 5)
        self.assertEqual(len(data["stages"]), 2)
        self.assertEqual(len(data["dealflows"]), 3)
        self.assertEqual(data["companies"][0], "Company 0")
        self.assertEqual(data["stages"][0], "Seed")
        self.assertEqual(data["dealflows"][0], "High")
        print("test_scrape_data_structure: OK")  # OK message


if __name__ == "__main__":
    unittest.main()
