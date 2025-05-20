from transformers import pipeline

class MotorGeracao:
    def __init__(self, model, tokenizer, generation_config):
        self.tokenizer = tokenizer
        self.pipe = pipeline(
            task="text-generation",
            model=model,
            tokenizer=tokenizer,
            generation_config=generation_config
        )

    def gerar_resposta(self, prompt: str, max_new_tokens=512):
        try:
            resposta = self.pipe(
                prompt,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                max_new_tokens=max_new_tokens
            )[0]['generated_text']
            return resposta.split("<assistant>:")[-1].strip()
        except Exception as e:
            return f"Erro na geração: {str(e)}"
