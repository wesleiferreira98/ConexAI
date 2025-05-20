class InterfaceTerminal:
    def exibir_boas_vindas(self):
        print("Sistema de Gestão Empresarial - Digite 'sair' para encerrar")

    def solicitar_usuario(self):
        return input("Identifique-se com um nome de usuário: ").strip()

    def exibir_chats_anteriores(self, chats):
        print("\n Seus chats anteriores:")
        if chats:
            for i, (chat_id, nome, data) in enumerate(chats, 1):
                print(f"{i}. {nome} (Criado em {data})")
            print("0. Criar novo chat")
            return input("Escolha um número: ").strip()
        else:
            print("Nenhum chat encontrado. Vamos criar um novo!")
            return "0"

    def solicitar_pergunta(self):
        return input("\nSua pergunta: ")
    
    def exibir_mensagem(self, mensagem):
        print(mensagem)
    
    def exibir_resposta(self, resposta, versao):
        print("\n ConexAI Responde:")
        print(resposta)
        print("\n" + "=" * 50)
        print(f"Fonte: ConexAI {versao} – seu assistente de gestão financeira.")

    def exibir_erro_validacao(self, detalhes):
        print(f"\n Pergunta fora do escopo: {detalhes.get('motivo', 'Motivo desconhecido')}")
        if 'scores' in detalhes:
            print("Detalhes Técnicos:")
            for modelo, score in detalhes['scores'].items():
                print(f"- {modelo.upper()}: {score:.4f}")
