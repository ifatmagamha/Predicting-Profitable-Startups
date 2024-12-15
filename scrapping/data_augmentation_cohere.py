import os
import sys
import pandas as pd
import cohere
import logging
import json
import time
from dotenv import load_dotenv

# Configure UTF-8 output for debugging
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, filename="enhancertest.log", format="%(asctime)s - %(levelname)s - %(message)s")

class CompanyDataEnhancer:
    def __init__(self, api_key, file_path):
        """Initialize with API key and file path."""
        self.api_key = api_key
        self.file_path = file_path
        self.data = None
        self.output_file = "enhanced_data.csv"

        # Initialize the Cohere client
        self.co = cohere.Client(api_key)

        # Define the shared preamble
        self.preamble = """ You are a data generator and mapping tool. You will be provided with non-preprocessed text containing a CSV file with company names, stages, and deal flows. Based on this information, you will generate the following:

    - City/Region: Choose from [Europe, USA, UK, India, Canada]. Choose the region based on company focus.
    - Description of the product: Use the company’s name and stage to generate a description.
    - Markets: Select appropriate markets based on company focus (SaaS, Fintech, Healthtech, AI, etc.).
    - Creation date: If available, set the creation date in the format "MM-YYYY". Set to present if not found.
    - Number of deals during the last 12 months: Use company characteristics to estimate deal flow.
    - Market value: Estimate based on the company's size, stage, and market.
    - Follow-on rate: For deals older than 18 months, calculate percentage based on investment stage.
    - Investments by stage: Provide investment breakdown by stage (seed, early, growth), given the company's stage.

    Example 1:
    Input:
    Company: Flight.VC Syndicate
    Stage: Seed
    Dealflow: High

    Output:
    {"company name": "Flight.VC Syndicate",
    "stage": "Seed",
    "dealsflow": "High",
    "region": "USA",
    "creation date": "10-2021",
    "description": "Flight.VC Syndicate is a VC firm investing in high-growth companies in AI, ML, and consumer product sectors. They focus on early-stage investments and have a strong track record of successful exits.",
    "markets": ["AI / ML", "Finance", "Consumer Product"],
    "follow on rate": "36%",
    "investment by stage": {"seed": "65%", "early": "24%", "growth": "5%"},
    "market value": "73$"}

    Example 2:
    Input:
    Company: Unwritten Capital
    Stage: Series A
    Dealflow: Medium

    Output:
    {"company name": "Unwritten Capital",
     "stage": "Series A",
    "dealsflow": "Medium",
    "region": "USA",
    "creation date": "06-2018",
    "description": "Unwritten Capital focuses on investing in promising companies with diverse founders in the Fintech, SaaS, and Healthtech industries. Their portfolio includes early-stage companies with high-growth potential.",
    "markets": ["ML/AI", "Healthtech"],
    "follow on rate": "45%",
    "investment by stage": {"seed": "50%", "early": "40%", "growth": "10%"},
    "market value": "108$"}

    Example 3:
    Input:
    Company: MyAsiaVC
    Stage: Seed
    Dealflow: Low

    Output:
    {"company name": "MyAsiaVC",
    "stage": "Seed",
    "dealsflow": "Low",
    "region": "India",
    "creation date": "09-2020",
    "description": "MyAsiaVC invests in early-stage startups across the AI, SaaS, and Fintech sectors. They are focused on the Indian market with a keen interest in innovative solutions for emerging markets.",
    "markets": ["AI", "SaaS", "Fintech"],
    "follow on rate": "20%",
    "investment by stage": {"seed": "70%", "early": "20%", "growth": "10%"},
    "market value": "228$"}

    Your task is to generate a valid JSON output with all the above fields based on the provided input information.
    """

    def load_data(self):
        """Load the CSV data into a DataFrame and check for required columns."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"The file {self.file_path} does not exist.")
        
        self.data = pd.read_csv(self.file_path)
        if "Company" not in self.data.columns:
            raise ValueError("The 'Company' column is missing from the CSV file.")

    def response_generator(self, prompt,retries=3):
        """Call Cohere API to generate a response with retry logic."""
        for attempt in range(retries):
            try:
                response = self.co.chat(
                message=prompt,
                preamble=self.preamble,
                model="command-nightly",
                max_tokens=2000,
                temperature=0.03,
                presence_penalty=0.01,
                k=5,
                p=1,
                )
                if response.text:
                    return response.text.strip()
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return "N/A"

    def enhance_field(self, company_name, fieled_name, prompt_template, sleep_time=10):
        """General method to enhance a specific field using the API."""
        prompt = prompt_template.format(company_name=company_name)
        result = self.response_generator(prompt)
        time.sleep(sleep_time)
        return result

    def process_data(self):
        """Enhance the dataset with new columns."""
        prompts = {
            "Region": "Identify the region or city for the company named '{company_name}'. Choose from [USA, UK, Canada, India, Europe, Africa, MENA].",
            "Markets": "Identify the markets that the company named '{company_name}' operates in. Example: Consumer Product, Blockchain / Crypto Finance, AI / ML.",
            "Product Description": "Describe the products or services provided by the company named '{company_name}'.",
            "Creation Date": "Provide the creation date for the company named '{company_name}'. Example: since October 2015.",
            "Number of Deals (12 months)": "How many deals has the company named '{company_name}' made in the last 12 months?",
            "Follow-On Rate": "Provide the follow-on rate for the company named '{company_name}' in the last 12 months. Example: 36%.",
            "Market Worth": "Provide the estimated market worth of the company named '{company_name}'. Example: 108$.",
        }

        results = {field: [] for field in prompts.keys()}

        for index, row in self.data.iterrows():
            company_name = str(row['Company'])
            logging.info(f"Processing company: {company_name}")

            for field, prompt_template in prompts.items():
                try:
                    enhanced_data = self.enhance_field(company_name, field, prompt_template)
                    results[field].append(enhanced_data)
                except Exception as e:
                    logging.error(f"Error processing field '{field}' for company '{company_name}': {e}")
                    results[field].append("Error")

        for field, values in results.items():
            self.data[field] = values

    def save_data(self):
        """Save the enhanced data to a CSV file."""
        try:
            self.data.to_csv(self.output_file, index=False)
            print(f"Enhanced data saved to {self.output_file}")
        except Exception as e:
            print(f"Error saving data: {e}")

# Main execution
if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("COHERE_API_KEY")  # Get the Cohere API key from environment

    if not api_key:
        print("Error: API key not found. Please set COHERE_API_KEY in your .env file.")
        sys.exit(1)

    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\scrapping\scraped_data.csv"

    try:
        enhancer = CompanyDataEnhancer(api_key, file_path)
        enhancer.load_data()
        enhancer.process_data()
        enhancer.save_data()
    except Exception as e:
        print(f"Critical error: {e}")
