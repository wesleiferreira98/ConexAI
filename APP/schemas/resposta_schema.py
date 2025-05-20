from pydantic import BaseModel
class RespostaChat(BaseModel):
    mensagem: str
    resposta: str  # opcional para retorno mais informativo
