from typing import List
from APP.schemas.perfil_schema import PerfilUsuarioSchema


def formatar_prompt(pergunta: str, dados_cliente: dict) -> str:
    contexto = f"""
Empresa: {dados_cliente['empresa']}
Conta: {dados_cliente['conta']}
Saldo: R$ {dados_cliente['saldo']:.2f}
Faturas em aberto: {dados_cliente['faturas_abertas']}
Total em faturas: R$ {dados_cliente['total_faturas']:.2f}
Último pagamento: {dados_cliente['ultimo_pagamento']}
"""

    return f"""<human>:
{pergunta}

Contexto atual:
{contexto.strip()}

Como especialista em gestão empresarial, responda:
1. Análise detalhada do problema
2. 3 ações recomendadas
3. Métricas de acompanhamento

<assistant>:
"""

def formatar_prompt_com_perfil(pergunta: str, perfil: 'PerfilUsuarioSchema', documentos: List[str]) -> str:
    """
    Formata o prompt para a IA, injetando um contexto rico baseado no
    perfil completo do usuário (preferências, histórico e configurações).

    Args:
        pergunta: A pergunta atual do usuário.
        perfil: Um objeto PerfilUsuarioSchema contendo os dados do usuário.
        Contexto Factual: Contem os artigos elaborados pela Conexa mais relevantes para a pergunta do usuario 

    Returns:
        O prompt final, pronto para ser enviado ao modelo de linguagem.
    """
    instrucao_sistema = """Você é o ConexAI, um assistente especialista em análise financeira e gestão de negócios. Suas respostas devem ser claras, bem estruturadas e educativas, sempre mantendo um tom profissional. Responda sempre em Português do Brasil.

Sempre que possível, estruture suas respostas da seguinte forma:
1.  **Definição Concisa:** Comece com uma definição clara e direta do conceito principal.
2.  **Detalhes e Estrutura:** Use listas (com marcadores `*` ou numeradas) para detalhar características, componentes ou critérios importantes. Se houver um acrônimo conhecido (como SMART), explique-o.
3.  **Exemplos Práticos:** Forneça de 2 a 3 exemplos concretos que ajudem a ilustrar o conceito em um cenário de negócios real.
4.  **Diferenciação ou Relevância:** Conclua explicando por que o conceito é importante ou o que o diferencia de outros similares.
"""

    # ... (o resto da função permanece exatamente o mesmo) ...

    # 2. Seção de Documentos Recuperados (Contexto Factual - RAG)
    secao_documentos = ""
    if documentos:
        contexto_documental = "\n\n".join(documentos)
        secao_documentos = f"""---
[BASE DE CONHECIMENTO RELEVANTE]
A seguir, trechos de artigos da nossa base de conhecimento que são relevantes para a pergunta. Baseie sua resposta principalmente nestas informações:

{contexto_documental}
---"""

    # 3. Seção de Perfil do Usuário (Contexto de Personalização)
    partes_contexto_usuario = []
    if perfil.preferencias:
        texto_preferencias = f"Adapte os exemplos e a linguagem aos interesses do usuário: {', '.join(perfil.preferencias)}."
        partes_contexto_usuario.append(texto_preferencias)
    if perfil.configuracoes and perfil.configuracoes.formato_resposta != "padrão":
        texto_config = f"O usuário prefere um formato de resposta '{perfil.configuracoes.formato_resposta}'."
        partes_contexto_usuario.append(texto_config)

    secao_usuario = ""
    if partes_contexto_usuario:
        contexto_usuario_texto = "\n".join(partes_contexto_usuario)
        secao_usuario = f"""
[INFORMAÇÕES ADICIONAIS SOBRE O USUÁRIO]
{contexto_usuario_texto}
---"""

    # 4. Montagem Final do Prompt
    instrucao_final = "\n Com base NAS INFORMAÇÕES DA BASE DE CONHECIMENTO e adaptando-se ao usuário, responda à pergunta:"

    prompt_final = f"""{instrucao_sistema}{secao_documentos}{secao_usuario}{instrucao_final}
<human>: {pergunta}
<assistant>:"""

    return prompt_final
