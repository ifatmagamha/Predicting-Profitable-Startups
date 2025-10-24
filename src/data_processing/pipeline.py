import pandas as pd
from sklearn.model_selection import train_test_split
from .ft_ing import FeatureEngineer

class DataPipeline:
    """
    Gère le chargement, la transformation et la séparation des données.
    Version simplifiée — sans sélection de variance, adaptée aux petits datasets.
    """

    def __init__(self, csv_path: str, target_col: str = 'market_value_usd', train_ratio: float = 0.7):
        self.csv_path = csv_path
        self.target_col = target_col
        self.train_ratio = train_ratio

        self.df_raw = None
        self.df_feat = None

    def load(self):
        """Charge le CSV brut."""
        self.df_raw = pd.read_csv(self.csv_path)
        return self

    def transform(self):
        """Applique les features engineering."""
        fe = FeatureEngineer()
        self.df_feat = fe.transform(self.df_raw)
        return self

    def split(self):
        """Sépare en train/test (indices reproductibles)."""
        X = self.df_feat.drop(columns=[self.target_col], errors='ignore')
        y = self.df_feat[self.target_col]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=self.train_ratio, random_state=42
        )

        return X_train, X_test, y_train, y_test
