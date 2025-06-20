import logging
from APP.services.chat.formatador_prompt import formatar_prompt, formatar_prompt_com_perfil
import torch
from transformers import GenerationConfig 
from APP.schemas.perfil_schema import PerfilUsuarioSchema
class GeradorRespostaLLM:
    def __init__(self, model, tokenizer=None,generation_config=None,framework="llama_cpp"):
        self.model = model
        self.tokenizer = tokenizer
        self.framework = framework
        self.generation_config=generation_config 

    def gerar_resposta(self, pergunta: str, perfil: PerfilUsuarioSchema) -> str:
        """
        Gera uma resposta da LLM usando um prompt personalizado com base no perfil do usuário.
        
        Args:
            pergunta (str): A pergunta feita pelo usuário.
            perfil (PerfilUsuarioSchema): O objeto de perfil completo do usuário.

        Returns:
            str: A resposta gerada pelo modelo.
        """
        # 3. Removemos os dados fixos e usamos o novo formatador
        try:
            # Esta é a mudança principal: usamos a nova função para criar um prompt rico
            prompt = formatar_prompt_com_perfil(pergunta, perfil)
            
            logging.info(f"Prompt final enviado para o modelo para o usuário '{perfil.id_usuario}':\n{prompt}")

            if self.framework == 'transformers':
                # O código de geração do transformers permanece o mesmo
                resposta = self.model(
                    prompt,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    max_new_tokens=512
                )[0]['generated_text']
                return resposta.split("<assistant>:")[-1].strip()
            
            elif self.framework == 'llama_cpp':
                # O código de geração do llama_cpp permanece o mesmo
                response = self.model(prompt, max_tokens=512)
                return response['choices'][0]['text'].strip()
            
            else:
                raise ValueError(f"Framework '{self.framework}' não é suportado.")
                
        except Exception as e:
            logging.error(f"Erro na geração de resposta para o usuário '{perfil.id_usuario}': {e}", exc_info=True)
            return f"Erro na geração: {str(e)}"

    # AQUI ESTÁ A ASSINATURA CORRETA, que aceita o perfil
    def gerar_resposta(self, pergunta: str, perfil: PerfilUsuarioSchema) -> str:
        """
        Gera uma resposta da LLM usando um prompt personalizado com base no perfil do usuário.
        
        Args:
            pergunta (str): A pergunta feita pelo usuário.
            perfil (PerfilUsuarioSchema): O objeto de perfil completo do usuário.

        Returns:
            str: A resposta gerada pelo modelo.
        """
        # Removemos os dados fixos e usamos o novo formatador
        try:
            # Esta é a mudança principal: usamos a nova função para criar um prompt rico
            prompt = formatar_prompt_com_perfil(pergunta, perfil)
            
            logging.info(f"Prompt final enviado para o modelo para o usuário '{perfil.id_usuario}':\n{prompt}")

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
            logging.error(f"Erro na geração de resposta para o usuário '{perfil.id_usuario}': {e}", exc_info=True)
            return f"Erro na geração: {str(e)}"
