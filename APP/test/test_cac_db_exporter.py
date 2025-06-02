# 
import asyncio
import logging
from datetime import datetime, timedelta

from matplotlib.dates import relativedelta
from APP.db.cac_storage import CacStorage
from APP.services.cac_exporter import CacExporter # Importa o novo exportador
from APP.test.test_cac_db import populate_and_test_cac_db # Importa o script de população de teste

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    # Primeiro, garanta que o DB de teste esteja populado
    await populate_and_test_cac_db()

    # Define o caminho do DB de teste e do arquivo de saída Excel
    db_path = "cac_reports_test.db"
    output_excel_file = "relatorio_cac_teste.xlsx"

    # Define o período para o relatório mensal
    # Ex: do início de 2024 até o mês atual
    end_month = datetime.now().strftime('%Y-%m')
    start_dt = datetime.now() - relativedelta(months=5) # 6 meses antes
    start_month = start_dt.strftime('%Y-%m')


    cac_storage_instance = CacStorage(db_path=db_path)
    await cac_storage_instance.connect() # Conecta para a exportação

    exporter = CacExporter(cac_storage=cac_storage_instance)

    success = await exporter.export_cac_report_to_excel(
        output_filepath=output_excel_file,
        start_month=start_month,
        end_month=end_month
    )

    if success:
        logging.info(f"Relatório Excel exportado com sucesso para: {output_excel_file}")
    else:
        logging.error("Falha na exportação do relatório Excel.")

    await cac_storage_instance.close() # Fechar a conexão após a exportação

if __name__ == "__main__":
    asyncio.run(main())