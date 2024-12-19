import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn.objects as so

class StartupPredictionsVisualizer:
    def __init__(self, csv_path):
        """Initialize the visualizer with a CSV file path."""
        self.csv_path = csv_path
        self.df_predictions = None

    def load_data(self):
        """Load data from the CSV file."""
        try:
            self.df_predictions = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            print("Error: File not found!")
        except pd.errors.EmptyDataError:
            print("Error: File is empty!")

    def validate_data(self):
        """Validate the presence of required columns."""
        required_columns = ['Predicted Market Worth (Lasso Regression)', 'Company']
        if not all(column in self.df_predictions.columns for column in required_columns):
            raise ValueError("Error: Required columns are missing!")

    def handle_missing_values(self):
        """Handle missing values in the dataset."""
        self.df_predictions = self.df_predictions.dropna()
        self.df_predictions = self.df_predictions.fillna(0)

    def plot_top_10_predictions(self):
        """Plot the top 10 startups based on Lasso Regression predictions."""
        top_10_predictions = self.df_predictions.head(10)
        plt.figure(figsize=(12, 6))
        sns.barplot(
            x='Predicted Market Worth (Lasso Regression)', 
            y='Company', 
            data=top_10_predictions, 
            palette='viridis'
        )
        plt.title("Top 10 Startups Predicted Market Worth (Lasso Regression)")
        plt.xlabel("Predicted Market Worth ($)")
        plt.ylabel("Company")
        plt.grid(True, axis='x', linestyle='--', alpha=0.6)
        plt.show()

    def plot_comparison(self):
        """Plot a comparison of market worth predictions across models."""
        comparison_data = self.df_predictions[[
            'Company', 
            'Predicted Market Worth (Lasso Regression)', 
            'Predicted Market Worth (Linear Regression)', 
            'Predicted Market Worth (SVR)'
        ]]
        comparison_data_melted = comparison_data.melt(
            id_vars='Company',
            value_vars=[
                'Predicted Market Worth (Lasso Regression)',
                'Predicted Market Worth (Linear Regression)',
                'Predicted Market Worth (SVR)'
            ],
            var_name='Model',
            value_name='Predicted Market Worth'
        )
        plt.figure(figsize=(14, 8))
        sns.barplot(
            x='Company', 
            y='Predicted Market Worth', 
            hue='Model', 
            data=comparison_data_melted
        )
        plt.title("Comparison of Market Worth Predictions by Different Models")
        plt.xlabel("Company")
        plt.ylabel("Predicted Market Worth ($)")
        plt.xticks(rotation=90)
        plt.legend(title='Model')
        plt.tight_layout()
        plt.show()

    def plot_distribution(self):
        """Plot the distribution of predicted market worth using Lasso Regression."""
        plt.figure(figsize=(10, 6))
        sns.histplot(
            self.df_predictions['Predicted Market Worth (Lasso Regression)'], 
            kde=True, 
            color='purple'
        )
        plt.title("Distribution of Predicted Market Worth (Lasso Regression)")
        plt.xlabel("Predicted Market Worth ($)")
        plt.ylabel("Frequency")
        plt.show()

if __name__ == "__main__":
    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\predections\startup_predictions_sorted.csv"  
    visualizer = StartupPredictionsVisualizer(file_path)
    visualizer.load_data()
    visualizer.validate_data()
    visualizer.handle_missing_values()
    visualizer.plot_top_10_predictions()
    visualizer.plot_comparison()
    visualizer.plot_distribution()
