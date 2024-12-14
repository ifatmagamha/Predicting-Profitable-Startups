import pandas as pd
import random
from datetime import datetime


def generate_default_values(row):
    """
    Generate random but contextually appropriate default values for missing fields.
    """
    if pd.isnull(row['Region']):
        row['Region'] = random.choice(
            ["USA", "Europe", "India", "Canada", "UK"])
    if pd.isnull(row['Creation Date']):
        row['Creation Date'] = datetime.now().strftime("%m-%Y")
    if pd.isnull(row['Production Description']):
        row['Production Description'] = f"Is a pioneering Start up in {random.choice(['AI', 'Fintech', 'SaaS'])}."
    if pd.isnull(row['Markets']):
        row['Markets'] = ", ".join(random.sample(
            ["AI", "SaaS", "Fintech", "Healthtech"], 2))
    if pd.isnull(row['Number of Deals (12months)']):
        row['Number of Deals (12months)'] = random.randint(5, 50)
    if pd.isnull(row['Market Worth']):
        row['Market Worth'] = random.randint(
            10, 100) * 1e6  # Random value in millions
    if pd.isnull(row['Follow-On rate']):
        row['Follow-On rate'] = random.uniform(10, 90)
    if pd.isnull(row["Growth rate"]):
        row["Growth rate"] = random.uniform(5, 50)
    return row


try:
    # Load the original CSV file
    file_path = "scrapping\scraped_data.csv"  # Replace with your actual file path
    df = pd.read_csv(file_path)

    # Ensure required columns are present
    required_columns = ["Stage", "Dealflow", "Region", "Markets", "Production Description",
                        "Creation Date", "Number of Deals (12months)", "Follow-On rate", "Growth rate", "Market Worth"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    # Fill missing values with generated defaults
    df = df.apply(generate_default_values, axis=1)

    # Save the enriched data to a new CSV file
    enriched_file_path = "startup_data_enriched.csv"
    df.to_csv(enriched_file_path, index=False)
    print(f"Enriched data saved to '{enriched_file_path}'.")
except Exception as e:
    print(f"An error occurred: {e}")
