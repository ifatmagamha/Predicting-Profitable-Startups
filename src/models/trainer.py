import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
import joblib
import pandas as pd

class Trainer:
    """Gère l'entraînement, l'évaluation et l'export du score ML."""
    def __init__(self, model, out_path='artifacts/'):
        self.model = model
        self.out_path = out_path
        self.scaler = MinMaxScaler()

    def fit(self, X_tr, y_tr):
        self.model.fit(X_tr, np.log1p(y_tr))
        return self

    def evaluate(self, X_te, y_te):
        y_pred = np.expm1(self.model.predict(X_te))
        rmse = np.sqrt(mean_squared_error(y_te, y_pred))
        r2 = r2_score(y_te, y_pred)
        return {'rmse': rmse, 'r2': r2}

    def export_ml_scores(self, X_test, df_ref: pd.DataFrame):
        preds = self.model.predict(X_test)
        scaled = (preds - preds.min()) / (preds.max() - preds.min() + 1e-9)

        df_ref = df_ref.copy()
        df_ref['ml_score'] = np.nan
        df_ref.loc[X_test.index, 'ml_score'] = scaled
        return df_ref


    def save(self):
        joblib.dump(self.model, f"{self.out_path}/model.joblib")

