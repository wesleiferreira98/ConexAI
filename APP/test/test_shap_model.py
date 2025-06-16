import unittest
import numpy as np
import shap
from transformers import AutoTokenizer

# Respostas simuladas
RESPOSTAS_SIMULADAS = [
    "1. A empresa enfrenta inadimplência elevada, com 5 faturas em aberto totalizando R$ 5.000,00.",
    "1. O saldo atual está positivo, mas há risco financeiro se as faturas não forem quitadas.",
    "1. A empresa apresenta boa saúde financeira: sem faturas em aberto, saldo de R$ 12.500,00.",
]

# Probabilidades simuladas associadas
PROBS_SIMULADAS = {
    RESPOSTAS_SIMULADAS[0]: [0.2, 0.8],  # classe 1 mais forte
    RESPOSTAS_SIMULADAS[1]: [0.6, 0.4],  # classe 0 mais forte
    RESPOSTAS_SIMULADAS[2]: [0.1, 0.9],  # classe 1 mais forte
}

# Tokenizer real (necessário para o SHAP)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Função de predição simulada (retorna probs fixos)
def model_predict_fn_simulado(texts):
    results = []
    for texto in texts:
        results.append(PROBS_SIMULADAS.get(texto, [0.5, 0.5]))  # padrão se não reconhecido
    return np.array(results)

# Explicador usando SHAP real com predições simuladas
class ShapExplicator:
    def __init__(self, model_predict_fn, tokenizer=None, class_names=None):
        self.model_predict_fn = model_predict_fn
        self.tokenizer = tokenizer
        self.class_names = class_names
        self.explainer = self._create_explainer()

    def _create_explainer(self):
        if self.tokenizer:
            masker = shap.maskers.Text(self.tokenizer, mask_token=self.tokenizer.mask_token or self.tokenizer.unk_token)
            return shap.Explainer(self.model_predict_fn, masker, output_names=self.class_names)
        else:
            raise ValueError("Tokenizer necessário para explicação de texto.")

    def explicar(self, entrada_textual: str):
        shap_values = self.explainer([entrada_textual])
        return shap_values

# Teste usando SHAP real com a função simulada
class TestShapExplicatorSimulado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.explicador = ShapExplicator(
            model_predict_fn=model_predict_fn_simulado,
            tokenizer=tokenizer,
            class_names=["Negativo", "Positivo"]
        )

    def test_explicar_resposta_simulada(self):
        for resposta in RESPOSTAS_SIMULADAS:
            resultado = self.explicador.explicar(resposta)
            self.assertIsInstance(resultado, shap.Explanation)
            self.assertGreater(len(resultado[0].values), 0)
            print("\nTexto:", resposta)
            print("Tokens:", resultado.data[0])
            print("SHAP values (Negativo):", resultado.values[0][:, 0])
            print("SHAP values (Positivo):", resultado.values[0][:, 1])

if __name__ == "__main__":
    unittest.main()
