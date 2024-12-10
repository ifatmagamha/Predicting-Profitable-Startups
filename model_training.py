from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def train_stage_model(X_train, y_train_stage):
    """Train the model for Stage prediction."""
    model_stage = RandomForestClassifier(n_estimators=100, random_state=42)
    model_stage.fit(X_train, y_train_stage)
    return model_stage

def train_dealflow_model(X_train, y_train_dealflow):
    """Train the model for Dealflow prediction."""
    model_dealflow = RandomForestClassifier(n_estimators=100, random_state=42)
    model_dealflow.fit(X_train, y_train_dealflow)
    return model_dealflow
