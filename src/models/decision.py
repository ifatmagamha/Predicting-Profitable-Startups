from typing import Dict
from .fuzzy_layer import build_fuzzy_system, evaluate_attractiveness

class DecisionSynthesizer:
    """Combine la prédiction ML et la décision fuzzy en score final."""
    def __init__(self, alpha: float = 0.6):
        self.alpha = alpha
        self.fuzzy_ctx = build_fuzzy_system()  # construit une seule fois

    def synthesize_one(self, row: Dict, ml_prob: float) -> Dict:
        follow_on = float(row.get('follow_on_rate', 0.0))
        stage_risk = float(row.get('stage_risk', 0.5))
        age_years = float(row.get('age_years', 0.0))

        fuzzy_val = evaluate_attractiveness(
            self.fuzzy_ctx,
            ml_score=ml_prob,
            follow_on_rate=follow_on,
            stage_risk=stage_risk,
            age_years=age_years
        )

        final_score = self.alpha * ml_prob + (1 - self.alpha) * (fuzzy_val / 100)
        return {
            'ml_prob': ml_prob,
            'fuzzy_score': fuzzy_val,
            'final_score': final_score
        }
