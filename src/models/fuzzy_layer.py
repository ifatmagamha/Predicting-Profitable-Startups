import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

def build_fuzzy_system():
    # Domaines
    ml_score = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'ml_score')
    follow_on = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'follow_on')
    stage_risk = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'stage_risk')
    age = ctrl.Antecedent(np.arange(0, 40, 1), 'age_years')
    attractiveness = ctrl.Consequent(np.arange(0, 101, 1), 'attractiveness')

    # Fonctions d'appartenance
    ml_score['low'] = fuzz.trimf(ml_score.universe, [0, 0, 0.5])
    ml_score['medium'] = fuzz.trimf(ml_score.universe, [0.3, 0.5, 0.7])
    ml_score['high'] = fuzz.trimf(ml_score.universe, [0.5, 1, 1])

    follow_on['low'] = fuzz.trimf(follow_on.universe, [0, 0, 0.4])
    follow_on['medium'] = fuzz.trimf(follow_on.universe, [0.3, 0.6, 0.8])
    follow_on['high'] = fuzz.trimf(follow_on.universe, [0.7, 1, 1])

    stage_risk['low'] = fuzz.trimf(stage_risk.universe, [0, 0, 0.4])
    stage_risk['medium'] = fuzz.trimf(stage_risk.universe, [0.3, 0.6, 0.8])
    stage_risk['high'] = fuzz.trimf(stage_risk.universe, [0.7, 1, 1])

    age['young'] = fuzz.trimf(age.universe, [0, 0, 5])
    age['mature'] = fuzz.trimf(age.universe, [3, 10, 20])
    age['old'] = fuzz.trimf(age.universe, [15, 25, 40])

    attractiveness['low'] = fuzz.trimf(attractiveness.universe, [0, 0, 40])
    attractiveness['medium'] = fuzz.trimf(attractiveness.universe, [30, 50, 70])
    attractiveness['high'] = fuzz.trimf(attractiveness.universe, [60, 100, 100])

    # Règles floues
    rules = [
        ctrl.Rule(ml_score['high'] & follow_on['high'], attractiveness['high']),
        ctrl.Rule(ml_score['medium'] & follow_on['medium'], attractiveness['medium']),
        ctrl.Rule(ml_score['low'] & follow_on['low'], attractiveness['low']),
        ctrl.Rule(stage_risk['high'], attractiveness['low']),
        ctrl.Rule(stage_risk['medium'], attractiveness['medium']),
        ctrl.Rule(age['young'] & ml_score['high'], attractiveness['high']),
        ctrl.Rule(age['mature'] & follow_on['medium'], attractiveness['medium']),
        # règle de secours : si rien n'est activé, score moyen
        ctrl.Rule(ml_score['medium'] & follow_on['low'], attractiveness['medium'])
    ]

    ctrl_sys = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(ctrl_sys)


def evaluate_attractiveness(fuzzy_ctx, ml_score, follow_on_rate, stage_risk, age_years):
    fuzzy_ctx.input['ml_score'] = float(ml_score)
    fuzzy_ctx.input['follow_on'] = float(follow_on_rate)
    fuzzy_ctx.input['stage_risk'] = float(stage_risk)
    fuzzy_ctx.input['age_years'] = float(age_years)

    try:
        fuzzy_ctx.compute()
        output = fuzzy_ctx.output.get('attractiveness', 50.0)
    except Exception as e:
        print(f"[Warning] Erreur fuzzy : {e}")
        output = 50.0
        
    return output
