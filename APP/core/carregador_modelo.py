import os
import torch
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, GenerationConfig
from peft import PeftModel
from ctransformers import AutoModelForCausalLM as CTransformersModel
from llama_cpp import Llama

# Carrega o token do .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")


def carregar_modelo(versao="ConexAI V1"):
    if versao == "ConexAI V2":
        base_model = "mistralai/Mistral-7B-Instruct-v0.2"
        adapter_repo = "wesleiferreira98/ConexAI_V2"
        torch_dtype = torch.float16

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch_dtype,
            bnb_4bit_use_double_quant=True
        )

        print(f"🔄 Carregando modelo {versao}...")
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch_dtype,
            use_auth_token=HF_TOKEN
        )
        model = PeftModel.from_pretrained(model, adapter_repo, use_auth_token=HF_TOKEN)
        return model.merge_and_unload()

    elif versao == "ConexAI V1":
        base_model = "deepseek-ai/deepseek-llm-7b-chat"
        adapter_repo = "wesleiferreira98/ConexAI_V1"
        torch_dtype = torch.bfloat16

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch_dtype,
            bnb_4bit_use_double_quant=True
        )

        print(f"🔄 Carregando modelo {versao}...")
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch_dtype,
            use_auth_token=HF_TOKEN
        )
        model = PeftModel.from_pretrained(model, adapter_repo, use_auth_token=HF_TOKEN)
        return model.merge_and_unload()

    elif versao == "ConexAI Vteste":
        return carregar_llama_modelo("ConexAI Vteste")

    else:
        raise ValueError(f"Versão de modelo '{versao}' não é suportada.")


def carregar_tokenizer(versao="ConexAI V1"):
    if versao == "ConexAI V2":
        base_model = "mistralai/Mistral-7B-Instruct-v0.2"
    elif versao == "ConexAI V1":
        base_model = "deepseek-ai/deepseek-llm-7b-chat"
    elif versao == "ConexAI Vteste":
        return None  # Não precisa de tokenizer
    else:
        raise ValueError("Versão inválida.")

    print(f"🔄 Carregando tokenizer para {versao}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model, use_auth_token=HF_TOKEN)
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def gerar_configuracao_geracao(tokenizer):
    if tokenizer is None:
        return None
    return GenerationConfig(
        max_new_tokens=512,
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.15,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )


def carregar_llama_modelo(versao="ConexAI Vteste"):
    if versao == "ConexAI Vteste":
        caminho_modelo = "./APP/modelos_conexAI/ConexAI Vteste"
        arquivo_modelo = "phi-2.Q4_0.gguf"

        print(f"🔄 Carregando modelo Llama com {versao}...")
        llm = Llama(
            model_path=os.path.join(caminho_modelo, arquivo_modelo),
            n_ctx=2048,
            n_threads=8,
            n_gpu_layers=35
        )
        return llm

    else:
        raise ValueError(f"Modelo Llama para '{versao}' não é suportado.")
