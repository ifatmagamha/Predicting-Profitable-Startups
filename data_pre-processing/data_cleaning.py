import pandas as pd
import os


class DataCleaning:
    """
    A class to clean and normalize datasets.

    Methods:
        clean_and_normalize_data(df):
            Cleans and normalizes the given dataset.
    """

    @staticmethod
    def clean_and_normalize_data(df):
        """
        Cleans and normalizes the given dataset.

        Steps:
        1. Fill missing values with appropriate defaults.
        2. Replace 'Present' in the 'creation date' column with '01-2024'.
        3. Normalize data types if necessary.

        Args:
            df (pd.DataFrame): The input DataFrame to clean.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """

        # Add any other columns you want to drop
        redundant_columns = ['company name', 'stage', 'dealsflow']

        # Drop the redundant columns
        df = df.drop(columns=redundant_columns)

        # Replace 'Present' in 'creation date' with '01-2024'
        if 'creation date' in df.columns:
            df['creation date'] = df['creation date'].replace(
                'Present', '01-2024')

        # Fill missing values for categorical columns with 'Unknown'
        categorical_columns = ['company name', 'stage',
                               'dealsflow', 'region', 'description', 'markets']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')

        # Fill missing values for numeric-like columns with mean
        if 'follow on rate' in df.columns:
            df['follow on rate'] = df['follow on rate'].str.rstrip(
                '%').astype(float, errors='ignore')
            df['follow on rate'] = df['follow on rate'].fillna(
                df['follow on rate'].mean()).astype(str) + '%'

        return df


if __name__ == "__main__":
    # Read the CSV into a DataFrame
    completedata_csv_path = r"C:\Users\Ramy\OneDrive\Documents\investment project python\Predicting-Profitable-Startups\data_pre-processing\complete_data.csv"
    output_csv_path = r"C:\Users\Ramy\OneDrive\Documents\investment project python\Predicting-Profitable-Startups\data_pre-processing\cleaned_data.csv"
    # completedata_csv_path = r"C:\\Users\\Fatma\\projet-python\\Predicting-Profitable-Startups\\data_pre-processing\\complete_data.csv"
    # output_csv_path = r"C:\\Users\\Fatma\\projet-python\\Predicting-Profitable-Startups\\data_pre-processing\\cleaned_data.csv"

    try:
        # Load the CSV file into a DataFrame
        data = pd.read_csv(completedata_csv_path, encoding='utf-8-sig')

        # Clean and normalize the data
        cleaned_data = DataCleaning.clean_and_normalize_data(data)

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_csv_path)
        os.makedirs(output_dir, exist_ok=True)

        # Save the cleaned data back to a new CSV file
        cleaned_data.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"Cleaned data saved successfully to '{output_csv_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
