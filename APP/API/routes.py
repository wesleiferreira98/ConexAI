# chat_api.py (Seu arquivo original renomeado para maior clareza)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

# Importa a função que fornece a instância de ChatGestao por requisição
from APP.services.chat_factory import get_chat_gestion_for_request 
from APP.services.chat_gestao import ChatGestao # Para type hinting
from APP.helpers.explicabilidade.utils import formatar_explicacao # Para formatar explicações
import logging # Para logging

logging.basicConfig(level=logging.INFO)

router = APIRouter()

# --- Modelos Pydantic para Input e Output ---
class PerguntaInput(BaseModel):
    usuario: str
    pergunta: str
    chat_id: Optional[str] = None # O cliente pode fornecer o chat_id para continuar a conversa

class RespostaFormatada(BaseModel):
    analise_detalhada: list[str]
    acoes_recomendadas: list[str]
    metricas_acompanhamento: list[str]

class ChatInteracaoOutput(BaseModel):
    chat_id: str
    usuario: str
    pergunta: str
    resposta_formatada: RespostaFormatada # Tipo aninhado
    resposta_bruta_llm: str # Mantém a resposta bruta do LLM
    modelo: str
    data: str
    valido: bool
    detalhes_validacao: Optional[Dict[str, Any]] = None
    explicacao_lime: Optional[str] = None
    explicacao_shap: Optional[str] = None
    dados_grafico: Optional[Dict[str, Any]] = None # Se os dados do gráfico forem enviados como JSON

# --- Funções Auxiliares ---
def _formatar_resposta_llm_para_cliente(resposta_bruta: str) -> RespostaFormatada:
    """
    Formata a resposta bruta do LLM para a estrutura esperada pelo cliente.
    """
    partes = resposta_bruta.strip().split('\n\n')
    analise = []
    acoes = []
    metricas = []
    secao = None

    for linha in partes:
        if "1. Análise detalhada do problema" in linha:
            secao = "analise"
        elif "2. 3 ações recomendadas" in linha:
            secao = "acoes"
        elif "3. Métricas de acompanhamento" in linha:
            secao = "metricas"
        elif linha.strip(): # Garante que a linha não é vazia após strip
            if secao == "analise":
                analise.append(linha.strip('- '))
            elif secao == "acoes":
                acoes.append(linha.strip('- '))
            elif secao == "metricas":
                metricas.append(linha.strip('- '))
    
    return RespostaFormatada(
        analise_detalhada=analise,
        acoes_recomendadas=acoes,
        metricas_acompanhamento=metricas
    )

# --- Endpoints da API ---
@router.post("/chat/pergunta", response_model=ChatInteracaoOutput, status_code=status.HTTP_200_OK)
async def responder_pergunta_endpoint(
    payload: PerguntaInput, 
    chat_manager: ChatGestao = Depends(get_chat_gestion_for_request) # Injeção de dependência
):
    """
    Processa uma pergunta do usuário e retorna a resposta do LLM,
    juntamente com validação e explicações.
    """
    logging.info(f"Requisição recebida de '{payload.usuario}' para o chat '{payload.chat_id or 'novo'}'")
    
    # Processa a pergunta usando o ChatGestao refatorado
    # Ele agora gerencia a criação do chat_id se necessário.
    try:
        resultado_processamento = await chat_manager.processar_pergunta_api(
            usuario=payload.usuario,
            pergunta=payload.pergunta,
            chat_id=payload.chat_id
        )
    except Exception as e:
        logging.error(f"Erro inesperado ao processar pergunta para '{payload.usuario}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno ao processar sua pergunta."
        )

    # Registra a interação completa no histórico do DB
    # A `ChatGestao.processar_pergunta_api` já deve ter lidado com a criação do chat_id.
    # Agora, precisamos registrar a interação no DB.
    # Se `HistoricoInteracao` for um serviço separado, ele deveria ser injetado.
    # Por enquanto, vamos usar `context_db` diretamente.
    
    # ATENÇÃO: `ContextStorage` deve ser thread-safe ou usar um connection pool
    # se o SQLite for usado em um ambiente de múltiplos workers/threads.
    
    interacao_para_db = {
        "chat_id": resultado_processamento["chat_id"],
        "usuario": resultado_processamento["usuario"],
        "pergunta": resultado_processamento["pergunta"],
        "resposta_raw": resultado_processamento["resposta_llm_bruta"],
        "valido": resultado_processamento["valido"],
        "detalhes_validacao": resultado_processamento["detalhes_validacao"],
        "explicacao_lime": resultado_processamento["explicacao_lime"],
        "explicacao_shap": resultado_processamento["explicacao_shap"],
        "dados_grafico": resultado_processamento["dados_grafico"],
        "modelo": resultado_processamento["modelo_versao"],
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    chat_manager.context_db.registrar_interacao(resultado_processamento["chat_id"], interacao_para_db)
    
    # Formata a resposta do LLM para o cliente (apenas a parte de conteúdo)
    resposta_formatada_para_cliente = _formatar_resposta_llm_para_cliente(resultado_processamento["resposta_llm_bruta"])

    # Monta e retorna o objeto de resposta para o cliente
    return ChatInteracaoOutput(
        chat_id=resultado_processamento["chat_id"],
        usuario=resultado_processamento["usuario"],
        pergunta=resultado_processamento["pergunta"],
        resposta_formatada=resposta_formatada_para_cliente,
        resposta_bruta_llm=resultado_processamento["resposta_llm_bruta"],
        modelo=resultado_processamento["modelo_versao"],
        data=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        valido=resultado_processamento["valido"],
        detalhes_validacao=resultado_processamento["detalhes_validacao"],
        explicacao_lime=resultado_processamento["explicacao_lime"],
        explicacao_shap=resultado_processamento["explicacao_shap"],
        dados_grafico=resultado_processamento["dados_grafico"]
    )


@router.get("/chat/historico", response_model=list[tuple[str, str]]) # Retorna lista de (chat_id, nome_chat)
async def obter_historico(usuario: str, chat_manager: ChatGestao = Depends(get_chat_gestion_for_request)):
    """
    Lista todos os chats de um usuário.
    """
    return chat_manager.context_db.listar_chats(usuario)


@router.get("/chat/historico/detalhado", response_model=Dict[str, Any]) # Retorna um dicionário com interações
async def obter_historico_detalhado(usuario: str, chat_manager: ChatGestao = Depends(get_chat_gestion_for_request)):
    """
    Retorna o histórico detalhado de interações para um usuário.
    """
    historico = chat_manager.context_db.listar_interacoes(usuario)
    return {"usuario": usuario, "interacoes": historico}


@router.get("/status", response_model=Dict[str, str])
async def status(chat_manager: ChatGestao = Depends(get_chat_gestion_for_request)):
    """
    Retorna o status da API e a versão do modelo LLM em uso.
    """
    return {"status": "API online", "modelo": chat_manager.versao}