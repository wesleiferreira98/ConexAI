from APP.services.chat.formatador_prompt import formatar_prompt

class GeradorRespostaLLM:
    def __init__(self, model, tokenizer=None, framework="llama_cpp"):
        self.model = model
        self.tokenizer = tokenizer
        self.framework = framework

    def gerar_resposta(self, pergunta: str) -> str:
        dados_cliente = {
            "empresa": "Tech Solutions",
            "conta": "12345",
            "saldo": 1500.75,
            "faturas_abertas": 3,
            "total_faturas": 3500.50,
            "ultimo_pagamento": "2025-04-25"
        }

        try:
            prompt = formatar_prompt(pergunta, dados_cliente)
            if self.framework == 'transformers':
                resposta = self.model(
                    prompt,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    max_new_tokens=512
                )[0]['generated_text']
                return resposta.split("<assistant>:")[-1].strip()
            elif self.framework == 'llama_cpp':
                response = self.model(prompt, max_tokens=512)
                return response['choices'][0]['text'].strip()
            else:
                raise ValueError(f"Framework '{self.framework}' não é suportado.")
        except Exception as e:
            return f"Erro na geração: {str(e)}"
