import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

def load_and_preprocess_data(file_path):
    # Load the dataset
    df = pd.read_csv(file_path)

    # Ensure required columns are present
    required_columns = ["Company", "Stage", "Dealflow", "Region", "Markets", "Production Description",
                        "Creation Date", "Number of Deals (12months)", "Follow-On rate", "Growth rate", "Market Worth"]
    assert all(
        col in df.columns for col in required_columns), "Missing required columns in the dataset!"

    # Data Preprocessing
    df_cleaned = df.drop(columns=["Production Description"])

    # Extract year from 'Creation Date' and convert it to age of the startup
    df_cleaned['Creation Date'] = pd.to_datetime(
        df_cleaned['Creation Date'], format='%m-%Y', errors='coerce')
    df_cleaned['Startup Age'] = pd.to_datetime('today') - df_cleaned['Creation Date']
    # Convert to years
    df_cleaned['Startup Age'] = df_cleaned['Startup Age'].dt.days // 365
    df_cleaned.drop(columns=['Creation Date'], inplace=True)

    # Encode categorical variables using One-Hot Encoding
    categorical_columns = ["Stage", "Dealflow", "Region", "Markets"]
    df_encoded = pd.get_dummies(
        df_cleaned, columns=categorical_columns, drop_first=True)

    # Handle any remaining NaN values
    df_encoded.fillna(0, inplace=True)

    # Prepare features (X) and target (y)
    X = df_encoded.drop(columns=["Market Worth", "Company"])
    y = df_encoded["Market Worth"]

    # Scale numerical features
    numerical_columns = X.select_dtypes(include=["int64", "float64"]).columns
    scaler = StandardScaler()
    X[numerical_columns] = scaler.fit_transform(X[numerical_columns])

    return df, X, y

def train_models(X_train, y_train, X_test, y_test):
    models = {
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Linear Regression": LinearRegression(),
        "SVR": SVR(kernel='linear')
    }
    
    predictions = {
        "Random Forest": None,
        "Linear Regression": None,
        "SVR": None
    }
    
    model_performance = {}

    for model_name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            predictions[model_name] = y_pred

            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            model_performance[model_name] = {"MSE": mse, "R2": r2}
        except Exception as e:
            print(f"Error during {model_name} training or prediction: {e}")
            model_performance[model_name] = {"MSE": None, "R2": None}

    return model_performance, predictions

def display_top_and_bottom_predictions(df_test_results, model_name, predicted_column):
    df_test_results_sorted = df_test_results.sort_values(by=predicted_column, ascending=False)

    # Display top predicted startups
    print(f"\nTop 10 Startups to Invest in based on {model_name} Predictions:")
    print(df_test_results_sorted[['Company', predicted_column]].head(10))

    # Display bottom predicted startups
    print(f"\nBottom 10 Startups to Avoid based on {model_name} Predictions:")
    print(df_test_results_sorted[['Company', predicted_column]].tail(10))
    
    # Save the sorted predictions to CSV
    df_test_results_sorted.to_csv("startup_predictions_sorted.csv", index=False)

def main(file_path):
    try:
        # Load and preprocess data
        df, X, y = load_and_preprocess_data(file_path)

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train models and get predictions
        model_performance, predictions = train_models(X_train, y_train, X_test, y_test)

        # Combine predictions with company names for display
        df_test_results = X_test.copy()
        df_test_results['Company'] = df.iloc[X_test.index]['Company'].values
        df_test_results['Actual Market Worth'] = y_test

        # Store the predictions in the DataFrame
        df_test_results['Predicted Market Worth (Random Forest)'] = predictions["Random Forest"]
        df_test_results['Predicted Market Worth (Linear Regression)'] = predictions["Linear Regression"]
        df_test_results['Predicted Market Worth (SVR)'] = predictions["SVR"]

        # Display the top and bottom predictions for each model
        for model_name in model_performance:
            display_top_and_bottom_predictions(
                df_test_results, model_name, f'Predicted Market Worth ({model_name})')

        print("Predictions saved to 'startup_predictions_sorted.csv'.")
    except Exception as e:
        print(f"Error during main execution: {e}")

# Run the main function
file_path = "Fillrandom/startup_data_enriched.csv"
main(file_path)
