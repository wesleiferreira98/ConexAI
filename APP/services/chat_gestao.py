import logging
from typing import Dict, Any, Optional, Tuple

from APP.db.contexto_db import ContextStorage # Ainda precisará para interações DB
from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM
from APP.services.validador import ValidadorPergunta
from APP.helpers.gerador_grafico import GeradorEstruturaGrafico

# Importações para explicabilidade (necessário para type hinting e uso)
from APP.helpers.explicabilidade.utils import MockLLMForExplanation, formatar_explicacao
from APP.helpers.explicabilidade.shap_explicator import ShapExplicator
import lime.lime_text # Para LimeTextExplainer

class ChatGestao:
    def __init__(self, validador: ValidadorPergunta, gerador: GeradorRespostaLLM, 
                 context_db: ContextStorage, # Passamos o DB para cá, se a ChatGestao ainda for "service layer"
                 versao: str, 
                 mock_llm_for_explanation: MockLLMForExplanation, 
                 lime_explicator: lime.lime_text.LimeTextExplainer, 
                 shap_explicator: ShapExplicator,
                 gerador_grafico: GeradorEstruturaGrafico): # Gerador de gráfico também é stateless
        
        self.validador = validador
        self.gerador = gerador
        self.context_db = context_db # Para criar/gerenciar chats no DB
        self.versao = versao
        self.mock_llm_for_explanation = mock_llm_for_explanation
        self.lime_explicator = lime_explicator
        self.shap_explicator = shap_explicator
        self.gerador_grafico = gerador_grafico
        logging.basicConfig(level=logging.INFO) # Configura logging

    async def processar_pergunta_api(self, usuario: str, pergunta: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Processa uma pergunta de um usuário no contexto de uma API.
        Gerencia a criação/recuperação do chat_id, validação, geração de resposta e explicabilidade.
        
        Retorna um dicionário com todos os dados da interação.
        """
        current_chat_id = chat_id

        # --- Gerenciamento do ID do Chat ---
        # Se não houver chat_id, cria um novo.
        if current_chat_id is None:
            new_chat_name = pergunta.strip()[:40].capitalize() # Nome baseado na primeira pergunta
            current_chat_id = self.context_db.criar_chat(usuario, new_chat_name)
            logging.info(f"API: Novo chat criado para '{usuario}': {current_chat_id}")
        else:
            # Opcional: Validar se o chat_id existe para este usuário no DB.
            # Para esta demonstração, assumimos que o chat_id é válido se fornecido.
            logging.info(f"API: Usando chat existente '{current_chat_id}' para '{usuario}'")

        # --- Validação da Pergunta ---
        valido, detalhes_validacao = self.validador.validar_pergunta(pergunta)
        
        resposta_llm = ""
        explicacao_lime = None
        explicacao_shap = None
        dados_grafico = None

        if valido:
            logging.info(f"API: Pergunta válida. Gerando resposta para '{usuario}'...")
            resposta_llm = self.gerador.gerar_resposta(pergunta)
            
            # --- Explicabilidade (LIME e SHAP) ---
            if self.lime_explicator and self.mock_llm_for_explanation:
                try:
                    logging.info("API: Gerando explicação LIME...")
                    # lime.lime_text.LimeTextExplainer.explain_instance
                    lime_explanation_obj = self.lime_explicator.explain_instance(
                        text_instance=pergunta,
                        classifier_fn=self.mock_llm_for_explanation.predict_proba,
                        labels=[1], # Assumindo que a classe 1 é "Sobre_Gestao" (do TopicoClassificador)
                        num_features=5 # Palavras mais importantes
                    )
                    explicacao_lime = formatar_explicacao(lime_explanation_obj.as_list(label=1))
                except Exception as e:
                    logging.warning(f"API - Erro ao gerar explicação LIME: {e}")
                    explicacao_lime = f"Erro ao gerar LIME: {e}"

            if self.shap_explicator:
                try:
                    logging.info("API: Gerando explicação SHAP...")
                    shap_explanation_obj = self.shap_explicator.explicar(pergunta)
                    explicacao_shap = formatar_explicacao(shap_explanation_obj)
                except Exception as e:
                    logging.warning(f"API - Erro ao gerar explicação SHAP: {e}")
                    explicacao_shap = f"Erro ao gerar SHAP: {e}"

            # --- Extração de Dados para Gráfico ---
            dados_grafico = self.gerador_grafico.extrair_dados_de_resposta(resposta_llm)
            if dados_grafico:
                logging.info("API: Dados estruturados para gráfico detectados.")
        else:
            logging.info(f"API: Pergunta inválida para '{usuario}'. Detalhes: {detalhes_validacao}")
            resposta_llm = detalhes_validacao.get('detalhes', "Não foi possível processar a pergunta devido a termos técnicos ou estar fora do escopo.")
            
        # --- Retornar Resultados ---
        return {
            "chat_id": current_chat_id,
            "usuario": usuario,
            "pergunta": pergunta,
            "resposta_llm_bruta": resposta_llm, # Retorna a resposta crua do LLM
            "valido": valido,
            "detalhes_validacao": detalhes_validacao,
            "explicacao_lime": explicacao_lime,
            "explicacao_shap": explicacao_shap,
            "dados_grafico": dados_grafico, # Retorna os dados estruturados para o cliente
            "modelo_versao": self.versao
        }
# Eles são específicos da CLI e não se aplicam a um contexto de API.