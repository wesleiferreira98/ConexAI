# APP/services/chat_factory.py
from typing import Dict
import logging

from fastapi.params import Depends 

from APP.core.config import CONFIG
from APP.core.carregador_modelo import carregar_modelo, carregar_tokenizer
from APP.db.contexto_db import ContextStorage
from APP.helpers.explicabilidade.shap_explicator import ShapExplicator
from APP.services.chat_gestao import ChatGestao
from APP.services.validador import ValidadorPergunta
from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM
from APP.services.chat.topico_classificador import TopicoClassificador
from APP.helpers.explicabilidade.utils import MockLLMForExplanation 
import lime.lime_text 
from APP.db.cac_storage import CacStorage 
from APP.helpers.gerador_grafico import GeradorEstruturaGrafico

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

_shared_resources = {}

async def get_shared_resources() -> Dict:
    """
    Carrega e retorna recursos compartilhados (LLM, tokenizers, explicadores)
    se ainda não foram carregados.
    """
    global _shared_resources
    if not _shared_resources:
        logging.info("🚀 Carregando recursos compartilhados do LLM e explicabilidade pela primeira vez...")
        
        context_db_instance = ContextStorage()
        await context_db_instance.connect()
        
        cac_storage_instance = CacStorage() # <<< NOVA INSTÂNCIA CAC
        await cac_storage_instance.connect()
        model = carregar_modelo()
        tokenizer = carregar_tokenizer()
        generation_config = CONFIG.GENERATION_CONFIG 
        framework = 'transformers' if not CONFIG.get_model_info()["llama_cpp"] else 'llama_cpp'
        
        gerador_llm = GeradorRespostaLLM(model, tokenizer, generation_config, framework)
        
        # --- Lógica Condicional para Explicabilidade (XAI) ---
        topico_classificador = None
        mock_llm_for_explanation = None
        lime_explicator = None
        shap_explicator = None

        if CONFIG.ENABLE_XAI: # <<< VERIFICA O NOVO FLAG
            logging.info("✨ Explicabilidade (XAI) está ATIVADA.")
            topico_classificador = TopicoClassificador()
            mock_llm_for_explanation = MockLLMForExplanation(gerador_llm, topico_classificador)
            
            lime_explicator = lime.lime_text.LimeTextExplainer(
                class_names=mock_llm_for_explanation.class_names
            )
            
            if tokenizer: 
                shap_explicator = ShapExplicator(
                    model_predict_fn=mock_llm_for_explanation.predict_proba, 
                    tokenizer=tokenizer,
                    class_names=mock_llm_for_explanation.class_names
                )
            else:
                logging.warning("⚠️ Tokenizer não disponível para SHAP Text Explainer. SHAP não será inicializado para esta versão do modelo.")
        else:
            logging.info("🚫 Explicabilidade (XAI) está DESATIVADA por configuração.")
        # --- Fim da Lógica Condicional para XAI ---

        _shared_resources = {
            "gerador_llm": gerador_llm,
            "validador_pergunta": ValidadorPergunta(CONFIG),
            "topico_classificador": topico_classificador, # Pode ser None
            "mock_llm_for_explanation": mock_llm_for_explanation, # Pode ser None
            "lime_explicator": lime_explicator, # Pode ser None
            "shap_explicator": shap_explicator, # Pode ser None
            "cac_storage": cac_storage_instance,
            "context_db": context_db_instance,
            "gerador_grafico": GeradorEstruturaGrafico()
        }
        logging.info("✅ Recursos compartilhados carregados com sucesso.")
    return _shared_resources

async def get_chat_gestion_for_request(shared_res: Dict = Depends(get_shared_resources)):
    """
    Cria e retorna uma instância de ChatGestao para uma requisição.
    Reutiliza os recursos pesados compartilhados.
    """
    return ChatGestao(
        validador=shared_res["validador_pergunta"],
        gerador=shared_res["gerador_llm"],
        context_db=shared_res["context_db"], 
        versao=CONFIG.VERSAO_MODELO,
        mock_llm_for_explanation=shared_res["mock_llm_for_explanation"],
        lime_explicator=shared_res["lime_explicator"],
        shap_explicator=shared_res["shap_explicator"],
        gerador_grafico=shared_res["gerador_grafico"]
    )

async def close_db_connection():
    """
    Fecha a conexão com o banco de dados armazenada nos recursos compartilhados.
    Deve ser chamada no evento de shutdown do FastAPI.
    """
    global _shared_resources
    if "context_db" in _shared_resources and _shared_resources["context_db"]:
        await _shared_resources["context_db"].close()
        logging.info("Conexão do banco de dados fechada no shutdown.")
    if "cac_storage" in _shared_resources and _shared_resources["cac_storage"]: # <<< FECHA TAMBÉM O CAC STORAGE
        await _shared_resources["cac_storage"].close()
        logging.info("Conexão do banco de dados (CacStorage) fechada no shutdown.")