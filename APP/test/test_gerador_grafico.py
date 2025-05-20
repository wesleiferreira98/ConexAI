from APP.helpers.gerador_grafico import GeradorEstruturaGrafico

def testar_gerador_grafico():
    gerador = GeradorEstruturaGrafico()
    
    # Teste 1: Dados temporais
    resposta_temporal = "A receita da empresa ao longo do ano foi a seguinte: Janeiro - R$ 1.000, Fevereiro - R$ 1.500, Março - R$ 2.000. O desempenho foi consistente."
    resultado_temporal = gerador.extrair_dados_de_resposta(resposta_temporal)
    print(" Teste 1 (Temporal):", resultado_temporal)
    
    # Teste 2: Dados percentuais
    resposta_percentual = "A distribuição do orçamento é a seguinte: Marketing - 40%, Vendas - 30%, RH - 20%, TI - 10%."
    resultado_percentual = gerador.extrair_dados_de_resposta(resposta_percentual)
    print(" Teste 2 (Percentual):", resultado_percentual)
    
    # Teste 3: Dados categóricos
    resposta_categorica = "As vendas por produto foram: Produto A: R$ 500, Produto B: R$ 700, Produto C: R$ 300. Isso indica um bom desempenho para o Produto B."
    resultado_categorica = gerador.extrair_dados_de_resposta(resposta_categorica)
    print(" Teste 3 (Categórico):", resultado_categorica)
    
    # Teste 4: Resposta sem dados estruturados
    resposta_sem_dados = "Este é apenas um texto descritivo sem dados numéricos relevantes."
    resultado_sem_dados = gerador.extrair_dados_de_resposta(resposta_sem_dados)
    print(" Teste 4 (Sem Dados):", resultado_sem_dados)
    
    # Teste 5: Mistura de dados
    resposta_mista = "Ao longo do ano, as vendas foram: Janeiro - R$ 1.000, Fevereiro - R$ 1.500, enquanto a distribuição do orçamento foi Marketing - 40%, Vendas - 30%."
    resultado_mista = gerador.extrair_dados_de_resposta(resposta_mista)
    print(" Teste 5 (Misto):", resultado_mista)



