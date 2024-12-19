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
        self.predictions = {}
        self.model_performance = {}

    def load_and_preprocess_data(self):
        # Load dataset
        self.df = pd.read_csv(self.file_path)

        # Ensure required columns
        required_columns = ["Company", "Stage", "Dealflow", "region",
                            "creation date", "description", "markets", "follow on rate", "market value", "investment by stage"]
        assert all(
            col in self.df.columns for col in required_columns), "Missing required columns!"

        # Clean dataset
        df_cleaned = self.df.drop(columns=["description"])
        df_cleaned['creation date'] = pd.to_datetime(
            df_cleaned['creation date'], format='%m-%Y', errors='coerce')
        df_cleaned['Startup Age'] = (pd.to_datetime('today') -
                                     df_cleaned['creation date']).dt.days // 365
        df_cleaned.drop(columns=['creation date'], inplace=True)

        df_cleaned['follow on rate'] = df_cleaned['follow on rate'].str.replace(
            '%', '').astype(float) / 100
        df_cleaned['market value'] = pd.to_numeric(
            df_cleaned['market value'].replace({'\$': '', 'M\$': ''}, regex=True), errors='coerce')

        # Encode categorical variables
        categorical_columns = ["Stage", "Dealflow", "region", "markets"]
        df_encoded = pd.get_dummies(
            df_cleaned, columns=categorical_columns, drop_first=True)

        df_encoded.fillna(0, inplace=True)

        # Define X and y
        self.X = df_encoded.drop(
            columns=["market value", "Company", "investment by stage"])
        self.y = df_encoded["market value"]

        # Scale numerical features
        scaler = StandardScaler()
        self.X = pd.DataFrame(scaler.fit_transform(self.X), columns=self.X.columns)

    def train_models(self):
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42)

        for model_name, model in self.models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            self.predictions[model_name] = y_pred[:10]  # Take first 10 results
            self.model_performance[model_name] = {"MSE": mse, "R2": r2}

        return self.model_performance, X_test.index[:10]