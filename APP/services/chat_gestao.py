from APP.db.contexto_db import ContextStorage
from APP.helpers.contexto_visual import ExportadorRespostaVisual
from APP.services.chat.interface_terminal import InterfaceTerminal
from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM
from APP.services.chat.formatador_prompt import formatar_prompt
from APP.helpers.historico_interacao import HistoricoInteracao
from APP.helpers.gerador_grafico import GeradorEstruturaGrafico


# Importações para explicabilidade
from APP.helpers.explicabilidade.utils import formatar_explicacao # preparar_dados_para_explicacao não é mais tão crítica aqui
from APP.helpers.explicabilidade.shap_explicator import ShapExplicator # Para type hinting
import lime.lime_text # Para type hinting e garantir que estamos usando o certo
class ChatGestao:
    def __init__(self, validador, gerador: GeradorRespostaLLM, context_db: ContextStorage, 
                 versao="ConexAI Vteste", mock_llm_for_explanation=None, # Novo parâmetro
                 lime_explicator: lime.lime_text.LimeTextExplainer = None, 
                 shap_explicator: ShapExplicator = None):
        
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
        
        self.mock_llm_for_explanation = mock_llm_for_explanation # Guarda a instância do mock
        self.lime_explicator = lime_explicator
        self.shap_explicator = shap_explicator

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
        resposta = "" 

        if valido:
            self.interface.exibir_mensagem("\nProcessando sua consulta...")
            resposta = self.gerador.gerar_resposta(pergunta)
            self.historico.registrar(pergunta, resposta, valido, detalhes)
            self._responder_pergunta_valida(pergunta, resposta)

            # --- Adição da explicabilidade ---
            # Verifica se os explicadores e o mock LLM estão disponíveis
            if self.lime_explicator and self.mock_llm_for_explanation:
                try:
                    self.interface.exibir_mensagem("\n--- Gerando Explicação LIME (Texto) ---")
                    # explain_instance espera: text_instance (a pergunta original), 
                    # classifier_fn (a função predict_proba do mock), e num_features.
                    lime_explanation = self.lime_explicator.explain_instance(
                        text_instance=pergunta,
                        classifier_fn=self.mock_llm_for_explanation.predict_proba,
                        labels=[1], # Qual classe queremos explicar? 1 = "Sobre_Gestao"
                        num_features=5 # Quantas palavras mais importantes
                    )
                    # exibe as palavras mais importantes para a classe "Sobre_Gestao"
                    self.interface.exibir_mensagem(
                        f"\nPalavras mais importantes da sua pergunta para a IA gerar resposta sobre 'Gestão':\n"
                        f"{formatar_explicacao(lime_explanation.as_list(label=1))}"
                    )
                except Exception as e:
                    self.interface.exibir_erro(f"Erro ao gerar explicação LIME: {e}")

            if self.shap_explicator:
                try:
                    self.interface.exibir_mensagem("\n--- Gerando Explicação SHAP (Texto) ---")
                    # O ShapExplicator já está configurado para receber o texto
                    shap_explanation = self.shap_explicator.explicar(pergunta)
                    self.interface.exibir_mensagem(
                        f"\nContribuição das palavras da sua pergunta (SHAP):\n"
                        f"{formatar_explicacao(shap_explanation)}"
                    )
                except Exception as e:
                    self.interface.exibir_erro(f"Erro ao gerar explicação SHAP: {e}")
            # --- Fim da adição da explicabilidade ---

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
        self.interface.exibir_resposta(resposta, self.versao)

        if self.novo_chat_temp:
            nome_chat = pergunta.strip()[:40].capitalize()
            self.chat_id = self.context_db.criar_chat(self.usuario, nome_chat)
            self.historico.configurar_chat_id(self.chat_id)
            self.novo_chat_temp = False
        

    def _responder_pergunta_invalida(self, detalhes: dict):
        self.interface.exibir_erro_validacao(detalhes)