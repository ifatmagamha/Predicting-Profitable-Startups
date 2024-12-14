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
        "investment by stage": {"seed": "65%", "early": "24%", "growth": "5%"}}

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
        "investment by stage": {"seed": "50%", "early": "40%", "growth": "10%"}}

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
        "investment by stage": {"seed": "70%", "early": "20%", "growth": "10%"}}

        Your task is to generate a valid JSON output with all the above fields based on the provided input information.
        """

        prompt = f"Generate the missing data for the company: {company_name}, stage: {stage}, dealsflow: {dealsflow}."
        message = preamble + prompt

        try:
            response = self.chat.send_message(message)  # Adjust this based on correct method to interact with your API
            print(f"Response: {response}")

            # Check if the response contains the expected 'result' and 'candidates'
            if hasattr(response, 'result') and 'candidates' in response.result:
                candidates = response.result['candidates']
                if candidates:
                    # Extract the first candidate's content
                    candidate = candidates[0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if parts:
                            # Clean the raw JSON output
                            raw_json_text = parts[0]['text']
                        
                            # Remove the markdown delimiters (```json...``` part)
                            raw_json_text = raw_json_text.lstrip('```json').rstrip('```').strip()

                            # Parse the JSON content
                            dict_obj = json.loads(raw_json_text)

                            # If any values are missing, generate defaults
                            dict_obj = self.generate_default_values(dict_obj, company_name, stage, dealsflow)
                            return dict_obj
                else:
                    print("No candidates found in the response.")
            else:
                print("Unexpected response format or no 'result' found in the response.")
        
            return None
        except Exception as e:
            print(f"Error during data generation: {e}")
            return None

    def generate_default_values(self, dict_obj, company_name, stage, dealsflow):
        """Generate random but contextually appropriate default values for missing fields."""
    
        # Define possible regions based on company focus
        regions = ["USA", "Europe", "India", "Canada", "UK"]
        if 'region' not in dict_obj:
            dict_obj['region'] = random.choice(regions)
    
        # Set a random creation date within a reasonable range based on the company stage
        if 'creation date' not in dict_obj:
            if stage == 'Seed':
                dict_obj['creation date'] = random.choice(["08-2020", "09-2021", "10-2022"])
            elif stage == 'Early':
                dict_obj['creation date'] = random.choice(["03-2019", "06-2020", "12-2021"])
            else:
                dict_obj['creation date'] = random.choice(["01-2017", "04-2018", "08-2019"])
    
        # Generate a placeholder description with some randomness based on the company name
        if 'description' not in dict_obj:
            descriptions = [
                f"{company_name} is a pioneering company with a vision to disrupt the {random.choice(['AI', 'Fintech', 'SaaS'])} industry.",
                f"{company_name} focuses on delivering high-impact solutions in {random.choice(['Healthtech', 'AI', 'Fintech'])} with a strong emphasis on innovation.",
                f"At {company_name}, we provide cutting-edge solutions in {random.choice(['SaaS', 'Blockchain', 'AI'])} to help businesses scale efficiently."
            ]
            dict_obj['description'] = random.choice(descriptions)
    
        # Randomize market selection based on the company stage and focus
        if 'markets' not in dict_obj:
            markets = ["AI", "SaaS", "Fintech", "Healthtech", "Blockchain", "ML"]
            if stage == 'Seed':
                dict_obj['markets'] = random.sample(markets, 2)
            elif stage == 'Early':
                dict_obj['markets'] = random.sample(markets, 3)
            else:
                dict_obj['markets'] = random.sample(markets, 4)
    
        # Randomize follow-on rate based on the deal flow
        if 'follow on rate' not in dict_obj:
            if dealsflow == 'High':
                dict_obj['follow on rate'] = f"{random.randint(30, 50)}%"
            elif dealsflow == 'Medium':
                dict_obj['follow on rate'] = f"{random.randint(20, 40)}%"
            else:
                dict_obj['follow on rate'] = f"{random.randint(10, 30)}%"
    
        # Generate random investment breakdown based on stage
        if 'investment by stage' not in dict_obj:
            investment_stages = {
            'seed': f"{random.randint(50, 70)}%",
            'early': f"{random.randint(20, 40)}%",
            'growth': f"{random.randint(5, 20)}%"
        }
        dict_obj['investment by stage'] = investment_stages
    
        return dict_obj

    def process_data(self):
        """Enhance the dataset with new columns."""
        enhancements = []

        for _, row in self.data.iterrows():
            company_name = row['Company']
            stage = row.get('Stage')  # Add handling for stage if available
            dealsflow = row.get('Dealflow')  # Add handling for dealflow if available
            print(f"Processing company: {company_name}")

            enhanced_data = self.generate_missing_data(company_name, stage, dealsflow)
            enhancements.append(enhanced_data)

        # Convert enhancements list into a DataFrame
        enhancement_df = pd.DataFrame(enhancements)
        self.data = pd.concat([self.data, enhancement_df], axis=1)

    def save_data(self):
        """Save the enhanced data to a CSV file."""
        self.data.to_csv(self.output_file, index=False, encoding='utf-8')

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("GOOGLE_API_KEY")  # Get the Generative AI API key from environment
    file_path = r"C:\Users\Fatma\projet-python\Predicting-VC-deals\companies.csv"  # Path to your CSV file

    try:
        company_enhancer = CompanyDataEnhancer(api_key, file_path)
        company_enhancer.load_data()
        company_enhancer.process_data()
        company_enhancer.save_data()
        print(f"Enhanced data saved to {enhancer.output_file}")
    except Exception as e:
        print(f"Critical error: {e}")