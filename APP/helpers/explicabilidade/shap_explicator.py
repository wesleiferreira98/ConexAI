import shap
import numpy as np
class ShapExplicator:
    def __init__(self, model):
        self.model = model
        self.explainer = shap.Explainer(model)

    def explicar(self, entrada):
        shap_values = self.explainer(entrada)
        return shap_values


def formatar_explicacao(explicacao):
    if isinstance(explicacao, list):
        return "\n".join([f"{feature}: {weight:.4f}" for feature, weight in explicacao])
    elif isinstance(explicacao, np.ndarray):
        return str(explicacao)
    return "Explicação não formatada"