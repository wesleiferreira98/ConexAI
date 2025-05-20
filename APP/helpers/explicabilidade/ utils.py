import numpy as np

def formatar_explicacao(explicacao):
    if isinstance(explicacao, list):
        return "\n".join([f"{feature}: {weight:.4f}" for feature, weight in explicacao])
    elif hasattr(explicacao, 'values') and hasattr(explicacao, 'data'):
        texto = []
        for i, val in enumerate(explicacao.values[0]):
            texto.append(f"Feature {i}: {val:.4f}")
        return "\n".join(texto)
    elif isinstance(explicacao, np.ndarray):
        return str(explicacao)
    return "Explicação não formatada"


def preparar_dados_para_explicacao(entrada_textual, tokenizer=None):
    # Função utilitária para converter entrada textual em vetor
    # Aqui será necessário adaptar à estrutura dos dados usados no modelo
    if tokenizer:
        return tokenizer.encode(entrada_textual, return_tensors="np")
    return [[len(entrada_textual)]]  # Exemplo simplificado