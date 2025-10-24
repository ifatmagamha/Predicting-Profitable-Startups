from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from lightgbm import LGBMRegressor

class InvestorRegressor:
    """Modèle de régression pour la prédiction de la valeur de marché."""
    def __init__(self, model_type='lgbm'):
        if model_type == 'ridge':
            model = Ridge(alpha=1.0)
            steps = [('scaler', None), ('model', model)]
        elif model_type == 'lgbm':
            model = LGBMRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=4,
                num_leaves=16,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbose=-1
            )
            steps = [('model', model)]
        else:
            raise ValueError(f"Unknown model {model_type}")

        self.pipe = Pipeline([(n, s) for n, s in steps if s is not None])

    def fit(self, X, y):
        self.pipe.fit(X, y)
        return self

    def predict(self, X):
        return self.pipe.predict(X)
