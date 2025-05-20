from APP.services.chat.gerador_resposta_llm import GeradorRespostaLLM
from APP.services.chat.formatador_prompt import FormatadorPrompt
from APP.services.chat.motor_geracao import MotorGeracao
from APP.services.chat.interface_terminal import InterfaceTerminal

class ConexAIAssistente:
    def __init__(self, cliente_id: str):
        """
        Inicializa uma instância isolada do assistente ConexAI para um cliente específico.
        :param cliente_id: Identificador único do cliente para garantir isolamento de dados.
        """
        self.cliente_id = cliente_id
        self.prompt_formatador = FormatadorPrompt(cliente_id=cliente_id)
        self.motor_geracao = MotorGeracao(cliente_id=cliente_id)
        self.interface_terminal = InterfaceTerminal()
        self.gerador_resposta = GeradorRespostaLLM(
            formatador=self.prompt_formatador,
            motor=self.motor_geracao
        )

    def responder(self, pergunta_usuario: str) -> str:
        """
        Gera uma resposta segura e contextualizada para a pergunta do usuário.
        :param pergunta_usuario: Entrada de texto do usuário final.
        :return: Resposta gerada pela LLM com base no contexto do cliente.
        """
        prompt = self.prompt_formatador.formatar(pergunta_usuario)
        resposta = self.gerador_resposta.gerar_resposta(prompt)
        return resposta
