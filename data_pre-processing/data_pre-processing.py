import pandas as pd
import json

class PreProcessor:
    def __init__(self, initial_csv_path, enriched_json_path, output_csv_path):
        """
        Initialize the PreProcessor with file paths.
        
        :param initial_csv_path: Path to the initial CSV file.
        :param enriched_json_path: Path to the enriched JSON file.
        :param output_csv_path: Path where the complete CSV file will be saved.
        """
        self.initial_csv_path = initial_csv_path
        self.enriched_json_path = enriched_json_path
        self.output_csv_path = output_csv_path
        self.initial_data = None
        self.enriched_data = None
        self.complete_data = None

    def load_data(self):
        """
        Load the initial CSV and enriched JSON data.
        """
        try:
            # Load initial CSV
            self.initial_data = pd.read_csv(self.initial_csv_path, encoding='utf-8-sig')  # Utilisation de utf-8-sig
            print(f"Initial CSV data loaded: {self.initial_data.shape[0]} rows.")
        
            # Load enriched JSON
            with open(self.enriched_json_path, 'r', encoding='utf-8-sig') as f:  # Utilisation de utf-8-sig
                self.enriched_data = json.load(f)
            print(f"Enriched JSON data loaded: {len(self.enriched_data)} entries.")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise


    def transform_data(self):
        """
        Transform enriched JSON data into a DataFrame.
        """
        try:
            enriched_df = pd.DataFrame.from_dict(self.enriched_data, orient='index')
            enriched_df.reset_index(drop=True, inplace=True)  # Reset index
            print(f"Transformed enriched data into DataFrame: {enriched_df.shape[0]} rows.")
            
            # Merge initial CSV with enriched data
            self.complete_data = pd.merge(
                self.initial_data,
                enriched_df,
                left_on="Company",  # Assuming 'Company' is the key column in the CSV
                right_on="company name",  # Assuming 'company name' is the key in JSON
                how="left"
            )
            print("Merged initial CSV with enriched data.")
        except Exception as e:
            print(f"Error transforming data: {e}")
            raise

    def save_to_csv(self):
        """
        Save the complete data to a CSV file.
        """
        try:
            # Ensure all columns are included and handle missing data
            if self.complete_data is not None:
                self.complete_data.fillna("N/A", inplace=True)  # Replace missing values with "N/A"
                self.complete_data.to_csv(self.output_csv_path, index=False, encoding='utf-8-sig')
                print(f"Complete data saved to {self.output_csv_path}")
            else:
                print("No data to save.")
        except Exception as e:
            print(f"Error saving data: {e}")
            raise

    def process(self):
        """
        Execute the full preprocessing pipeline.
        """
        self.load_data()
        self.transform_data()
        self.save_to_csv()

# Example usage
if __name__ == "__main__":

    initial_csv_path = r"C:\Users\Ramy\OneDrive\Documents\investment project python\Predicting-Profitable-Startups\scraped_data.csv"#C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\scrapping\scraped_data.csv"
    enriched_json_path = r"C:\Users\Ramy\OneDrive\Documents\investment project python\Predicting-Profitable-Startups\scrapping\enhanced_data.json"  #"C:\\Users\\Fatma\\projet-python\\Predicting-Profitable-Startups\\scrapping\\enhanced_data.json"
    output_csv_path = r"C:\Users\Ramy\OneDrive\Documents\investment project python\Predicting-Profitable-Startups\data_pre-processing\complete_data.csv" #C:\\Users\\Fatma\\projet-python\\Predicting-Profitable-Startups\\data_pre-processing\\complete_data.csv"

    preprocessor = PreProcessor(initial_csv_path, enriched_json_path, output_csv_path)
    preprocessor.process()
