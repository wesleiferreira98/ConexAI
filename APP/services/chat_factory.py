from APP.core.config import CONFIG
from APP.core.constantes import VERSAO_MODELO
from APP.core.carregador_modelo import carregar_modelo, carregar_tokenizer, gerar_configuracao_geracao
from APP.db.contexto_db import ContextStorage
from APP.services.chat_gestao import ChatGestao
from APP.services.validador import ValidadorPergunta
from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM

def criar_chat():
    validador = ValidadorPergunta(CONFIG)
    context_db = ContextStorage()

    model = carregar_modelo("ConexAI Vteste")
    tokenizer = carregar_tokenizer()
    generation_config = gerar_configuracao_geracao(tokenizer)
    framework = 'transformers' if tokenizer else 'llama_cpp'
    gerador = GeradorRespostaLLM(model, tokenizer,framework)

    return ChatGestao(
        validador=validador,
        gerador=gerador,
        context_db=context_db,
        versao="ConexAI Vteste"
    )
