import unittest
from unittest.mock import MagicMock, patch
from scraping import StartupScraper


class TestStartupScraper(unittest.TestCase):

    def setUp(self):  # this method is called before each test method in the class to prepare the test environment
        self.driver_path = r"C:\Users\Ramy\Downloads\edgedriver_win64\msedgedriver.exe"
        self.url = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"
        self.scraper = StartupScraper(self.driver_path, self.url)

    @patch('scraping.webdriver.Edge')
    @patch('scraping.Service')
    def test_setup_driver(self, mock_service, mock_edge):
        """Test the setup_driver method."""
        mock_driver = MagicMock()# create a mock object that has the same methods as the original object but with empty implementations
        mock_edge.return_value = mock_driver

        self.scraper.setup_driver()

        mock_service.assert_called_once_with(self.driver_path)
        mock_edge.assert_called_once()
        mock_driver.get.assert_called_once_with(self.url)

    @patch('scraping.input', return_value='')
    def test_wait_for_login(self, mock_input):
        """Test the wait_for_login method."""
        mock_driver = MagicMock()
        self.scraper.driver = mock_driver
        mock_driver.current_url = "https://venture.angellist.com/v/ramy-lazghab/i/ramy-lazghab/syndicates/all"

        self.scraper.wait_for_login()

        mock_input.assert_called_once_with(
            "Press Enter after you have successfully logged in...")
        mock_driver.get.assert_not_called()

    @patch('scraping.WebDriverWait')
    @patch('scraping.webdriver.Edge')
    def test_scrape_data(self, mock_edge, mock_wait):
        """Test the scrape_data method."""
        mock_driver = MagicMock()
        self.scraper.driver = mock_driver

        # Mock elements for companies, stages, and dealflows
        mock_company_elements = [
            MagicMock(text=f"Company {i}") for i in range(3)]
        mock_stage_elements = [MagicMock(text=f"Stage {i}") for i in range(3)]
        mock_dealflow_elements = [MagicMock(text="High"), MagicMock(
            text="Medium"), MagicMock(text="Low")]

        mock_driver.find_elements.side_effect = [
            mock_company_elements,  # Company names
            mock_stage_elements,   # Stages
            mock_dealflow_elements  # Dealflows
        ]

        result = self.scraper.scrape_data()

        self.assertEqual(result['companies'], [
                         f"Company {i}" for i in range(3)])
        self.assertEqual(result['stages'], [f"Stage {i}" for i in range(3)])
        self.assertEqual(result['dealflows'], ["High", "Low"])

    @patch('builtins.open', new_callable=MagicMock)
    @patch('scraping.csv.writer')
    def test_save_to_csv(self, mock_csv_writer, mock_open):
        """Test the save_to_csv method."""
        mock_writer_instance = MagicMock()
        mock_csv_writer.return_value = mock_writer_instance

        data = {
            "companies": ["Company 1", "Company 2"],
            "stages": ["Stage 1", "Stage 2"],
            "dealflows": ["High", "Low"]
        }

        self.scraper.save_to_csv(data, filename="test.csv")

        mock_open.assert_called_once_with(
            "test.csv", mode='w', newline='', encoding='utf-8')
        mock_csv_writer.assert_called_once()
        mock_writer_instance.writerow.assert_any_call(
            ["Company", "Stage", "Dealflow"])
        mock_writer_instance.writerow.assert_any_call(
            ["Company 1", "Stage 1", "High"])
        mock_writer_instance.writerow.assert_any_call(
            ["Company 2", "Stage 2", "Low"])

    @patch('scraping.webdriver.Edge')
    def test_close_driver(self, mock_edge):
        """Test the close_driver method."""
        mock_driver = MagicMock()
        self.scraper.driver = mock_driver

        self.scraper.close_driver()

        mock_driver.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
