from src.data_processing.pipeline import DataPipeline
from src.models.model import InvestorRegressor
from src.models.trainer import Trainer
from src.models.decision import DecisionSynthesizer
from sklearn.model_selection import cross_val_score, KFold
import pandas as pd
import os

os.environ["LOKY_MAX_CPU_COUNT"] = "4"


pipe = DataPipeline('data/cleaned_data.csv')
pipe.load().transform()
X_train, X_test, y_train, y_test = pipe.split()


model = InvestorRegressor('lgbm')
trainer = Trainer(model)
trainer.fit(X_train, y_train)


cv = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model.pipe, X_train, y_train, cv=cv, scoring='r2')
print(f"R² moyen (CV 5-folds): {scores.mean():.3f} ± {scores.std():.3f}")

results = trainer.evaluate(X_test, y_test)
print("Evaluation sur test:", results)

df_ready = trainer.export_ml_scores(X_test, pipe.df_feat)
synth = DecisionSynthesizer()

results = []
for _, row in df_ready.iterrows():
    res = synth.synthesize_one(row.to_dict(), row['ml_score'])
    results.append({**row.to_dict(), **res})

final_df = pd.DataFrame(results)
final_df.to_csv('data/final_investor_scores.csv', index=False)
print("Exported: data/final_investor_scores.csv")
