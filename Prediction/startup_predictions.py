import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# Load the dataset
file_path = "Fillrandom/startup_data_enriched.csv"
df = pd.read_csv(file_path)

# Ensure required columns are present
required_columns = ["Company", "Stage", "Dealflow", "Region", "Markets", "Production Description",
                    "Creation Date", "Number of Deals (12months)", "Follow-On rate", "Growth rate", "Market Worth"]
assert all(
    col in df.columns for col in required_columns), "Missing required columns in the dataset!"

# Data Preprocessing

# 1. Drop non-numeric columns like and "Production Description"
df_cleaned = df.drop(columns=["Production Description"])

# 2. Extract year from 'Creation Date' and convert it to age of the startup
df_cleaned['Creation Date'] = pd.to_datetime(
    df_cleaned['Creation Date'], format='%m-%Y', errors='coerce')
df_cleaned['Startup Age'] = pd.to_datetime(
    'today') - df_cleaned['Creation Date']
# Convert to years
df_cleaned['Startup Age'] = df_cleaned['Startup Age'].dt.days // 365
df_cleaned.drop(columns=['Creation Date'], inplace=True)

# 3. Encode categorical variables using One-Hot Encoding
categorical_columns = ["Stage", "Dealflow", "Region", "Markets"]
df_encoded = pd.get_dummies(
    df_cleaned, columns=categorical_columns, drop_first=True)

# 4. Handle any remaining NaN values
df_encoded.fillna(0, inplace=True)

# Prepare features (X) and target (y)
# Drop 'Company' from X
X = df_encoded.drop(columns=["Market Worth", "Company"])
y = df_encoded["Market Worth"]

# 5. Identify numerical columns (those that should be scaled)
numerical_columns = X.select_dtypes(include=["int64", "float64"]).columns

# Apply scaling only to numerical columns
scaler = StandardScaler()
X[numerical_columns] = scaler.fit_transform(X[numerical_columns])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Initialize a dictionary to store model performance
model_performance = {}

# 6. Random Forest Regression
# Handles non-linear relationships between features.
# Robust to overfitting, especially with a large number of trees.
# Can handle high-dimensional data with many features.
# When predicting the market worth of a startup, each tree in the forest makes a prediction based on the data it saw, and the final prediction is averaged across all the trees.
# This averaging helps to reduce overfitting and improves the robustness of the model.
try:
    print("Running Random Forest Regression...")
    rf_model = RandomForestRegressor(random_state=42, n_estimators=100)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)

    # Evaluate the model
    rf_mse = mean_squared_error(y_test, y_pred_rf)
    rf_r2 = r2_score(y_test, y_pred_rf)
    model_performance['Random Forest'] = {"MSE": rf_mse, "R2": rf_r2}
    print(f"Random Forest MSE: {rf_mse}, R2: {rf_r2}")
except Exception as e:
    print(f"Error during Random Forest Regression: {e}")

# 7. Linear Regression
# Works well if the relationship between features and target variable is linear.
# Simple and easy to interpret.
# The model looks at all the features of the startups (e.g., stage, region, growth rate) and tries to find a linear relationship between these features and the market worth.
# It uses this relationship to make predictions for unseen startups, where the result is the predicted market worth.
try:
    print("Running Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)

    # Evaluate the model
    lr_mse = mean_squared_error(y_test, y_pred_lr)
    lr_r2 = r2_score(y_test, y_pred_lr)
    model_performance['Linear Regression'] = {"MSE": lr_mse, "R2": lr_r2}
    print(f"Linear Regression MSE: {lr_mse}, R2: {lr_r2}")
except Exception as e:
    print(f"Error during Linear Regression: {e}")

# 8. Support Vector Regression (SVR)
# Effective in high-dimensional spaces (many features).
# Works well with non-linear data if using appropriate kernels.
# Robust to overfitting (especially with the right parameters)
# SVR finds the function that minimizes prediction error (within a certain tolerance), and for each startup, it predicts the market worth based on the features.
# If the relationship between the features and target is non-linear, SVR uses kernel functions to map the data into a higher-dimensional space where a linear function can be found

try:
    print("Running Support Vector Regression (SVR)...")
    svr_model = SVR(kernel='linear')  # Use linear kernel for simplicity
    svr_model.fit(X_train, y_train)
    y_pred_svr = svr_model.predict(X_test)

    # Evaluate the model
    svr_mse = mean_squared_error(y_test, y_pred_svr)
    svr_r2 = r2_score(y_test, y_pred_svr)
    model_performance['SVR'] = {"MSE": svr_mse, "R2": svr_r2}
    print(f"SVR MSE: {svr_mse}, R2: {svr_r2}")
except Exception as e:
    print(f"Error during Support Vector Regression: {e}")

# 9. Compare model performance
print("\nModel Performance Summary:")
for model, metrics in model_performance.items():
    print(f"{model}: MSE = {metrics['MSE']:.2f}, R2 = {metrics['R2']:.2f}")

# 10. Combine the predicted market worths with company names
df_test_results = X_test.copy()
df_test_results['Company'] = df.iloc[X_test.index]['Company'].values
df_test_results['Actual Market Worth'] = y_test
df_test_results['Predicted Market Worth (RF)'] = y_pred_rf
df_test_results['Predicted Market Worth (LR)'] = y_pred_lr
df_test_results['Predicted Market Worth (SVR)'] = y_pred_svr

# Sort and display the results for each model


def display_top_and_bottom_predictions(model_name, predicted_column):
    # Sort the results by predicted market worth (from highest to lowest)
    df_test_results_sorted = df_test_results.sort_values(
        by=predicted_column, ascending=False)

    # Display the top predicted startups
    print(f"\nTop 10 Startups to Invest in based on {model_name} Predictions:")
    print(df_test_results_sorted[['Company', predicted_column]].head(10))

    # Display the bottom predicted startups
    print(f"\nBottom 10 Startups to Avoid based on {model_name} Predictions:")
    print(df_test_results_sorted[['Company', predicted_column]].tail(10))
    df_test_results_sorted.to_csv(
        "startup_predictions_sorted.csv", index=False)


# Display for Random Forest, Linear Regression, and SVR models
display_top_and_bottom_predictions(
    "Random Forest", 'Predicted Market Worth (RF)')
display_top_and_bottom_predictions(
    "Linear Regression", 'Predicted Market Worth (LR)')
display_top_and_bottom_predictions("SVR", 'Predicted Market Worth (SVR)')

# Save the predictions to CSV

print("Predictions saved to 'startup_predictions_sorted.csv'.")
