import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class DataVisualizer:
    def __init__(self, dataframe):
        """
        Initialize the DataVisualizer with a DataFrame.

        :param dataframe: pandas DataFrame containing the data to analyze and visualize.
        """
        self.data = dataframe

    def overview(self):
        """
        Display a summary of the DataFrame, including shape, data types, and missing values.
        """
        print("Data Overview:")
        print(self.data.info())
        print("\nMissing Values:")
        print(self.data.isnull().sum())

    def plot_numeric_distributions(self):
        """
        Plot distributions for all numeric features in the dataset.
        """
        numeric_columns = self.data.select_dtypes(include=['float64', 'int64']).columns
        self.data[numeric_columns].hist(bins=30, figsize=(15, 10), color='skyblue', edgecolor='black')
        plt.suptitle('Distributions of Numeric Features')
        plt.show()

    def plot_categorical_distributions(self):
        """
        Plot bar charts for all categorical features in the dataset.
        """
        categorical_columns = self.data.select_dtypes(include=['object', 'category']).columns
        for column in categorical_columns:
            plt.figure(figsize=(10, 6))
            self.data[column].value_counts().plot(kind='bar', color='teal', edgecolor='black')
            plt.title(f'Distribution of {column}')
            plt.xlabel(column)
            plt.ylabel('Count')
            plt.show()

    def plot_correlation_matrix(self):
        """
        Plot a heatmap showing the correlation matrix for numeric features.
        """
        numeric_columns = self.data.select_dtypes(include=['float64', 'int64']).columns
        correlation_matrix = self.data[numeric_columns].corr()

        plt.figure(figsize=(12, 8))
        sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', cbar=True)
        plt.title('Correlation Matrix')
        plt.show()

    def pairplot(self, features):
        """
        Plot pairwise relationships between selected features.

        :param features: List of feature names to include in the pairplot.
        """
        sns.pairplot(self.data[features], diag_kind='kde')
        plt.show()

    def boxplot_feature_vs_target(self, feature, target):
        """
        Plot a boxplot to show the distribution of a feature grouped by a target variable.

        :param feature: The feature to analyze.
        :param target: The target variable for grouping.
        """
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=target, y=feature, data=self.data, palette='Set2')
        plt.title(f'Boxplot of {feature} by {target}')
        plt.show()

    def plot_investment_stage(self, stage_columns, top_n=10):
        """
        Visualize the investment stage focus for top companies.

        :param stage_columns: List of columns representing the stages (e.g., ['Seed', 'Early', 'Growth']).
        :param top_n: Number of top companies to display.
        """
        investment_stage = self.data[['Company'] + stage_columns].set_index('Company')
        investment_stage = investment_stage.astype(float)  # Ensure numeric
        investment_stage.head(top_n).plot(kind='bar', stacked=True, figsize=(12, 6), colormap='viridis')
        plt.title(f"Investment Stage Focus of Top {top_n} Companies")
        plt.xlabel("Company")
        plt.ylabel("Investment Percentage")
        plt.show()

    def plot_follow_on_rate(self, follow_on_column, top_n=10):
        """
        Visualize top companies by follow-on rate.

        :param follow_on_column: Column representing the follow-on rate.
        :param top_n: Number of top companies to display.
        """
        top_follow_on = self.data.sort_values(by=follow_on_column, ascending=False).head(top_n)
        plt.figure(figsize=(12, 6))
        sns.barplot(data=top_follow_on, x=follow_on_column, y='Company', palette='viridis')
        plt.title(f"Top {top_n} Companies by Follow-On Rate")
        plt.xlabel("Follow-On Rate (%)")
        plt.ylabel("Company")
        plt.show()


if __name__ == "__main__":
    # Load dataset
    file_path = r"C:\Users\Fatma\projet-python\Predicting-Profitable-Startups\data_pre-processing\cleaned_data.csv"
    data = pd.read_csv(file_path)

    # Initialize DataVisualizer
    visualizer = DataVisualizer(data)

    # Perform EDA
    visualizer.overview()
    visualizer.plot_numeric_distributions()
    visualizer.plot_categorical_distributions()
    visualizer.plot_correlation_matrix()

    # Advanced analysis
    selected_features = ['feature1', 'feature2', 'feature3']
    visualizer.pairplot(selected_features)
    visualizer.boxplot_feature_vs_target('feature1', 'target')

    # specific visualizations
    stage_columns = ['Seed', 'Early', 'Growth']
    visualizer.plot_investment_stage(stage_columns, top_n=10)
    follow_on_column = 'follow on rate'
    visualizer.plot_follow_on_rate(follow_on_column, top_n=10)
