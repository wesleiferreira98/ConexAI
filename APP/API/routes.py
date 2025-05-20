from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from APP.services.chat_factory import criar_chat

router = APIRouter()
chat = criar_chat()

class PerguntaInput(BaseModel):
    usuario: str
    pergunta: str

def formatar_resposta(resposta: str) -> dict:
    # Remove possíveis tags e organiza as seções do retorno
    partes = resposta.strip().split('\n\n')
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
        elif linha.strip():
            if secao == "analise":
                analise.append(linha.strip('- '))
            elif secao == "acoes":
                acoes.append(linha.strip('- '))
            elif secao == "metricas":
                metricas.append(linha.strip('- '))

    return {
        "analise_detalhada": analise,
        "acoes_recomendadas": acoes,
        "metricas_acompanhamento": metricas
    }

@router.post("/chat/pergunta")
async def responder_pergunta(payload: PerguntaInput):
    chat.usuario = payload.usuario
    if chat.chat_id is None:
        chat._selecionar_ou_criar_chat()
    resposta = chat.processar_pergunta(payload.pergunta)
    resposta_formatada = formatar_resposta(resposta)
    interacao = {
        "chat_id": chat.chat_id,
        "usuario": chat.usuario,
        "pergunta": payload.pergunta,
        "resposta": resposta_formatada,
        "modelo": chat.versao,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Registra a interação no histórico (completa)
    chat.context_db.registrar_interacao(chat.chat_id, interacao)
    return interacao


@router.get("/chat/historico")
async def obter_historico(usuario: str):
    return chat.context_db.listar_chats(usuario)


@router.get("/chat/historico/detalhado")
async def obter_historico_detalhado(usuario: str):
    historico = chat.context_db.listar_interacoes(usuario)
    return {"usuario": usuario, "interacoes": historico}


@router.get("/status")
async def status():
    return {"status": "API online", "modelo": chat.versao}
