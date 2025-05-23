from typing import Dict

from fastapi.params import Depends
from APP.core.config import CONFIG
from APP.core.constantes import VERSAO_MODELO
from APP.core.carregador_modelo import carregar_modelo, carregar_tokenizer, gerar_configuracao_geracao
from APP.db.contexto_db import ContextStorage
from APP.helpers.explicabilidade.shap_explicator import ShapExplicator
from APP.services.chat_gestao import ChatGestao
from APP.services.validador import ValidadorPergunta
from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM
from APP.services.chat.topico_classificador import TopicoClassificador
from APP.helpers.explicabilidade.utils import MockLLMForExplanation 
import lime.lime_text 
from APP.db.contexto_db import ContextStorage
from fastapi.params import Depends 
import logging

from APP.helpers.gerador_grafico import GeradorEstruturaGrafico

# Variáveis globais para armazenar recursos pesados carregados uma única vez.
# Isso garante que o modelo do LLM e os explicadores não sejam carregados em cada requisição.
_shared_resources = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis globais para armazenar recursos pesados carregados uma única vez.
_shared_resources = {}

async def get_shared_resources() -> Dict:
    """
    Carrega e retorna recursos compartilhados (LLM, tokenizers, explicadores, DB).
    Garante que sejam carregados uma única vez.
    """
    global _shared_resources
    if not _shared_resources:
        logging.info("🚀 Carregando recursos compartilhados do LLM e explicabilidade pela primeira vez...")
        
        # Conecta o ContextStorage assincronamente ANTES de usá-lo ou passá-lo
        context_db_instance = ContextStorage()
        await context_db_instance.connect() # <<< CORREÇÃO CRÍTICA AQUI

        # Carrega o modelo LLM e tokenizer (os mais pesados)
        model = carregar_modelo()
        tokenizer = carregar_tokenizer()
        
        # A geração de configuração já é tratada por CONFIG.set_tokenizer_pad_id no carregar_tokenizer
        generation_config = CONFIG.GENERATION_CONFIG 
        framework = 'transformers' if not CONFIG.get_model_info()["is_llama_cpp"] else 'llama_cpp'
        
        gerador_llm = GeradorRespostaLLM(model, tokenizer, generation_config, framework)
        
        # Inicializa o classificador de tópicos e o mock para explicabilidade
        topico_classificador = TopicoClassificador()
        mock_llm_for_explanation = MockLLMForExplanation(gerador_llm, topico_classificador)
        
        # Inicializa os explicadores
        lime_explicator = lime.lime_text.LimeTextExplainer(
            class_names=mock_llm_for_explanation.class_names
        )
        
        shap_explicator = None
        if tokenizer: 
            shap_explicator = ShapExplicator(
                model_predict_fn=mock_llm_for_explanation.predict_proba, 
                tokenizer=tokenizer,
                class_names=mock_llm_for_explanation.class_names
            )
        else:
            logging.warning("⚠️ Tokenizer não disponível. SHAP Text Explainer não será inicializado para esta versão do modelo.")

        _shared_resources = {
            "gerador_llm": gerador_llm,
            "validador_pergunta": ValidadorPergunta(CONFIG),
            "topico_classificador": topico_classificador,
            "mock_llm_for_explanation": mock_llm_for_explanation,
            "lime_explicator": lime_explicator,
            "shap_explicator": shap_explicator,
            "context_db": context_db_instance, # A instância da conexão agora é o recurso
            "gerador_grafico": GeradorEstruturaGrafico()
        }
        logging.info("✅ Recursos compartilhados carregados com sucesso.")
    return _shared_resources

# Esta função será usada pelo FastAPI para injetar uma instância de ChatGestao por requisição.
async def get_chat_gestion_for_request(shared_res: Dict = Depends(get_shared_resources)): # <<< CORREÇÃO: Agora é async
    """
    Cria e retorna uma instância de ChatGestao para uma requisição.
    Reutiliza os recursos pesados compartilhados.
    """
    return ChatGestao(
        validador=shared_res["validador_pergunta"],
        gerador=shared_res["gerador_llm"],
        context_db=shared_res["context_db"], 
        versao=CONFIG.VERSAO_MODELO, # <<< CORREÇÃO: Usar CONFIG.VERSAO_MODELO
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