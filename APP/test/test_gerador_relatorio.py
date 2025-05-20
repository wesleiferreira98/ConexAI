from APP.helpers.relatorio_generator import RelatorioGenerator


def testar_geracao_relatorios():
    rg = RelatorioGenerator()
    rg._criar_tabelas_teste()
    print("Testando geração de relatórios...")
    resultado = rg.gerar_relatorio("Faturamento", formato="xlsx", periodo=("2024-01-01", "2024-12-31"),
                                    usuario="weslei", chat_id=1)
    print(resultado)