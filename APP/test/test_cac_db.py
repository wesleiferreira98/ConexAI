# test_cac_db.py
import asyncio
from datetime import datetime, timedelta
import logging
from APP.db.cac_storage import CacStorage # Ajuste o caminho se necessário

# Configura o logging para ver as mensagens do CacStorage
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def populate_and_test_cac_db():
    logging.info("Iniciando população e testes do banco de dados CAC...")
    
    db_path = "cac_reports_test.db" # Usar um DB de teste separado para não misturar
    cac_db = CacStorage(db_path=db_path)

    try:
        await cac_db.connect() # Conecta ao DB e cria tabelas se não existirem

        logging.info("\n--- Limpando dados existentes (opcional para testes repetidos) ---")
        async with cac_db._conn.cursor() as cursor:
            await cursor.execute("DELETE FROM despesas")
            await cursor.execute("DELETE FROM clientes")
            await cac_db._conn.commit()
        logging.info("Dados de teste anteriores removidos.")


        logging.info("\n--- Adicionando Despesas ---")
        # Despesas de marketing e vendas (com data de competência no passado para testes)
        
        # Mês de Março de 2024 (2024-03)
        await cac_db.adicionar_despesa("Campanha Google Ads Março", 1500.00, "2024-03-10", "2024-03-01", False, True, 100.0)
        await cac_db.adicionar_despesa("Salário Vendedor A Março", 3000.00, "2024-03-31", "2024-03-15", True, True, 70.0) # 70% do salário
        await cac_db.adicionar_despesa("Ferramenta SEO Assinatura Março", 200.00, "2024-03-05", "2024-02-28", True, True, 100.0)
        await cac_db.adicionar_despesa("Despesa Administrativa Março", 500.00, "2024-03-20", "2024-03-10", True, False, 0.0) # Não considera no CAC

        # Mês de Abril de 2024 (2024-04)
        await cac_db.adicionar_despesa("Campanha Facebook Ads Abril", 2000.00, "2024-04-15", "2024-04-01", False, True, 100.0)
        await cac_db.adicionar_despesa("Salário Vendedor B Abril", 3500.00, "2024-04-30", "2024-04-15", True, True, 60.0) # 60% do salário
        await cac_db.adicionar_despesa("Consultoria Marketing Abril", 1000.00, "2024-04-25", "2024-04-05", False, True, 100.0)
        await cac_db.adicionar_despesa("Aluguel Escritório Abril", 1200.00, "2024-04-01", "2024-03-28", True, False, 0.0)

        # Mês de Maio de 2024 (2024-05) - Mês atual para simular "mês anterior"
        await cac_db.adicionar_despesa("Campanha Google Ads Maio", 2500.00, "2024-05-10", "2024-05-01", False, True, 100.0)
        await cac_db.adicionar_despesa("Salário Vendedor A Maio", 3000.00, "2024-05-31", "2024-05-15", True, True, 70.0)
        await cac_db.adicionar_despesa("Licença CRM Maio", 300.00, "2024-05-01", "2024-04-25", True, True, 100.0)
        await cac_db.adicionar_despesa("Despesa de Viagem Maio", 800.00, "2024-05-20", "2024-05-10", False, False, 0.0)


        logging.info("\n--- Adicionando Clientes e Registrando Primeiras Vendas Pagantes ---")
        
        # Clientes de Março de 2024
        c1_id = await cac_db.adicionar_cliente("Cliente Alfa Ltda.", "2024-02-20")
        await cac_db.registrar_primeira_venda_pagante_cliente(c1_id, "2024-03-05")
        
        c2_id = await cac_db.adicionar_cliente("Cliente Beta S.A.", "2024-03-01")
        await cac_db.registrar_primeira_venda_pagante_cliente(c2_id, "2024-03-15")
        
        c3_id = await cac_db.adicionar_cliente("Cliente Gama MEI", "2024-03-10")
        await cac_db.registrar_primeira_venda_pagante_cliente(c3_id, "2024-03-25")
        
        # Clientes de Abril de 2024
        c4_id = await cac_db.adicionar_cliente("Cliente Delta Ltda.", "2024-03-28")
        await cac_db.registrar_primeira_venda_pagante_cliente(c4_id, "2024-04-02")
        
        c5_id = await cac_db.adicionar_cliente("Cliente Epsilon S.A.", "2024-04-05")
        await cac_db.registrar_primeira_venda_pagante_cliente(c5_id, "2024-04-10")
        
        c6_id = await cac_db.adicionar_cliente("Cliente Zeta Consultoria", "2024-04-18")
        await cac_db.registrar_primeira_venda_pagante_cliente(c6_id, "2024-04-22")
        
        c7_id = await cac_db.adicionar_cliente("Cliente Eta Finanças", "2024-04-20")
        await cac_db.registrar_primeira_venda_pagante_cliente(c7_id, "2024-04-28")

        # Clientes de Maio de 2024 (mês atual)
        c8_id = await cac_db.adicionar_cliente("Cliente Theta Marketing", "2024-05-01")
        await cac_db.registrar_primeira_venda_pagante_cliente(c8_id, "2024-05-05")
        
        c9_id = await cac_db.adicionar_cliente("Cliente Iota Tecnologia", "2024-05-10")
        await cac_db.registrar_primeira_venda_pagante_cliente(c9_id, "2024-05-18")


        logging.info("\n--- Testando Cálculos de CAC ---")
        
        # Calcular para Março de 2024
        mes_marco = "2024-03"
        total_despesas_marco = await cac_db.calcular_total_despesas_cac_mensal(mes_marco)
        num_clientes_marco = await cac_db.contar_novos_clientes_mensal(mes_marco)
        cac_marco = await cac_db.calcular_cac_mensal(mes_marco)
        logging.info(f"Relatório CAC para {mes_marco}:")
        logging.info(f"  Despesas CAC: R$ {total_despesas_marco:.2f}")
        logging.info(f"  Novos Clientes: {num_clientes_marco}")
        logging.info(f"  CAC: R$ {cac_marco:.2f}")
        
        # Esperado para 2024-03:
        # Despesas: 1500 (100%) + 3000 * 0.7 (2100) + 200 (100%) = 1500 + 2100 + 200 = 3800.00
        # Clientes: 3
        # CAC: 3800 / 3 = 1266.67

        # Calcular para Abril de 2024
        mes_abril = "2024-04"
        total_despesas_abril = await cac_db.calcular_total_despesas_cac_mensal(mes_abril)
        num_clientes_abril = await cac_db.contar_novos_clientes_mensal(mes_abril)
        cac_abril = await cac_db.calcular_cac_mensal(mes_abril)
        logging.info(f"Relatório CAC para {mes_abril}:")
        logging.info(f"  Despesas CAC: R$ {total_despesas_abril:.2f}")
        logging.info(f"  Novos Clientes: {num_clientes_abril}")
        logging.info(f"  CAC: R$ {cac_abril:.2f}")

        # Esperado para 2024-04:
        # Despesas: 2000 (100%) + 3500 * 0.6 (2100) + 1000 (100%) = 2000 + 2100 + 1000 = 5100.00
        # Clientes: 4
        # CAC: 5100 / 4 = 1275.00

        # Calcular para Maio de 2024 (mês atual - se rodar em maio)
        mes_maio = "2024-05"
        total_despesas_maio = await cac_db.calcular_total_despesas_cac_mensal(mes_maio)
        num_clientes_maio = await cac_db.contar_novos_clientes_mensal(mes_maio)
        cac_maio = await cac_db.calcular_cac_mensal(mes_maio)
        logging.info(f"Relatório CAC para {mes_maio}:")
        logging.info(f"  Despesas CAC: R$ {total_despesas_maio:.2f}")
        logging.info(f"  Novos Clientes: {num_clientes_maio}")
        logging.info(f"  CAC: R$ {cac_maio:.2f}")

        # Esperado para 2024-05:
        # Despesas: 2500 (100%) + 3000 * 0.7 (2100) + 300 (100%) = 2500 + 2100 + 300 = 4900.00
        # Clientes: 2
        # CAC: 4900 / 2 = 2450.00

        # Testar mês sem dados
        mes_futuro = "2024-06"
        cac_futuro = await cac_db.calcular_cac_mensal(mes_futuro)
        logging.info(f"Relatório CAC para {mes_futuro}: R$ {cac_futuro:.2f}") # Deve ser 0.0

    except Exception as e:
        logging.error(f"Erro durante a população e teste do DB: {e}", exc_info=True)
    finally:
        await cac_db.close()
        logging.info("População e testes do banco de dados CAC finalizados.")

if __name__ == "__main__":
    # Para rodar a função assíncrona
    asyncio.run(populate_and_test_cac_db())