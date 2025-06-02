import asyncio
#from APP.test.test_gerador_grafico import testar_gerador_grafico
#from APP.test.test_gerador_relatorio import testar_geracao_relatorios
#from APP.test.test_carregamento_modelos import test_carregamento_modelo_transformers
#from APP.test.test_cac_db import populate_and_test_cac_db
from APP.test.test_cac_db_exporter import main

#testar_gerador_grafico()
#testar_geracao_relatorios()
#test_carregamento_modelo_transformers("ConexAI V2")

asyncio.run(main())