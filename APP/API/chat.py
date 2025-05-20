from fastapi import APIRouter
from schemas.chat_schema import PerguntaInput
from services.chat_service import chat_instance

router = APIRouter()

@router.post("/chat/pergunta")
async def responder_pergunta(payload: PerguntaInput):
    chat_instance.usuario = payload.usuario
    if chat_instance.chat_id is None:
        chat_instance._selecionar_ou_criar_chat()
    chat_instance.processar_pergunta(payload.pergunta)
    return {"mensagem": "Pergunta processada."}


@router.get("/chat/historico")
async def obter_historico(usuario: str):
    return chat_instance.context_db.listar_chats(usuario)


@router.get("/status")
async def status():
    return {"status": "API online", "modelo": chat_instance.versao}