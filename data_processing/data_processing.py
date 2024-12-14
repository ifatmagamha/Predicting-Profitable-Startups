import pandas as pd
from sklearn.preprocessing import LabelEncoder

def load_data(file_path):
    """Load the CSV data."""
    return pd.read_csv(file_path)

def clean_data(df):
    """Clean the data (e.g., handle missing values)."""
    df.fillna("Unknown", inplace=True)  # Replace missing values
    return df

def preprocess_data(df):
    """Encode categorical variables."""
    stage_encoder = LabelEncoder()
    dealflow_encoder = LabelEncoder()

    if 'Stage' in df.columns:
        df['Stage'] = stage_encoder.fit_transform(df['Stage'])
    if 'Dealflow' in df.columns:
        df['Dealflow'] = dealflow_encoder.fit_transform(df['Dealflow'])

    return df, stage_encoder, dealflow_encoder