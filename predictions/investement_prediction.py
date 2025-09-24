import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score


class StartupInvestmentPredictor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.X = None
        self.y = None
        self.models = {
            "Lasso Regression": Lasso(alpha=0.1),
            "Linear Regression": LinearRegression(),
            "SVR": SVR(kernel='linear')
        }
        self.predictions = {
            "Lasso Regression": None,
            "Linear Regression": None,
            "SVR": None
        }
        self.model_performance = {}

    def load_and_preprocess_data(self):
        # Load the dataset
        self.df = pd.read_csv(self.file_path)

        # Ensure required columns are present
        required_columns = ["Company", "Stage", "Dealflow", "region",
                            "creation date", "description", "markets", "follow on rate", "market value", "investment by stage"]
        assert all(
            col in self.df.columns for col in required_columns), "Missing required columns in the dataset!"

        # Drop unnecessary columns including 'description'
        df_cleaned = self.df.drop(columns=["description"])

        # Extract year from 'creation date' and convert it to age of the startup
        df_cleaned['creation date'] = pd.to_datetime(
            df_cleaned['creation date'], format='%m-%Y', errors='coerce')
        df_cleaned['Startup Age'] = pd.to_datetime(
            'today') - df_cleaned['creation date']
        # Convert to years
        df_cleaned['Startup Age'] = df_cleaned['Startup Age'].dt.days // 365
        df_cleaned.drop(columns=['creation date'], inplace=True)

        # Clean 'follow on rate' column by removing '%' and converting to float
        df_cleaned['follow on rate'] = df_cleaned['follow on rate'].str.replace(
            '%', '').astype(float) / 100

        # Clean 'market value' column by removing '$' and 'M$' symbols
        df_cleaned['market value'] = df_cleaned['market value'].replace(
            {'\$': '', 'M\$': ''}, regex=True)
        # Convert market value to numeric, assuming values in millions
        df_cleaned['market value'] = pd.to_numeric(
            df_cleaned['market value'], errors='coerce')

        # Encode categorical variables using One-Hot Encoding
        categorical_columns = ["Stage", "Dealflow", "region", "markets"]
        df_encoded = pd.get_dummies(
            df_cleaned, columns=categorical_columns, drop_first=True)

        # Handle any remaining NaN values
        df_encoded.fillna(0, inplace=True)

        # Prepare features (X) and target (y)
        self.X = df_encoded.drop(
            columns=["market value", "Company", "investment by stage"])
        self.y = df_encoded["market value"]

        # Scale numerical features
        numerical_columns = self.X.select_dtypes(
            include=["int64", "float64"]).columns
        scaler = StandardScaler()
        self.X[numerical_columns] = scaler.fit_transform(
            self.X[numerical_columns])

    def train_models(self, X_train, y_train, X_test, y_test):
        for model_name, model in self.models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                self.predictions[model_name] = y_pred

                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                self.model_performance[model_name] = {"MSE": mse, "R2": r2}
            except Exception as e:
                print(f"Error during {model_name} training or prediction: {e}")
                self.model_performance[model_name] = {"MSE": None, "R2": None}

    def display_top_and_bottom_predictions(self, df_test_results, model_name, predicted_column):
        # Check if the predicted column exists in the DataFrame
        if predicted_column not in df_test_results.columns:
            print(f"ERROR: {predicted_column} not found in the dataframe")
            return

        df_test_results_sorted = df_test_results.sort_values(
            by=predicted_column, ascending=False)

        # Display top predicted startups
        print(
            f"\nTop 10 Startups to Invest in based on {model_name} Predictions:")
        print(df_test_results_sorted[[
            'Company', 'investment by stage', predicted_column]].head(10))

        # Display bottom predicted startups
        print(
            f"\nBottom 10 Startups to Avoid based on {model_name} Predictions:")
        print(df_test_results_sorted[[
            'Company', 'investment by stage', predicted_column]].tail(10))

        # Save the sorted predictions to CSV
        df_test_results_sorted.to_csv(
            "startup_predictions_sorted.csv", index=False)

    def run(self):
        try:
            # Load and preprocess data
            self.load_and_preprocess_data()

            # Split the data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, self.y, test_size=0.2, random_state=42)

            # Train models and get predictions
            self.train_models(X_train, y_train, X_test, y_test)

            # Combine predictions with company names for display
            df_test_results = X_test.copy()
            df_test_results['Company'] = self.df.iloc[X_test.index]['Company'].values
            df_test_results['Actual Market Worth'] = y_test

            # Store the predictions in the DataFrame
            df_test_results['Predicted Market Worth (Lasso Regression)'] = self.predictions["Lasso Regression"]
            df_test_results['Predicted Market Worth (Linear Regression)'] = self.predictions["Linear Regression"]
            df_test_results['Predicted Market Worth (SVR)'] = self.predictions["SVR"]

            # Include 'investment by stage' column
            df_test_results['investment by stage'] = self.df.iloc[X_test.index]['investment by stage'].values

            # Display the top and bottom predictions for each model
            for model_name in self.model_performance:
                self.display_top_and_bottom_predictions(
                    df_test_results, model_name, f'Predicted Market Worth ({model_name})')

            print("Predictions saved to 'startup_predictions_sorted.csv'.")
        except Exception as e:
            print(f"Error during main execution: {e}")


if __name__ == "__main__":
    file_path = "data_pre-processing/cleaned_data.csv"
    predictor = StartupInvestmentPredictor(file_path)
    predictor.run()
