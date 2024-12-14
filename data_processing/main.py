import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from data_processing.data_processing import load_data, clean_data, preprocess_data
from data_processing.model_training import train_stage_model, train_dealflow_model
from sklearn.metrics import accuracy_score

# Load the data
file_path = "scraped_data.csv"
df = load_data(file_path)

# Clean and preprocess the data
df = clean_data(df)
df, stage_encoder, dealflow_encoder = preprocess_data(df)

# Split the data for Stage and Dealflow
X = df.drop(columns=['Company'])  # Features
y_stage = df['Stage']  # Target variable for Stage
y_dealflow = df['Dealflow']  # Target variable for Dealflow

# Split data into training and testing sets
X_train, X_test, y_train_stage, y_test_stage = train_test_split(
    X, y_stage, test_size=0.2, random_state=42)
X_train, X_test, y_train_dealflow, y_test_dealflow = train_test_split(
    X, y_dealflow, test_size=0.2, random_state=42)

# Train the models
model_stage = train_stage_model(X_train, y_train_stage)
model_dealflow = train_dealflow_model(X_train, y_train_dealflow)

# Predict the Stage and Dealflow for all startups
df['Predicted_Stage'] = model_stage.predict(X)
df['Predicted_Dealflow'] = model_dealflow.predict(X)

# Reverse encode the predictions
df['Predicted_Stage'] = stage_encoder.inverse_transform(df['Predicted_Stage'])
df['Predicted_Dealflow'] = dealflow_encoder.inverse_transform(
    df['Predicted_Dealflow'])

# Rank the startups based on both predicted Stage and Dealflow
df['Score'] = df['Predicted_Stage'].astype(
    'category').cat.codes + df['Predicted_Dealflow'].astype('category').cat.codes

# Sort startups by combined score (higher score = better startup to invest in)
df_sorted = df.sort_values(by='Score', ascending=False)

# Add a new 'Investor_Description' column based on Stage and Dealflow


def describe_investment(row):
    # Define the stage risk and opportunity based on stage
    stage = row['Predicted_Stage']
    dealflow = row['Predicted_Dealflow']

    if stage == 'Series A':
        stage_description = 'High growth potential but higher risk.'
    elif stage == 'Series B':
        stage_description = 'Moderate risk,solid growth opportunities.'
    elif stage == 'Series C':
        stage_description = 'Lower risk,steady growth.'
    elif stage == 'Series D':
        stage_description = 'Mature, stable,preparing for IPO/acquisition, lower risk.'
    elif stage == 'Series E':
        stage_description = 'Late-stage, lower-risk investments,safer returns.'
    else:
        stage_description = 'Unknown stage.'

    # Define dealflow opportunity based on deal flow category
    if dealflow == 'Low':
        dealflow_description = 'Limited investment opportunities.'
    elif dealflow == 'Medium':
        dealflow_description = 'Moderate investment opportunities.'
    elif dealflow == 'High':
        dealflow_description = 'Strong investment opportunities with higher competition.'
    else:
        dealflow_description = 'Unknown dealflow.'

    # Combine stage and dealflow descriptions
    return f"{stage_description} {dealflow_description}"


# Apply the description function to the sorted dataframe
df_sorted['Investor_Description'] = df_sorted.apply(
    describe_investment, axis=1)

# Display the top 10 startups based on predicted Stage and Dealflow with the new description
print("Top Startups to Invest In (Based on Predicted Stage and Dealflow):")
print(df_sorted[['Company', 'Predicted_Stage',
      'Predicted_Dealflow', 'Score', 'Investor_Description']].head(10))

# Evaluate the models
y_pred_stage = model_stage.predict(X_test)
y_pred_dealflow = model_dealflow.predict(X_test)

accuracy_stage = accuracy_score(y_test_stage, y_pred_stage)
accuracy_dealflow = accuracy_score(y_test_dealflow, y_pred_dealflow)

print(f"Model Accuracy (Stage Prediction): {accuracy_stage:.2f}")
print(f"Model Accuracy (Dealflow Prediction): {accuracy_dealflow:.2f}")