# APP/core/config.py
from transformers import GenerationConfig
import os
import torch # Importar torch para usar getattr para dtypes

class ConexAIConfig:
    VERSAO_MODELO = os.environ.get("CONEXAI_MODELO", "ConexAI Vteste")
    
    MODELOS = {
        "ConexAI V1": {
            "base_model": "deepseek-ai/deepseek-llm-7b-chat",
            "adapter_repo": "wesleiferreira98/ConexAI_V1",
            "torch_dtype": "bfloat16",
            "llama_cpp": False
        },
        "ConexAI V2": {
            "base_model": "mistralai/Mistral-7B-Instruct-v0.2",
            "adapter_repo": "wesleiferreira98/ConexAI_V2",
            "torch_dtype": "float16",
            "llama_cpp": False
        },
        "ConexAI Vteste": {
            "base_model": None,
            "adapter_repo": None,
            "llama_cpp": True,
            "llama_cpp_model_info": {
                "repo_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
                "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "n_ctx": 2048,
                "n_threads": 8,
                "n_gpu_layers": 35
            }
        }
    }

    GENERATION_CONFIG = GenerationConfig(
        max_new_tokens=512,
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.15,
        do_sample=True,
        pad_token_id=0
    )

    EMBEDDINGS_CONFIG = {
        'modelo_t5': 'sentence-t5-xxl',
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

    @classmethod
    def get_model_info(cls):
        modelo_info = cls.MODELOS.get(cls.VERSAO_MODELO)
        if not modelo_info:
            raise ValueError(f"Modelo '{cls.VERSAO_MODELO}' não é suportado.")
        return modelo_info

    @classmethod
    def set_tokenizer_pad_id(cls, tokenizer):
        if tokenizer and hasattr(tokenizer, 'eos_token_id'):
            cls.GENERATION_CONFIG.pad_token_id = tokenizer.eos_token_id
        else:
            print("⚠️ Tokenizer não fornecido ou não possui 'eos_token_id'. 'pad_token_id' pode estar incorreto.")

CONFIG = ConexAIConfig

if CONFIG.VERSAO_MODELO not in CONFIG.MODELOS:
    raise ValueError(f"Modelo '{CONFIG.VERSAO_MODELO}' definido em CONEXAI_MODELO não é suportado na configuração.")