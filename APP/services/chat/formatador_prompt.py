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
