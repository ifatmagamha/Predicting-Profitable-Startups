import os
import sys
import pandas as pd
import cohere
import time
from dotenv import load_dotenv
from datetime import datetime

# Configure UTF-8 output for debugging
sys.stdout.reconfigure(encoding='utf-8')

class CompanyDataEnhancer:
    def __init__(self, api_key, file_path):
        """Initialize with API key and file path."""
        self.api_key = api_key
        self.file_path = file_path
        self.data = None
        self.output_file = "enhanced_data.csv"

        # Initialize the Cohere client
        self.co = cohere.Client(api_key)

    def load_data(self):
        """Load the CSV data into a DataFrame and check for required columns."""
        self.data = pd.read_csv(self.file_path)
        if "Company" not in self.data.columns:
            raise ValueError("The 'Company' column is missing from the CSV file.")

    def response_generator(self, prompt, max_tokens=2000, temperature=0.03):
        """Call Cohere API to generate a response based on the prompt."""
        try:
            response = self.co.chat(
                message=prompt,
                model="command-nightly",
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.01,
                k=5,
                p=1,
            )

            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                return "No response generated"
        except Exception as e:
            # Log and raise the exception
            print(f"Error generating response: {e}")
            raise

    def enhance_data(self, company_name, enhancement_function, sleep_time):
        """General method to enhance data with retries and rate limiting."""
        try:
            result = enhancement_function(company_name)
            time.sleep(sleep_time) 
            return result
        except Exception as e:
            print(f"Error for company '{company_name}': {e}")
            return "N/A"
        
    def add_region_city(self, company_name):
        """Generate the region or city for the company."""
        prompt = f"Identify the region or city for the company named '{company_name}'. give an exemple of these [USA, UK, Canada, India, Europe, Africa, MENA]"
        return self.response_generator(prompt)

    def add_markets(self, company_name):
        """Generate the markets for the company."""
        prompt = f"Identify the markets that the company named '{company_name}' operates in. exemple : Consumer Product, Blockchain / Crypto Finance, AI / ML"
        return self.response_generator(prompt)

    def add_product_description(self, company_name):
        """Generate the product description for the company."""
        prompt = f"Describe the products or services provided by the company named '{company_name}'."
        return self.response_generator(prompt)

    def add_creation_date(self, company_name):
        """Generate the creation date for the company."""
        prompt = f"Provide the creation date for the company named '{company_name} example : since October 2015'."
        return self.response_generator(prompt)

    def add_number_of_deals(self, company_name):
        """Generate the number of deals for the company."""
        prompt = f"generate the number of how many deals has the company named '{company_name}' made in the last 12 months?"
        return self.response_generator(prompt)

    def add_follow_on_rate(self, company_name):
        """Generate the follow-on rate for the company."""
        prompt = f"Provide the follow-on rate for the company named '{company_name}' in the last 12 months. exemple : 36% ."
        return self.response_generator(prompt)

    def add_market_worth(self, company_name):
        """Generate the market worth for the company."""
        prompt = f"Provide the estimated market worth of the company named '{company_name}' exemple : 108£ ."
        return self.response_generator(prompt)


    def process_data(self):
        """Enhance the dataset with new columns."""
        regions, markets, descriptions, creation_dates, deals, follow_ons, worths = [], [], [], [], [], [], []

        for index, row in self.data.iterrows():
            company_name = row['Company']
            print(f"Processing company: {company_name}")
            
            regions.append(self.enhance_data(company_name, self.add_region_city, sleep_time=20))
            markets.append(self.enhance_data(company_name, self.add_markets, sleep_time=20))
            descriptions.append(self.enhance_data(company_name, self.add_product_description, sleep_time=20))
            creation_dates.append(self.enhance_data(company_name, self.add_creation_date, sleep_time=20))
            deals.append(self.enhance_data(company_name, self.add_number_of_deals, sleep_time=20))
            follow_ons.append(self.enhance_data(company_name, self.add_follow_on_rate, sleep_time=20))
            worths.append(self.enhance_data(company_name, self.add_market_worth, sleep_time=20))

        # Add the results to the DataFrame in one go
        self.data['Region/City'] = regions
        self.data['Markets'] = markets
        self.data['Product Description'] = descriptions
        self.data['Creation Date'] = creation_dates
        self.data['Number of Deals (12 months)'] = deals
        self.data['Follow-On Rate'] = follow_ons
        self.data['Market Worth'] = worths

    def save_data(self):
        """Save the enhanced data to a CSV file."""
        self.data.to_csv(self.output_file, index=False)

# Main execution
if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("COHERE_API_KEY")  # Get the Cohere API key from environment
    file_path = "scrapping\scraped_data.csv"  
    #file_path= "C:\Users\Ramy\OneDrive\Documents\investment project python\Predicting-Profitable-Startups\scrapping\scraping.py"
    # file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\scraped_data.csv"

    try:
        enhancer = CompanyDataEnhancer(api_key, file_path)
        enhancer.load_data()
        enhancer.process_data()
        enhancer.save_data()
        print(f"Enhanced data saved to {enhancer.output_file}")
    except Exception as e:
        print(f"Critical error: {e}")
