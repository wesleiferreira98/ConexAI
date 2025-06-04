# test_cac_db.py
import asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta # Para adicionar meses facilmente
import logging
import random # Para gerar dados simulados

from APP.db.cac_storage import CacStorage # Ajuste o caminho se necessário

# Configura o logging para ver as mensagens do CacStorage
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def populate_and_test_cac_db():
    logging.info("Iniciando população e testes do banco de dados CAC para todos os meses de 2025...")
    
    db_path = "cac_reports_test.db" # Usar um DB de teste separado para não misturar
    cac_db = CacStorage(db_path=db_path)

    try:
        await cac_db.connect() # Conecta ao DB e cria tabelas se não existirem

        logging.info("\n--- Limpando dados existentes para testes repetidos ---")
        async with cac_db._conn.cursor() as cursor:
            await cursor.execute("DELETE FROM despesas")
            await cursor.execute("DELETE FROM clientes")
            await cac_db._conn.commit()
        logging.info("Dados de teste anteriores removidos.")

        base_year = 2025

        logging.info(f"\n--- Adicionando Despesas e Clientes para cada mês de {base_year} ---")

        for month in range(1, 13): # Loop para cada mês de Janeiro a Dezembro
            current_month_str = f"{base_year}-{month:02d}"
            
            # Calcular o último dia do mês para datas de despesas/clientes
            if month == 12:
                last_day_of_month = datetime(base_year, 12, 31)
            else:
                last_day_of_month = datetime(base_year, month + 1, 1) - timedelta(days=1)
            
            logging.info(f"Processando dados para {current_month_str}...")

            # --- Adicionando Despesas para o Mês Atual ---
            
            # Despesas fixas (com valor ligeiramente variável para simulação)
            salario_vendedor_a_val = 3000.00 + random.randint(-100, 100)
            await cac_db.adicionar_despesa(f"Salário Vendedor A {current_month_str}", salario_vendedor_a_val, 
                                           f"{current_month_str}-28", f"{current_month_str}-15", True, True, 70.0) # 70% no CAC
            
            licenca_crm_val = 300.00 + random.randint(-20, 20)
            await cac_db.adicionar_despesa(f"Licença CRM {current_month_str}", licenca_crm_val, 
                                           f"{current_month_str}-01", f"{current_month_str}-01", True, True, 100.0)

            # Despesas variáveis (simulando flutuação de campanhas)
            google_ads_val = random.uniform(1500.00, 2500.00)
            await cac_db.adicionar_despesa(f"Campanha Google Ads {current_month_str}", google_ads_val, 
                                           f"{current_month_str}-{random.randint(5, 15)}", f"{current_month_str}-01", False, True, 100.0)
            
            facebook_ads_val = random.uniform(1800.00, 3000.00)
            await cac_db.adicionar_despesa(f"Campanha Facebook Ads {current_month_str}", facebook_ads_val, 
                                           f"{current_month_str}-{random.randint(10, 20)}", f"{current_month_str}-05", False, True, 100.0)
            
            consultoria_marketing_val = random.uniform(800.00, 1500.00)
            await cac_db.adicionar_despesa(f"Consultoria Marketing {current_month_str}", consultoria_marketing_val, 
                                           f"{current_month_str}-{random.randint(20, last_day_of_month.day)}", f"{current_month_str}-10", False, True, 100.0)
            
            # Despesa que NÃO entra no CAC (para testar o filtro)
            despesa_admin_val = 400.00 + random.randint(-50, 50)
            await cac_db.adicionar_despesa(f"Despesa Administrativa {current_month_str}", despesa_admin_val, 
                                           f"{current_month_str}-25", f"{current_month_str}-20", True, False, 0.0)

            # --- Adicionando Clientes e Registrando Primeiras Vendas Pagantes para o Mês Atual ---
            
            num_new_clients_this_month = random.randint(2, 6) # Simula 2 a 6 novos clientes por mês
            for i in range(num_new_clients_this_month):
                client_day_of_sale = random.randint(1, last_day_of_month.day)
                first_sale_date_str = f"{base_year}-{month:02d}-{client_day_of_sale:02d}"
                
                # Data de cadastro pode ser um pouco antes da primeira venda
                cadastro_date_dt = datetime(base_year, month, client_day_of_sale) - timedelta(days=random.randint(1, 10))
                cadastro_date_str = cadastro_date_dt.strftime('%Y-%m-%d')

                client_name = f"Cliente {current_month_str}-{i+1} (ID Interno: {random.randint(1000, 9999)})"
                new_client_id = await cac_db.adicionar_cliente(client_name, cadastro_date_str)
                await cac_db.registrar_primeira_venda_pagante_cliente(new_client_id, first_sale_date_str)
        
        logging.info(f"\n--- Todos os dados de {base_year} adicionados. Testando Cálculos de CAC ---")

        # Testar cálculos para alguns meses específicos e para o final do ano
        months_to_test = [f"{base_year}-{m:02d}" for m in range(1, 13)] # Todos os meses de 2025

        for mes in months_to_test:
            total_despesas_cac = await cac_db.calcular_total_despesas_cac_mensal(mes)
            num_novos_clientes = await cac_db.contar_novos_clientes_mensal(mes)
            cac_mensal = await cac_db.calcular_cac_mensal(mes)
            
            logging.info(f"Relatório CAC para {mes}:")
            logging.info(f"  Despesas CAC: R$ {total_despesas_cac:.2f}")
            logging.info(f"  Novos Clientes: {num_novos_clientes}")
            logging.info(f"  CAC: R$ {cac_mensal:.2f}")

        # Testar um mês sem dados (ex: Janeiro do próximo ano)
        mes_sem_dados = f"{base_year + 1}-01"
        cac_sem_dados = await cac_db.calcular_cac_mensal(mes_sem_dados)
        logging.info(f"Relatório CAC para {mes_sem_dados}: R$ {cac_sem_dados:.2f} (Esperado 0.00)")

    except Exception as e:
        logging.error(f"Erro durante a população e teste do DB: {e}", exc_info=True)
    finally:
        await cac_db.close()
        logging.info("População e testes do banco de dados CAC finalizados.")

if __name__ == "__main__":
    asyncio.run(populate_and_test_cac_db())



# Esperado para 2025-05:
# Despesas: 2500 (100%) + 3000 * 0.7 (2100) + 300 (100%) = 2500 + 2100 + 300 = 4900.00
# Clientes: 2
# CAC: 4900 / 2 = 2450.00

# Esperado para 2025-04:
# Despesas: 2000 (100%) + 3500 * 0.6 (2100) + 1000 (100%) = 2000 + 2100 + 1000 = 5100.00
# Clientes: 4
# CAC: 5100 / 4 = 1275.00
# Calcular para Maio de 2025 (mês atual - se rodar em maio)

# Esperado para 2025-03:
# Despesas: 1500 (100%) + 3000 * 0.7 (2100) + 200 (100%) = 1500 + 2100 + 200 = 3800.00
# Clientes: 3
# CAC: 3800 / 3 = 1266.67
# Calcular para Abril de 2025