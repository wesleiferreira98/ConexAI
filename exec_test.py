#import asyncio
import asyncio
import unittest
from APP.test.test_gerador_grafico import testar_gerador_grafico
from APP.test.test_gerador_relatorio import testar_geracao_relatorios
from APP.test.test_personalizacao import executar_teste_de_personalizacao
from APP.test.test_shap_explicator import TestShapExplicator, visualizar_explicacao_manual, visualizar_respostas_simuladas
#from APP.test.test_carregamento_modelos import test_carregamento_modelo_transformers
#from APP.test.test_cac_db import populate_and_test_cac_db
#from APP.test.test_cac_db_exporter import main

testar_gerador_grafico()
testar_geracao_relatorios()
#test_carregamento_modelo_transformers("ConexAI V2")
def rodar_testes_shap_explicator():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestShapExplicator)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    # Instancia a classe e executa método específico manualmente
    print("\n>>>>> Visualizando explicação SHAP manualmente com respostas simuladas <<<<<")
    
    visualizar_respostas_simuladas()
    # Instancia a classe e chama visualização manualmente
    print("\n>>>>> Visualizando explicação SHAP manualmente <<<<<")
    
    visualizar_explicacao_manual()


# Agora chame como as outras funções:
rodar_testes_shap_explicator()


if __name__ == "__main__":
    # Roda a função de teste assíncrona
    asyncio.run(executar_teste_de_personalizacao())