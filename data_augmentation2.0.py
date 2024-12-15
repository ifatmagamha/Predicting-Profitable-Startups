import os
import json
from dotenv import load_dotenv
import pandas as pd
import random
from datetime import datetime
import google.generativeai as genai

class CompanyDataEnhancer:
    def __init__(self, api_key, file_path, output_file="enhanced_data.csv"):
        self.api_key = api_key
        self.file_path = file_path
        self.output_file = output_file
        self.data = None
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Ensure this is the correct model name
        self.chat = self.model.start_chat(history=[])

    def load_data(self):
        """Load data from the CSV file."""
        self.data = pd.read_csv(self.file_path)

    def enhance_data(self, company_name, enhancement_function):
        """Enhance data for a company using the specified function."""
        return enhancement_function(company_name)

    def generate_missing_data(self, company_name, stage=None, dealsflow=None):
        """Generate missing data for a company."""
        preamble = """
        You are a data generator and mapping tool. You will be provided with non-preprocessed text containing a CSV file with company names, stages, and deal flows. Based on this information, you will generate the following:

        - City/Region: Choose from [Europe, USA, UK, India, Canada]. Choose the region based on company focus.
        - Description of the product: Use the company’s name and stage to generate a description.
        - Markets: Select appropriate markets based on company focus (SaaS, Fintech, Healthtech, AI, etc.).
        - Creation date: If available, set the creation date in the format "MM-YYYY". Set to present if not found.
        - Number of deals during the last 12 months: Use company characteristics to estimate deal flow.
        - Market value: Estimate based on the company's size, stage, and market.
        - Follow-on rate: For deals older than 18 months, calculate percentage based on investment stage.
        - Investments by stage: Provide investment breakdown by stage (seed, early, growth), given the company's stage.
        """
        prompt = f"Generate the missing data for the company: {company_name}, stage: {stage}, dealsflow: {dealsflow}."
        message = preamble + prompt

        try:
            response = self.chat.send_message(message)
            print(f"Response: {response}")

            if hasattr(response, 'result') and 'candidates' in response.result:
                candidates = response.result['candidates']
                if candidates:
                    raw_json_text = candidates[0].get('text', '')
                    raw_json_text = raw_json_text.strip("```json").strip("```").strip()
                    dict_obj = json.loads(raw_json_text)
                    return self.generate_default_values(dict_obj, company_name, stage, dealsflow)
        except Exception as e:
            print(f"Error during data generation: {e}")
        return None

    def generate_default_values(self, dict_obj, company_name, stage, dealsflow):
        """Generate random but contextually appropriate default values for missing fields."""
        regions = ["USA", "Europe", "India", "Canada", "UK"]
        if 'region' not in dict_obj:
            dict_obj['region'] = random.choice(regions)
        if 'creation date' not in dict_obj:
            dict_obj['creation date'] = random.choice(["08-2020", "09-2021", "10-2022"])
        if 'description' not in dict_obj:
            dict_obj['description'] = f"{company_name} is a pioneering company focusing on {random.choice(['AI', 'Fintech', 'SaaS'])}."
        if 'markets' not in dict_obj:
            dict_obj['markets'] = random.sample(["AI", "SaaS", "Fintech", "Healthtech"], 2)
        if 'follow on rate' not in dict_obj:
            dict_obj['follow on rate'] = f"{random.randint(10, 50)}%"
        if 'investment by stage' not in dict_obj:
            dict_obj['investment by stage'] = {
                'seed': f"{random.randint(50, 70)}%",
                'early': f"{random.randint(20, 40)}%",
                'growth': f"{random.randint(5, 20)}%"
            }
        return dict_obj

    def process_data(self):
        """Enhance the dataset with new columns."""
        enhancements = []
        for _, row in self.data.iterrows():
            company_name = row['Company']
            stage = row.get('Stage')
            dealsflow = row.get('Dealflow')
            print(f"Processing company: {company_name}")
            enhanced_data = self.generate_missing_data(company_name, stage, dealsflow)
            enhancements.append(enhanced_data)

        enhancement_df = pd.DataFrame(enhancements)
        self.data = pd.concat([self.data, enhancement_df], axis=1)

    def save_data(self):
        """Save the enhanced data to a CSV file."""
        self.data.to_csv(self.output_file, index=False, encoding='utf-8')

if __name__ == "__main__":
    load_dotenv() 
    api_key = os.getenv("GOOGLE_API_KEY")  
    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\scrapping\scraped_data.csv"  

    try:
        company_enhancer = CompanyDataEnhancer(api_key, file_path)
        company_enhancer.load_data()
        company_enhancer.process_data()
        company_enhancer.save_data()
        print(f"Enhanced data saved to {company_enhancer.output_file}")
    except Exception as e:
        print(f"Critical error: {e}")
