# APP/core/utils.py
import numpy as np
import shap
import lime.lime_text # Adiciona import para LimeTextExplainer
from APP.services.chat.topico_classificador import TopicoClassificador # Novo import

def formatar_explicacao(explicacao):
    """
    Formata objetos de explicação LIME ou SHAP em uma string legível.
    """
    if isinstance(explicacao, list):
        # Formato LIME (para lime.lime_text.LimeTextExplainer)
        # Ex: [('palavra_chave', peso), ('outra_palavra', peso)]
        return "\n".join([f"'{feature}': {weight:.4f}" for feature, weight in explicacao])
    elif isinstance(explicacao, shap.Explanation):
        if explicacao.values.ndim == 1:
            textos = []
            for i, val in enumerate(explicacao.values):
                feature_name = explicacao.feature_names[i] if explicacao.feature_names else f"Feature {i}"
                textos.append(f"{feature_name}: {val:.4f}")
            return "\n".join(textos)
        elif explicacao.values.ndim == 2:
            textos = []
            # Para SHAP text, explicacao.data são os tokens ou palavras
            # explicacao.values[0] são os valores SHAP para o primeiro exemplo
            # Podemos tentar mapear para palavras se explicacao.data estiver disponível
            if explicacao.data is not None and len(explicacao.data) == len(explicacao.values[0]):
                for i, val_per_feature in enumerate(explicacao.values[0]):
                    feature_token = explicacao.data[i] # A palavra/token real
                    # Se for multi-classe, some os valores SHAP para a palavra entre as classes
                    textos.append(f"'{feature_token}': {np.sum(val_per_feature):.4f} (soma das classes)")
            else:
                for i, val_per_feature in enumerate(explicacao.values[0]):
                    feature_name = explicacao.feature_names[i] if explicacao.feature_names else f"Feature {i}"
                    textos.append(f"{feature_name}: {np.sum(val_per_feature):.4f} (soma das classes)")
            return "\n".join(textos)
        else:
            return "Formato SHAP complexo não suportado nesta função."
    elif isinstance(explicacao, np.ndarray):
        return str(explicacao)
    return "Explicação não formatada ou tipo desconhecido."


def preparar_dados_para_explicacao(entrada_textual: str, tokenizer=None):
    """
    Para LimeTextExplainer e SHAP com text maskers, a entrada é a própria string.
    """
    return entrada_textual


class MockLLMForExplanation:
    """
    Um wrapper para o seu GeradorRespostaLLM que simula uma interface de classificação
    (predict_proba) para LIME e SHAP, avaliando a *resposta do LLM* em termos de tópicos.
    """
    def __init__(self, gerador_llm, topico_classificador: TopicoClassificador):
        self.gerador = gerador_llm
        self.tokenizer = gerador_llm.tokenizer # Pode ser None para Llama.cpp
        self.topico_classificador = topico_classificador
        self.class_names = topico_classificador.class_names # Pegar as classes do classificador de tópicos
        print(f"MockLLMForExplanation (para explicação de texto) inicializado com classes: {self.class_names}")

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        """
        Recebe uma lista de textos (perguntas perturbadas por LIME/SHAP) e
        retorna as probabilidades de tópico para a *resposta gerada pelo LLM*
        para cada pergunta perturbada.
        """
        all_probabilities = []
        for text_input in texts:
            # 1. Gerar resposta do LLM para a pergunta perturbada
            # ATENÇÃO: Chamar o LLM para cada perturbação pode ser LENTO.
            # LIME/SHAP fazem muitas chamadas. Otimizar é crucial para uso real.
            try:
                llm_response = self.gerador.gerar_resposta(text_input)
            except Exception as e:
                print(f"⚠️ Erro ao gerar resposta do LLM para explicação: {e}. Usando resposta vazia.")
                llm_response = "" # Lida com erros de geração

            # 2. Avaliar a resposta do LLM para obter probabilidades de tópico
            probs, _ = self.topico_classificador.classificar_texto(llm_response)
            all_probabilities.append(probs)
        
        return np.array(all_probabilities)

    def predict(self, texts: list[str]) -> np.ndarray:
        """
        Retorna o índice da classe com maior probabilidade.
        """
        probs = self.predict_proba(texts)
        return np.argmax(probs, axis=1) # Retorna o índice da classe com maior probabilidade