import os
import json
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import random
import time
import google.generativeai as genai

class CompanyDataEnhancer:

    preamble = """ You are a data generator and mapping tool. You will be provided with non-preprocessed text containing a CSV file with company names, stages, and deal flows. Based on this information, you will generate the following:

    - Region: Choose from [Europe, USA, UK, India, Canada]. Choose the region based on company focus.
    - Creation date: If available, set the creation date in the format "MM-YYYY". Set to present if not found.
    - Description of the product: Use the company’s name and stage to generate a description.
    - Markets: Select appropriate markets based on company focus (SaaS, Fintech, Healthtech, AI, etc.).
    - Follow-on rate: For deals older than 18 months, calculate percentage based on investment stage.
    - Number of deals during the last 12 months: Use company characteristics to estimate deal flow.
    - Investments by stage: Provide investment breakdown by stage (seed, early, growth), given the company's stage.
    - Market value: Estimate based on the company's size, stage, and market.


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
    "number of deals (12months)": "27",
    "investment by stage": {"seed": "65%", "early": "24%", "growth": "5%"},
    "market value" : "247M$"}

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
    "number of deals (12months)": "14",
    "investment by stage": {"seed": "57%", "early": "43%", "growth": "11%"},
    "market value" : "108M$"}

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
    "number of deals (12months)": "6",
    "investment by stage": {"seed": "73%", "early": "26%", "growth": "9%"},
    "market value" : "73M$"}

    Your task is to generate a valid JSON output with all the above fields based on the provided input information.
    """

    def __init__(self, api_key, csv_file_path, output_file="enhanced_data.json"):
        self.api_key = api_key
        self.csv_file_path = csv_file_path
        self.output_file = output_file
        self.data = None
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

    def load_data(self):
        try:
            self.data = pd.read_csv(self.csv_file_path, encoding='utf-8')
            print(f"Data successfully loaded from {self.csv_file_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading data: {e}")

    def load_existing_data(self):
        try:
            with open(self.output_file, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def generate_info(self, company_name, stage, dealsflow):
        prompt = f"""{self.preamble}
        Input:
        Company: {company_name}
        Stage: {stage}
        Dealflow: {dealsflow}

        Output:
        A valid JSON file with all the required keys as mentioned in the schema in the preamble.
        """
        retry_count = 3
        for attempt in range(retry_count):
            try:
                response = self.model.generate_content(prompt)
                return json.loads(response.text)
            except json.JSONDecodeError:
                print(f"Error decoding JSON for {company_name}.")
                return None
            except Exception as e:
                if "429" in str(e):
                    print(f"Quota exceeded for {company_name}, retrying ({attempt + 1}/{retry_count})...")
                    time.sleep(60)
                else:
                    print(f"Critical error for {company_name}: {e}. Returning default values.")
                    break  # Stop further attempts for this company
            return None

    def generate_default_values(self, company_name, stage, dealsflow):
        regions = ["USA", "Europe", "India", "Canada", "UK"]

        if stage == "Seed":
            market_value = random.randint(30, 100)  # Valeur plus basse pour les entreprises en Seed
        elif stage == "Series A":
            market_value = random.randint(100, 200)  # Valeur plus haute pour les Series A
        elif stage == "Series B" or stage == "Growth":
            market_value = random.randint(200, 370)  # Valeur encore plus haute pour les stades plus avancés
        else:
            market_value = random.randint(50, 150)  # Valeur par défaut pour les stades inconnus


        return {
            "company name": company_name,
            "stage": stage,
            "dealsflow": dealsflow,
            "region": random.choice(regions),
            "creation date": datetime.now().strftime("%m-%Y"),
            "description": f"{company_name} is a pioneering company in {random.choice(['AI', 'Fintech', 'SaaS'])}.",
            "markets": random.sample(["AI", "SaaS", "Fintech", "Healthtech"], 2),
            "follow on rate": f"{random.randint(10, 90)}%",
            "number of deals (12months)":f"{random.randint(3, 30)}",
            "investment by stage": {
                "seed": f"{random.randint(50, 70)}%",
                "early": f"{random.randint(10, 30)}%",
                "growth": f"{random.randint(5, 20)}%"
            },
            "market value": f"{market_value}$"
        }

    def process_data(self, batch_size=5):
        enhanced_data = self.load_existing_data()
        companies_batch = []

        for _, row in self.data.iterrows():
            company_name = row['Company']
            stage = row.get('Stage', 'Unknown')
            dealsflow = row.get('Dealflow', 'Unknown')

            if company_name in enhanced_data:
                print(f"Skipping {company_name}, already processed.")
                continue

            companies_batch.append({
                "company_name": company_name,
                "stage": stage,
                "dealsflow": dealsflow
            })

            if len(companies_batch) >= batch_size:
                batch_results = self.generate_batch_info(companies_batch)
                enhanced_data.update(batch_results)
                companies_batch = []
                self.save_data(enhanced_data)

        if companies_batch:
            batch_results = self.generate_batch_info(companies_batch)
            enhanced_data.update(batch_results)
            self.save_data(enhanced_data)

    def generate_batch_info(self, companies_batch):
        results = {}
        for company in companies_batch:
            result = self.generate_info(company['company_name'], company['stage'], company['dealsflow'])
            if result:
                results[company['company_name']] = result
            else:
                results[company['company_name']] = self.generate_default_values(**company)
        return results

    def save_data(self, enhanced_data):
        try:
            with open(self.output_file, 'w', encoding='utf-8-sig') as f:
                json.dump(enhanced_data, f, ensure_ascii=False, indent=4)
            print(f"Enhanced data saved to {self.output_file}")
        except Exception as e:
            print(f"Error saving data: {e}")


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    csv_file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\scrapping\scraped_data.csv"
    output_file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\scrapping\enhanced_data.json"

    if not api_key:
        print("API key is missing. Please set it in your environment variables.")
    else:
        try:
            company_enhancer = CompanyDataEnhancer(api_key, csv_file_path, output_file_path)
            company_enhancer.load_data()
            company_enhancer.process_data()
        except Exception as e:
            print(f"Critical error: {e}")

