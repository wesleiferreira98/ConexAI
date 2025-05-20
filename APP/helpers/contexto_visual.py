import json
from APP.helpers.gerador_grafico import GeradorEstruturaGrafico

class ExportadorRespostaVisual:
    def __init__(self, exportar_json=True, caminho_exportacao="resposta_estruturada.json"):
        self.gerador = GeradorEstruturaGrafico()
        self.exportar_json = exportar_json
        self.caminho = caminho_exportacao

    def processar(self, resposta_ia):
        estrutura = self.gerador.extrair_dados_de_resposta(resposta_ia)
        if estrutura and self.exportar_json:
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump(estrutura, f, ensure_ascii=False, indent=2)
        return estrutura