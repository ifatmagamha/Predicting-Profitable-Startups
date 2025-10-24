import shap, numpy as np
from explainerdashboard import RegressionExplainer

def build_shap(pipe, X_background):
    try:
        explainer = shap.Explainer(pipe.predict, X_background)
    except Exception:
        explainer = None
    return explainer

def dashboard_for_best(pipe, X_test, y_test):
    rex = RegressionExplainer(pipe, X_test, y_test)
    return rex  # you can launch ExplainerDashboard(rex).run()
