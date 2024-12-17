import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer

class StartupInvestmentPredictor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.X = None
        self.y = None
        self.models = {
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Linear Regression": LinearRegression(),
            "SVR": SVR(kernel='linear')
        }
        self.predictions = {}
        self.model_performance = {}

    def load_and_preprocess_data(self):
        try:
            # Load the dataset
            self.df = pd.read_csv(self.file_path, encoding="utf-8-sig")
            print("Data loaded and preprocessed successfully.")

            # Ensure 'market value' is the target
            if "market value" not in self.df.columns:
                raise ValueError("Target column 'market value' is missing!")

            # Select features (drop target and non-numerical columns if any)
            self.X = self.df.drop(columns=["market value", "Company"], errors='ignore')

            # Ensure only numerical columns
            self.X = self.X.select_dtypes(include=["float64", "int64"])

            # Handle missing values with imputer
            imputer = SimpleImputer(strategy='mean')
            self.X = pd.DataFrame(imputer.fit_transform(self.X), columns=self.X.columns)

            # Define target variable
            self.y = self.df["market value"]

            # Standardize numerical features
            scaler = StandardScaler()
            self.X = pd.DataFrame(scaler.fit_transform(self.X), columns=self.X.columns)

        except Exception as e:
            print(f"Error during data preprocessing: {e}")

    def train_models(self):
        try:
            X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

            # Create a dictionary to store predictions
            for model_name, model in self.models.items():
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                # Store predictions and performance metrics
                self.predictions[model_name] = y_pred
                self.model_performance[model_name] = {"MSE": mse, "R2": r2}
                print(f"{model_name} - MSE: {mse:.2f}, R2: {r2:.2f}")

            # Call display method after model training
            self.display_predictions(X_test, y_test)

        except Exception as e:
            print(f"Error during model training: {e}")

    def display_predictions(self, X_test, y_test):
        try:
            # Combine predictions with company names for display
            df_test_results = X_test.copy()
            df_test_results['Company'] = self.df.iloc[X_test.index]['Company'].values
            df_test_results['Actual Market Worth'] = y_test

            # Store the predictions for each model and only keep necessary columns
            for model_name, y_pred in self.predictions.items():
                df_test_results[f'Predicted Market Worth ({model_name})'] = y_pred

            # Keep only 'Company', 'Actual Market Worth' and the predictions for each model
            columns_to_keep = ['Company', 'Actual Market Worth']
            for model_name in self.models.keys():
                predicted_column = f'Predicted Market Worth ({model_name})'
                columns_to_keep.append(predicted_column)

            df_test_results = df_test_results[columns_to_keep]

            # Save results to CSV for each model
            self.save_csv(df_test_results)

        except Exception as e:
            print(f"Error during displaying predictions: {e}")

    def save_csv(self, df_test_results):
        try:
            # Save the results in a specific folder
            output_directory = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\predections"  
            output_file_path = f"{output_directory}\\startup_predictions.csv"
            
            print(f"Saving predictions to {output_file_path}...")
            df_test_results.to_csv(output_file_path, index=False, encoding='utf-8-sig')
            print(f"Predictions saved to {output_file_path}.")
        except Exception as e:
            print(f"Error during saving CSV: {e}")

    def run(self):
        self.load_and_preprocess_data()
        self.train_models()


if __name__ == "__main__":
    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\data_pre-processing\processed_textual-data_TF-IDF.csv"  # Change this to your file path
    predictor = StartupInvestmentPredictor(file_path)
    predictor.run()
