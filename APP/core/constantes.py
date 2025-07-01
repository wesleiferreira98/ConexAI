import os

# Versão padrão do modelo (se não estiver definida a variável de ambiente)
VERSAO_MODELO = os.environ.get("CONEXAI_MODELO", "ConexAI Vteste")
VERSAO_MODELO = "ConexAI Vteste"

# Caminhos dos adaptadores para cada versão
ADAPTER_PATHS = {
    "ConexAI V1": "ConexAITeam/ConexAI V1",
    "ConexAI V2": "ConexAITeam/ConexAI V2",
    "ConexAI Vteste": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
}

# Modelos base para cada versão
MODELOS_BASE = {
    "ConexAI V1": "deepseek-ai/deepseek-llm-7b-chat",
    "ConexAI V2": "mistralai/Mistral-7B-Instruct-v0.2",
    "ConexAI Vteste": None  # Não usa modelo base, usa ctransformers
}

# Verifica se o modelo selecionado é válido
if VERSAO_MODELO not in ADAPTER_PATHS:
    raise ValueError(f"Modelo '{VERSAO_MODELO}' não é suportado.")

# Configurações do modelo selecionado
ADAPTER_PATH = ADAPTER_PATHS[VERSAO_MODELO]
BASE_MODEL = MODELOS_BASE[VERSAO_MODELO]

# Configurações de embeddings para validação semântica
CONFIG = {
    'modelo_t5': 'sentence-t5-large',
    'modelo_mpnet': 'all-mpnet-base-v2',
    'modelo_distil': 'all-MiniLM-L6-v2',

    'embeddings_t5': 'Validador/embeddings_gestao_t5.npy',
    'embeddings_mpnet': 'Validador/embeddings_gestao_mpnet.npy',
    'embeddings_distil': 'Validador/embeddings_gestao_distil.npy',

    'limiares': {
        't5': 0.75,
        'mpnet': 0.68,
        'distil': 0.60
    },
    'limiar_llm': 0.65,
    'termos_bloqueio': [
        r'\b(c[oó]digo|programa[cç][aã]o|algoritmo|python|java|c\+\+)\b',
        r'\b(fun[cç][aã]o|classe|loop|compilar|debug|query|sql)\b'
    ]
}

LIBRARY = {
    'chunk_info':'Biblioteca/chunk_info.json',
    'faiss_index': 'Biblioteca/faiss_index.bin'
}