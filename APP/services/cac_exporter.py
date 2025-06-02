# APP/services/cac_exporter.py
import pandas as pd
import asyncio
from datetime import datetime
from dateutil.relativedelta import relativedelta # pip install python-dateutil
import logging
from typing import List, Dict, Any, Optional

from APP.db.cac_storage import CacStorage # Importa a classe CacStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CacExporter:
    def __init__(self, cac_storage: CacStorage):
        self.cac_storage = cac_storage
        logging.info("CacExporter inicializado.")

    async def _get_data_as_dataframe(self, query: str) -> pd.DataFrame:
        """
        Executa uma consulta SQL e retorna os resultados como um DataFrame do pandas.
        """
        async with self.cac_storage._conn.cursor() as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()
            # Obtém os nomes das colunas a partir da descrição do cursor
            columns = [description[0] for description in cursor.description]
            return pd.DataFrame(rows, columns=columns)

    async def export_cac_report_to_excel(self, output_filepath: str, start_month: str, end_month: str) -> bool:
        """
        Exporta dados brutos de despesas e clientes, e o relatório mensal de CAC
        para um arquivo Excel (.xlsx).

        Args:
            output_filepath (str): Caminho completo para o arquivo Excel de saída (ex: "relatorio_cac.xlsx").
            start_month (str): Mês de início para o relatório mensal no formato "YYYY-MM".
            end_month (str): Mês de fim para o relatório mensal no formato "YYYY-MM".

        Returns:
            bool: True se a exportação foi bem-sucedida, False caso contrário.
        """
        logging.info(f"Iniciando exportação do relatório CAC para '{output_filepath}'...")
        
        try:
            # Conecta ao banco de dados se não estiver conectado (para uso isolado)
            if not self.cac_storage._conn:
                await self.cac_storage.connect()
                logging.info("Conexão do CacStorage estabelecida para exportação.")

            # Cria um objeto ExcelWriter do pandas
            # 'engine' é definido explicitamente para openpyxl
            with pd.ExcelWriter(output_filepath, engine='openpyxl') as writer:
                logging.info("Exportando dados brutos de despesas...")
                # 1. Exportar Despesas Brutas
                df_despesas = await self._get_data_as_dataframe("SELECT * FROM despesas ORDER BY data_competencia DESC")
                df_despesas.to_excel(writer, sheet_name='Despesas Brutas', index=False)
                logging.info(f"Despesas Brutas: {len(df_despesas)} linhas exportadas.")

                logging.info("Exportando dados brutos de clientes...")
                # 2. Exportar Clientes Brutos
                df_clientes = await self._get_data_as_dataframe("SELECT * FROM clientes ORDER BY data_cadastro DESC")
                df_clientes.to_excel(writer, sheet_name='Clientes Brutos', index=False)
                logging.info(f"Clientes Brutos: {len(df_clientes)} linhas exportadas.")

                logging.info(f"Gerando relatório mensal de CAC de {start_month} a {end_month}...")
                # 3. Gerar e Exportar Relatório Mensal de CAC
                cac_summary_data = []
                
                # Gerar lista de meses no intervalo
                current_month = datetime.strptime(start_month, '%Y-%m')
                end_dt = datetime.strptime(end_month, '%Y-%m')

                while current_month <= end_dt:
                    mes_str = current_month.strftime('%Y-%m')
                    total_despesas = await self.cac_storage.calcular_total_despesas_cac_mensal(mes_str)
                    num_clientes = await self.cac_storage.contar_novos_clientes_mensal(mes_str)
                    cac = await self.cac_storage.calcular_cac_mensal(mes_str)
                    
                    cac_summary_data.append({
                        'Mes_Ano': mes_str,
                        'Total_Despesas_CAC': total_despesas,
                        'Novos_Clientes_Adquiridos': num_clientes,
                        'CAC_Mensal': cac
                    })
                    current_month += relativedelta(months=1) # Avança para o próximo mês

                df_cac_summary = pd.DataFrame(cac_summary_data)
                
                # Formatar colunas monetárias para melhor visualização no Excel
                df_cac_summary['Total_Despesas_CAC'] = df_cac_summary['Total_Despesas_CAC'].map('R$ {:,.2f}'.format)
                df_cac_summary['CAC_Mensal'] = df_cac_summary['CAC_Mensal'].map('R$ {:,.2f}'.format)

                df_cac_summary.to_excel(writer, sheet_name='CAC_Mensal_Resumo', index=False)
                logging.info(f"Relatório de CAC Mensal: {len(df_cac_summary)} meses exportados.")

            logging.info(f"Exportação concluída com sucesso para '{output_filepath}'.")
            return True

        except Exception as e:
            logging.error(f"Erro durante a exportação do relatório CAC para Excel: {e}", exc_info=True)
            return False
        finally:
            # Fechar conexão se ela foi aberta por este exportador para uso isolado
            if self.cac_storage._conn and output_filepath.endswith("_test.xlsx"): # Exemplo de como controlar o fechamento
                await self.cac_storage.close()