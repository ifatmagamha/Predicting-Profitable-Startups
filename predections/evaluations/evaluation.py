import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
import seaborn as sns
import matplotlib.pyplot as plt


from predections.investement_predection import StartupInvestmentPredictor

class StartupInvestmentEvaluator:
    def __init__(self, predictions, model_performance, df):
        self.predictions = predictions
        self.model_performance = model_performance
        self.df = df

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
            output_directory = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\predections\evaluation"  
            output_file_path = f"{output_directory}\\startup_predictions_performance.csv"
            
            print(f"Saving predictions to {output_file_path}...")
            df_test_results.to_csv(output_file_path, index=False, encoding='utf-8-sig')
            print(f"Predictions saved to {output_file_path}.")
        except Exception as e:
            print(f"Error during saving CSV: {e}")

    def plot_model_performance(self):
        # Visualisation de la performance des modèles
        models = list(self.model_performance.keys())
        mse_values = [self.model_performance[model]['MSE'] for model in models]
        r2_values = [self.model_performance[model]['R2'] for model in models]

        fig, ax = plt.subplots(1, 2, figsize=(14, 7))

        # MSE Graph
        ax[0].barh(models, mse_values, color='lightblue')
        ax[0].set_title("Model MSE Comparison")
        ax[0].set_xlabel("Mean Squared Error")

        # R2 Graph
        ax[1].barh(models, r2_values, color='lightgreen')
        ax[1].set_title("Model R2 Comparison")
        ax[1].set_xlabel("R2 Score")

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\data_pre-processing\processed_textual-data_TF-IDF.csv"  
    
    # Step 1: Train and test models
    trainer = StartupInvestmentPredictor(file_path)
    trainer.load_and_preprocess_data()
    model_performance, top_indices, best_model_name, X_test, y_test = trainer.train_and_test_models()
    
    # Step 2: Evaluate predictions and model performance
    evaluator = StartupInvestmentEvaluator(trainer.predictions, model_performance, trainer.df)
    df_test_results = evaluator.display_predictions(X_test, y_test, best_model_name)
    evaluator.plot_model_performance()