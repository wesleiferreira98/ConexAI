from datetime import datetime

class HistoricoInteracao:
    def __init__(self, context_db, chat_id=None):
        self.registros = []
        self.context_db = context_db
        self.chat_id = chat_id

    def registrar(self, pergunta: str, resposta: str, valido: bool, detalhes: dict):
        registro = {
            'pergunta': pergunta,
            'resposta': resposta,
            'valido': valido,
            'detalhes': detalhes,
            'data': datetime.now().isoformat()
        }
        self.registros.append(registro)

        if self.chat_id:
            self.context_db.adicionar_interacao(self.chat_id, pergunta, resposta)

    def listar(self):
        return self.registros

    def limpar(self):
        self.registros.clear()
        if self.chat_id:
            self.context_db.limpar_contexto(self.chat_id)

    def configurar_chat_id(self, chat_id):
        self.chat_id = chat_id
