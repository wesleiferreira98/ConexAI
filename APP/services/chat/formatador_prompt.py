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

def formatar_prompt_com_perfil(pergunta: str, perfil: 'PerfilUsuarioSchema') -> str:
    """
    Formata o prompt para a IA, injetando um contexto rico baseado no
    perfil completo do usuário (preferências, histórico e configurações).

    Args:
        pergunta: A pergunta atual do usuário.
        perfil: Um objeto PerfilUsuarioSchema contendo os dados do usuário.

    Returns:
        O prompt final, pronto para ser enviado ao modelo de linguagem.
    """
    partes_contexto = []

    # 1. Adiciona as preferências
    if perfil.preferencias:
        texto_preferencias = f"O usuário tem interesse em: {', '.join(perfil.preferencias)}."
        partes_contexto.append(texto_preferencias)

    # 2. Adiciona as configurações
    if perfil.configuracoes:
        nivel = perfil.configuracoes.nivel_experiencia
        formato = perfil.configuracoes.formato_resposta
        if nivel != "não informado" or formato != "padrão":
            texto_config = f"O usuário se identifica com o nível '{nivel}' e prefere respostas no formato '{formato}'."
            partes_contexto.append(texto_config)

    # 3. Adiciona o histórico de interações
    if perfil.historico_interacoes:
        # Formata o histórico para o formato Pergunta/Resposta que os modelos entendem bem
        historico_formatado = "\n".join([f"Pergunta anterior: {interacao['pergunta']}\nResposta anterior: {interacao['resposta']}" for interacao in perfil.historico_interacoes])
        partes_contexto.append(f"Este é um resumo de suas interações recentes:\n{historico_formatado}")

    # Monta o prompt final
    if partes_contexto:
        contexto_texto = "\n".join(partes_contexto)
        prompt_final = f"""Use o seguinte contexto sobre o usuário para personalizar sua resposta:
---
[CONTEXTO DO USUÁRIO]
{contexto_texto}
---

Com base nesse contexto, responda à pergunta do usuário:
<human>: {pergunta}
<assistant>:"""
    else:
        # Fallback se não houver perfil (TSK053.04)
        prompt_final = f"""<human>: {pergunta}
<assistant>:"""

    return prompt_final