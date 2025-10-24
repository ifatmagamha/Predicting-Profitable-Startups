import pandas as pd
import numpy as np
import ast
from collections import Counter
from datetime import datetime
from .parser import parse_percent, parse_money, parse_inv_stage

class FeatureEngineer:
    def __init__(self, top_k_markets=8):
        self.top_k_markets = top_k_markets
        self.top_markets_ = None

    def fit_markets(self, df):
        lists = df['markets'].apply(lambda s: ast.literal_eval(str(s)) if pd.notna(s) else [])
        flat = [m for lst in lists for m in lst]
        counts = Counter(flat)
        self.top_markets_ = [m for m, _ in counts.most_common(self.top_k_markets)]

    def transform(self, df):
        df = df.copy()

        # Base parsing
        df['follow_on_rate'] = df['follow on rate'].apply(parse_percent)
        df['market_value_usd'] = df['market value'].apply(parse_money)

        df['creation date'] = pd.to_datetime(df['creation date'], format='%m-%Y', errors='coerce')
        df['age_years'] = (pd.Timestamp.today() - df['creation date']).dt.days / 365.25


        # Investment by stage
        inv = df['investment by stage'].apply(parse_inv_stage)
        for c in ['seed', 'early', 'growth']:
            df[f'pct_{c}'] = inv.apply(lambda d: d.get(c, np.nan))
        sums = df[['pct_seed','pct_early','pct_growth']].sum(axis=1)
        for c in ['pct_seed','pct_early','pct_growth']:
            df[c] = df[c] / sums

        # encoding Stage / Dealflow / Region
        stage_map = {'pre-seed':1.0,'seed':0.8,'early':0.6,'series a':0.5,'series b':0.4,'growth':0.3,'late':0.2}
        df['stage_risk'] = df['Stage'].str.lower().map(stage_map).fillna(0.6)
        df['dealflow_enc'] = df['Dealflow'].str.capitalize().map({'Low':0,'Medium':1,'High':2})
        df = pd.get_dummies(df, columns=['region'], prefix='region', drop_first=True)

        # One-hot sur top markets
        if self.top_markets_ is None:
            self.fit_markets(df)
        for m in self.top_markets_:
            col = f"market__{m.lower().replace(' ','_').replace('/','_')}"
            df[col] = df['markets'].apply(lambda s: 1 if pd.notna(s) and m in ast.literal_eval(str(s)) else 0)


        df["growth_x_followon"] = df["pct_growth"] * df["follow_on_rate"]
        df["risk_x_age"] = df["stage_risk"] * df["age_years"]
        df["dealflow_x_risk"] = df["dealflow_enc"] * df["stage_risk"]


        # data seperation ML vs. reporting
        self.df_full = df.copy()
        drop_cols = ['Company','description','markets','follow on rate', 'market value','investment by stage','creation date','Stage','Dealflow','region']  
        df_model = df.drop(columns=drop_cols, errors='ignore')



        return df_model.fillna(0)
