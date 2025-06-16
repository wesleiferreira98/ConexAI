import unittest
from unittest.mock import Mock
from APP.helpers.explicabilidade.shap_explicator import ShapExplicator
import shap
from transformers import AutoTokenizer
from unittest import skip
import matplotlib.pyplot as plt
from IPython.display import display # type: ignore
#Fixture de respostas simuladas
RESPOSTAS_SIMULADAS = [
    """1. A empresa enfrenta inadimplência elevada, com 5 faturas em aberto totalizando R$ 5.000,00.
2. Ações recomendadas:
   - Entrar em contato com clientes inadimplentes
   - Renegociar prazos com fornecedores
   - Reavaliar fluxo de caixa
3. Métricas: Redução no total de faturas, saldo médio mensal, índice de inadimplência""",

    """1. O saldo atual está positivo, mas há risco financeiro se as faturas não forem quitadas.
2. Ações recomendadas:
   - Priorizar pagamentos com vencimento mais próximo
   - Buscar antecipação de recebíveis
   - Revisar orçamento operacional
3. Métricas: Variação do saldo, percentual de faturas pagas, margem operacional""",

    """1. A empresa apresenta boa saúde financeira: sem faturas em aberto, saldo de R$ 12.500,00.
2. Ações recomendadas:
   - Investir em melhorias operacionais
   - Considerar expansão de serviços
   - Monitorar comportamento de pagamento
3. Métricas: ROI de novos investimentos, satisfação do cliente, saldo médio""",
]
class DummyTokenizer:
    def __init__(self):
        self.mask_token = "[MASK]"
    
    def __call__(self, text):
        return text.split()  # Simples tokenização baseada em espaço

    def convert_tokens_to_string(self, tokens):
        return ' '.join(tokens)

# Função preditora simulada para teste
def mock_predict_fn(texts):
    # Retorna probabilidade fixa para cada entrada (2 classes)
    return [[0.4, 0.6] for _ in texts]

class TestShapExplicator(unittest.TestCase):
    def setUp(self):
        # Função de predição simulada (mesmo shape que modelos reais retornam)
        self.mock_predict_fn = lambda x: [[0.1, 0.9] for _ in x]

        # Tokenizer real da Hugging Face
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

        self.explicador = ShapExplicator(
            model_predict_fn=self.mock_predict_fn,
            tokenizer=self.tokenizer,
            class_names=["Negativo", "Positivo"]
        )


    def test_explicar_return_type(self):
        entrada = "Gostei do serviço"
        resultado = self.explicador.explicar(entrada)
        self.assertIsInstance(resultado, shap.Explanation)


    def test_explicar_values_exist(self):
        entrada = "Gostei do atendimento"
        resultado = self.explicador.explicar(entrada)
        self.assertTrue(hasattr(resultado[0], "values"))
        self.assertGreater(len(resultado[0].values), 0)
    
    @skip("Executar manualmente para ver explicação SHAP")
    def test_visualizar_explicacao(self):
        entrada = "O atendimento foi excelente, gostei muito"
        resultado = self.explicador.explicar(entrada)

        # Visualização textual no terminal
        print("Tokens:", resultado.data[0])
        print("Valores SHAP por token (classe 0):", resultado.values[0][:, 0])
        print("Valores SHAP por token (classe 1):", resultado.values[0][:, 1])

        # Visualização gráfica (para uso interativo)
        shap.plots.text(resultado[0])
        plt.show()
    def test_explicar_com_respostas_simuladas(self):
            for resposta in RESPOSTAS_SIMULADAS:
                resultado = self.explicador.explicar(resposta)
                self.assertIsInstance(resultado, shap.Explanation)
                self.assertGreater(len(resultado[0].values), 0)

    @skip("Executar manualmente para visualizar SHAP das respostas simuladas")
    def test_explicar_com_respostas_simuladas(self):
        for i, resposta in enumerate(RESPOSTAS_SIMULADAS):
            resultado = self.explicador.explicar(resposta)

            # Visualização via terminal (tokens + valores)
            print(f"\n--- Resposta {i} ---")
            print("Texto:", resposta)
            print("Tokens:", resultado.data[0])
            print("Valores SHAP (classe 0):", resultado.values[0][:, 0])
            print("Valores SHAP (classe 1):", resultado.values[0][:, 1])

            # Salva como HTML para análise visual
            html_str = shap.plots.text(resultado[0], display=False)
            path = f"explicacao_simulada_{i}.html"
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_str)
            print(f"Explicação visual salva em: {path}")

def visualizar_explicacao_manual():
    explicador = ShapExplicator(
        model_predict_fn=lambda x: [[0.1, 0.9] for _ in x],
        tokenizer=AutoTokenizer.from_pretrained("bert-base-uncased"),
        class_names=["Negativo", "Positivo"]
    )

    entrada = "O atendimento foi excelente, gostei muito"
    resultado = explicador.explicar(entrada)

    print("Tokens:", resultado.data[0])
    print("Valores SHAP por token (classe 0):", resultado.values[0][:, 0])
    print("Valores SHAP por token (classe 1):", resultado.values[0][:, 1])

    # `shap.plots.text` retorna uma string HTML quando display=False
    html_str = shap.plots.text(resultado[0], display=False)

    with open("explicacao_shap.html", "w", encoding="utf-8") as f:
        f.write(html_str)

    print("Explicação SHAP salva em 'explicacao_shap.html'")


def visualizar_respostas_simuladas():
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    explicador = ShapExplicator(
        model_predict_fn=mock_predict_fn,
        tokenizer=tokenizer,
        class_names=["Negativo", "Positivo"]
    )

    for i, resposta in enumerate(RESPOSTAS_SIMULADAS):
        resultado = explicador.explicar(resposta)

        print(f"\n--- Resposta {i} ---")
        print("Texto:", resposta)
        print("Tokens:", resultado.data[0])
        print("SHAP Classe 0:", resultado.values[0][:, 0])
        print("SHAP Classe 1:", resultado.values[0][:, 1])

        html_str = shap.plots.text(resultado[0], display=False)
        path = f"explicacao_simulada_{i}.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_str)
        print(f"✅ Explicação salva em: {path}")

