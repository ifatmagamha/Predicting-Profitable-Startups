import re, json, ast
import numpy as np

def parse_percent(x):
    if x is None or (isinstance(x,float) and np.isnan(x)): return np.nan
    s = str(x).strip().replace('%','')
    try:
        v = float(s)
        return v/100 if v>1 else v
    except:
        return np.nan

def parse_money(x):
    if x is None: return np.nan
    s = str(x).strip().lower().replace('$','')
    mult = 1.0
    if 'm' in s: s = s.replace('m',''); mult = 1e6
    if 'b' in s: s = s.replace('b',''); mult = 1e9
    s = re.sub(r'[^0-9.]','', s)
    try:
        return float(s) * mult
    except:
        return np.nan

def parse_inv_stage(s):
    if s is None: return {}
    try:
        js = str(s).replace("'", '"')
        d = json.loads(js)
        return {k: parse_percent(v) for k,v in d.items()}
    except Exception:
        # fallback: try ast.literal_eval
        try:
            d = ast.literal_eval(s)
            return {k: parse_percent(v) for k,v in d.items()}
        except:
            return {}



