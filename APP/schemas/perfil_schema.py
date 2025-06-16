from pydantic import BaseModel, Field
from typing import List, Optional

class ConfiguracoesSchema(BaseModel):
    """Define as configurações de preferência do usuário."""
    nivel_experiencia: Optional[str] = Field(
        default="não informado",
        description="Nível de experiência do usuário (ex: iniciante, intermediário, avançado)."
    )
    formato_resposta: Optional[str] = Field(
        default="padrão",
        description="Formato de resposta preferido (ex: conciso, detalhado com exemplos)."
    )

class PerfilUsuarioSchema(BaseModel):
    """Esquema completo para o perfil de um usuário."""
    id_usuario: str = Field(..., description="Identificador único do usuário.")
    
    nome: Optional[str] = Field(None, description="Nome do usuário.")
    
    preferencias: List[str] = Field(
        default_factory=list,
        description="Lista de tópicos de preferência do usuário."
    )
    
    historico_interacoes: List[str] = Field(
        default_factory=list,
        description="Lista das últimas interações (perguntas) do usuário."
    )
    
    configuracoes: ConfiguracoesSchema = Field(
        default_factory=ConfiguracoesSchema,
        description="Configurações personalizadas do usuário."
    )

    class ConfigSchema:
        # Exemplo de como o schema se pareceria em JSON
        schema_extra = {
            "example": {
                "id_usuario": "user-abc-123",
                "nome": "Weslei",
                "preferencias": ["IA generativa", "Python", "API REST"],
                "historico_interacoes": [
                    "O que é o mecanismo de atenção em transformers?",
                    "Como usar o Pydantic para validação de dados?"
                ],
                "configuracoes": {
                    "nivel_experiencia": "avançado",
                    "formato_resposta": "detalhado com exemplos de código"
                }
            }
        }