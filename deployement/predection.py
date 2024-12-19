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

            for model_name, model in self.models.items():
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                self.predictions[model_name] = y_pred
                self.model_performance[model_name] = {"MSE": mse, "R2": r2}

            sorted_models = sorted(self.model_performance.items(), key=lambda x: x[1]['R2'], reverse=True)
            top_indices = [model[0] for model in sorted_models]
            best_model_name = top_indices[0]

            return self.model_performance, top_indices, best_model_name, X_test, y_test
        except Exception as e:
            print(f"Error during model training: {e}")
            return None


    def display_predictions(self, X_test, y_test, best_model_name):
        try:
            # Prepare the results DataFrame
            df_test_results = X_test.copy()
            if 'Company' in self.df.columns:
                df_test_results['Company'] = self.df.iloc[X_test.index]['Company'].values
            df_test_results['Actual Market Worth'] = y_test

            # Add predictions and differences for each model
            for model_name, y_pred in self.predictions.items():
                predicted_column = f'Predicted Market Worth ({model_name})'
                df_test_results[predicted_column] = y_pred
                diff_column = f'Difference ({model_name})'
                df_test_results[diff_column] = df_test_results['Actual Market Worth'] - df_test_results[predicted_column]

            # Sort by predictions from the best model
            best_predicted_column = f'Predicted Market Worth ({best_model_name})'
            if best_predicted_column in df_test_results:
                df_test_results = df_test_results.sort_values(by=best_predicted_column, ascending=False)

            # Save to CSV
            self.save_csv(df_test_results)
            return df_test_results

        except Exception as e:
            print(f"Error during displaying predictions: {e}")
            return None

    def save_csv(self, df_test_results):
        try:
            # Save the results in a specific folder
            output_directory = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\deployement\data"  
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
    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\data_pre-processing\processed_textual-data_TF-IDF.csv"  
    predictor = StartupInvestmentPredictor(file_path)
    predictor.run()
