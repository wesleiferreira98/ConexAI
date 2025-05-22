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

def criar_chat():
    validador = ValidadorPergunta(CONFIG)
    context_db = ContextStorage()

    model = carregar_modelo("ConexAI Vteste")
    tokenizer = carregar_tokenizer()
    generation_config = gerar_configuracao_geracao(tokenizer)
    framework = 'transformers' if not CONFIG.get_model_info()["is_llama_cpp"] else 'llama_cpp'
    
    gerador = GeradorRespostaLLM(model, tokenizer, generation_config, framework)

    # --- Setup para Explicabilidade (LIME e SHAP) ---
    topico_classificador = TopicoClassificador()
    
    # Este é o modelo que LIME/SHAP vão "explicar".
    # Ele recebe perguntas perturbadas, gera respostas com o LLM real,
    # e então classifica a *resposta* do LLM usando o TopicoClassificador.
    mock_llm_for_explanation = MockLLMForExplanation(gerador, topico_classificador)

    # 1. LIME Text Explainer
    # O class_names deve vir do mock_llm_for_explanation para consistência.
    lime_explicator = lime.lime_text.LimeTextExplainer(
        class_names=mock_llm_for_explanation.class_names
    )
    # Não precisa de training_data para LimeTextExplainer no __init__ se classifier_fn for fornecido
    # em explain_instance.

    # 2. SHAP Text Explainer
    # SHAP precisa de uma função `predict` (ou `predict_proba`) e o tokenizer/masker.
    # Passamos o predict_proba do mock_llm e o tokenizer real do LLM.
    shap_explicator = ShapExplicator(
        model_predict_fn=mock_llm_for_explanation.predict_proba, 
        tokenizer=tokenizer, # Passa o tokenizer real
        class_names=mock_llm_for_explanation.class_names
    )

    return ChatGestao(
        validador=validador,
        gerador=gerador,
        context_db=context_db,
        versao=CONFIG.VERSAO_MODELO,
        # Passa o mock_llm_for_explanation para que chat_gestao possa passá-lo
        # para a chamada `explain_instance` do LIME.
        mock_llm_for_explanation=mock_llm_for_explanation, 
        lime_explicator=lime_explicator,
        shap_explicator=shap_explicator
    )
