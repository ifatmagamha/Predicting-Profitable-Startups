import pandas as pd
from pathlib import Path

REQUIRED_COLS = ["Investor","Stage","Dealflow","region","creation date",
                 "description","markets","follow on rate","investment by stage","market value"]

def load_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    df = pd.read_csv(p)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return df
