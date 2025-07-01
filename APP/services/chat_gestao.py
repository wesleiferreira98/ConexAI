import logging
from typing import Dict, Any, Optional, Tuple

from APP.db.contexto_db import ContextStorage # Ainda precisará para interações DB
from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM
from APP.services.validador import ValidadorPergunta
from APP.helpers.gerador_grafico import GeradorEstruturaGrafico
from APP.schemas.perfil_schema import PerfilUsuarioSchema
from APP.db.document_retriever import DocumentRetriever
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
                 gerador_grafico: GeradorEstruturaGrafico,document_retriever: Optional[DocumentRetriever]): # Gerador de gráfico também é stateless
        
        self.validador = validador
        self.gerador = gerador
        self.context_db = context_db # Para criar/gerenciar chats no DB
        self.versao = versao
        self.mock_llm_for_explanation = mock_llm_for_explanation
        self.lime_explicator = lime_explicator
        self.shap_explicator = shap_explicator
        self.gerador_grafico = gerador_grafico
        self.document_retriever = document_retriever
        logging.basicConfig(level=logging.INFO) # Configura logging

    async def processar_pergunta_api(self, usuario: str, pergunta: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Processa uma pergunta de um usuário no contexto de uma API.
        Gerencia a criação/recuperação do chat_id, busca de perfil, validação, 
        geração de resposta personalizada e explicabilidade.
        
        Retorna um dicionário com todos os dados da interação.
        """
        current_chat_id_str = chat_id

        # --- Gerenciamento do ID do Chat ---
        if not current_chat_id_str:
            new_chat_name = pergunta.strip()[:40].capitalize()
            # Garante que a chamada para criar o chat seja assíncrona
            new_chat_id = await self.context_db.criar_chat(usuario, new_chat_name)
            current_chat_id_str = str(new_chat_id)
            logging.info(f"API: Novo chat criado para '{usuario}': {current_chat_id_str}")
        else:
            logging.info(f"API: Usando chat existente '{current_chat_id_str}' para '{usuario}'")

        # ========= LÓGICA DE PERFIL (ESTÁ CORRETA) =========
        logging.info(f"API: Buscando perfil completo para o usuário '{usuario}'...")
        try:
            chat_id_int = int(current_chat_id_str) if current_chat_id_str else None
            perfil_usuario = await self.context_db.obter_perfil_completo(
                usuario=usuario,
                chat_id=chat_id_int
            )
        except Exception as e:
            logging.error(f"Não foi possível obter o perfil do usuário '{usuario}'. Erro: {e}", exc_info=True)
            return {"erro": "Falha ao carregar o perfil do usuário. Não é possível continuar."}
        # =========================================================

        # --- Validação da Pergunta ---
        valido, detalhes_validacao = self.validador.validar_pergunta(pergunta)
        
        resposta_llm = ""
        explicacao_lime = None
        explicacao_shap = None
        dados_grafico = None
         # ========= INÍCIO DA NOVA LÓGICA DE BUSCA DE DOCUMENTOS =========
        documentos_relevantes = []
        if self.document_retriever:
            try:
                # O search retorna uma lista de dicionários, pegamos só o texto
                chunks_encontrados = self.document_retriever.search(pergunta)
                documentos_relevantes = [chunk['texto'] for chunk in chunks_encontrados]
            except Exception as e:
                logging.error(f"Erro ao buscar documentos relevantes: {e}")
        # ========= FIM DA NOVA LÓGICA DE BUSCA DE DOCUMENTOS =========

        if valido:
            logging.info(f"API: Pergunta válida. Gerando resposta personalizada para '{usuario}'...")
            # ================== CORREÇÃO PRINCIPAL AQUI ==================
            # Passa o 'perfil_usuario' para que a resposta seja personalizada
            resposta_llm = self.gerador.gerar_resposta(pergunta, perfil_usuario,documentos=documentos_relevantes)
            # =============================================================
            
            # --- O restante do código de explicabilidade e gráficos ---
            if self.lime_explicator and self.mock_llm_for_explanation:
               
                pass
            if self.shap_explicator:
                
                pass
            dados_grafico = self.gerador_grafico.extrair_dados_de_resposta(resposta_llm)
            if dados_grafico:
                logging.info("API: Dados estruturados para gráfico detectados.")
        else:
            logging.info(f"API: Pergunta inválida para '{usuario}'. Detalhes: {detalhes_validacao}")
            resposta_llm = detalhes_validacao.get('detalhes', "Não foi possível processar a pergunta devido a termos técnicos ou estar fora do escopo.")
            
        # --- Retornar Resultados ---
        return {
            "chat_id": current_chat_id_str,
            "usuario": usuario,
            "pergunta": pergunta,
            "resposta_llm_bruta": resposta_llm,
            "valido": valido,
            "detalhes_validacao": detalhes_validacao,
            "explicacao_lime": explicacao_lime,
            "explicacao_shap": explicacao_shap,
            "dados_grafico": dados_grafico,
            "modelo_versao": self.versao
        }