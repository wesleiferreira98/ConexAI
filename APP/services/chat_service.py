from APP.db.contexto_db import ContextStorage
from APP.services.chat_gestao import ChatGestao
from APP.services.validador import ValidadorPergunta
from core.carregador_modelo import carregar_modelo_conexai
from core.config import generation_config
from core.constantes import CONFIG, VERSAO_MODELO

# Inicialização única
validador = ValidadorPergunta(CONFIG)
model, tokenizer = carregar_modelo_conexai()

context_db = ContextStorage()

chat_instance = ChatGestao(
    validador=validador,
    model=model,
    tokenizer=tokenizer,
    generation_config=generation_config,
    context_db=context_db,
    versao=VERSAO_MODELO
)
