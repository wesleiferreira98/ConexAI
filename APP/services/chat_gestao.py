from APP.db.contexto_db import ContextStorage
from APP.helpers.contexto_visual import ExportadorRespostaVisual
from APP.services.chat.interface_terminal import InterfaceTerminal
from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM
from APP.services.chat.formatador_prompt import formatar_prompt
from APP.helpers.historico_interacao import HistoricoInteracao
from APP.helpers.gerador_grafico import GeradorEstruturaGrafico

class ChatGestao:
    def __init__(self, validador, gerador: GeradorRespostaLLM, context_db: ContextStorage, versao="ConexAI Vteste"):
        self.validador = validador
        self.gerador = gerador
        self.context_db = context_db
        self.versao = versao

        self.chat_id = None
        self.usuario = None
        self.novo_chat_temp = False
        self.interface = InterfaceTerminal()
        self.historico = HistoricoInteracao(self.context_db)
        self.gerador_grafico = GeradorEstruturaGrafico()

    def iniciar_chat(self):
        self.interface.exibir_boas_vindas()
        self.usuario = self.interface.solicitar_usuario()
        self._selecionar_ou_criar_chat()

        while True:
            pergunta = self.interface.solicitar_pergunta()
            if pergunta.lower() in ['sair', 'exit']:
                break
            self.processar_pergunta(pergunta)

    def _selecionar_ou_criar_chat(self):
        chats = self.context_db.listar_chats(self.usuario)
        self.novo_chat_temp = False

        escolha = self.interface.exibir_chats_anteriores(chats)

        if escolha == "0":
            self.novo_chat_temp = True
            self.interface.exibir_mensagem("🔧 O nome do novo chat será definido com base na primeira pergunta enviada.")
        else:
            idx = int(escolha) - 1
            self.chat_id = chats[idx][0]
            self.historico.configurar_chat_id(self.chat_id)

    def processar_pergunta(self, pergunta: str):
        valido, detalhes = self.validador.validar_pergunta(pergunta)

        if valido:
            resposta = self.gerador.gerar_resposta(pergunta)
            self.historico.registrar(pergunta, resposta, valido, detalhes)
            self._responder_pergunta_valida(pergunta, resposta)
            dados_grafico = self.gerador_grafico.extrair_dados_de_resposta(resposta)

            if dados_grafico:
                self.interface.exibir_mensagem("\n🔍 Dados estruturados detectados, gerando gráfico...")
                exportador = ExportadorRespostaVisual()
                exportador.exportar(dados_grafico)

        else:
            self.historico.registrar(pergunta, "", valido, detalhes)
            self._responder_pergunta_invalida(detalhes)
        return resposta

    def _responder_pergunta_valida(self, pergunta: str, resposta: str):
        self.interface.exibir_mensagem("\nProcessando sua consulta...")
        self.interface.exibir_resposta(resposta, self.versao)

        if self.novo_chat_temp:
            nome_chat = pergunta.strip()[:40].capitalize()
            self.chat_id = self.context_db.criar_chat(self.usuario, nome_chat)
            self.historico.configurar_chat_id(self.chat_id)
            self.novo_chat_temp = False
        

    def _responder_pergunta_invalida(self, detalhes: dict):
        self.interface.exibir_erro_validacao(detalhes)
