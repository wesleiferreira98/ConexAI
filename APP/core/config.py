from transformers import GenerationConfig
import os

class ConexAIConfig:
    VERSAO_MODELO = os.environ.get("CONEXAI_MODELO", "ConexAI Vteste")
    
    MODELOS = {
        "ConexAI V1": {
            "base_model": "deepseek-ai/deepseek-llm-7b-chat",
            "adapter_path": "./APP/modelos_conexAI/ConexAI V1"
        },
        "ConexAI V2": {
            "base_model": "mistralai/Mistral-7B-Instruct-v0.2",
            "adapter_path": "./APP/modelos_conexAI/ConexAI V2"
        },
        "ConexAI Vteste": {
            "base_model": None,  # Usado com ctransformers, sem modelo base
            "adapter_path": "./APP/modelos_conexAI/ConexAI Vteste"
        }
    }

    # Configuração de geração padrão
    GENERATION_CONFIG = GenerationConfig(
        max_new_tokens=512,
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.15,
        do_sample=True,
        pad_token_id=0  # Será atualizado após carregar o tokenizer
    )

    @classmethod
    def get_model_info(cls):
        modelo_info = cls.MODELOS.get(cls.VERSAO_MODELO)
        if not modelo_info:
            raise ValueError(f"Modelo '{cls.VERSAO_MODELO}' não é suportado.")
        return modelo_info

    @classmethod
    def set_tokenizer_pad_id(cls, tokenizer):
        cls.GENERATION_CONFIG.pad_token_id = tokenizer.eos_token_id


# Exporta a classe como CONFIG
CONFIG = ConexAIConfig
