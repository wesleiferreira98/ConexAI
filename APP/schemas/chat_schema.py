from pydantic import BaseModel

class PerguntaInput(BaseModel):
    usuario: str
    pergunta: str
