import re
import json
from dateutil import parser

class GeradorEstruturaGrafico:
    def __init__(self):
        pass

    def extrair_dados_de_resposta(self, resposta: str):
        """
        Analisa a resposta textual da IA e tenta extrair dados estruturados para visualização gráfica.
        """

        dados = []
        tipo_grafico = "pizza"
        is_temporal = False

        # 🔹 Padrão: Data - Valor
        padrao_temporal = re.findall(r'([\w\s\d/]+)[\s\-:]+R?\$?\s?([\d\.,]+)', resposta)

        for label, valor in padrao_temporal:
            try:
                data_possivel = parser.parse(label, fuzzy=True, dayfirst=True)
                valor_formatado = float(valor.replace('.', '').replace(',', '.'))
                dados.append({"data": data_possivel.strftime("%Y-%m"), "valor": valor_formatado})
                is_temporal = True
            except:
                continue

        if is_temporal:
            return {
                "grafico": "linha",
                "titulo": "Evolução temporal extraída",
                "dados": dados,
                "moeda": "BRL"
            }

        # 🔹 Padrão: Categoria: Valor
        padrao_categoria_valor = re.findall(r'[\d\.\)]*\s*([\w\s]+?)\s*[:=]\s*R?\$?\s?([\d\.,]+)', resposta)

        if padrao_categoria_valor:
            for label, valor in padrao_categoria_valor:
                try:
                    valor_formatado = float(valor.replace('.', '').replace(',', '.'))
                    dados.append({"categoria": label.strip(), "valor": valor_formatado})
                except:
                    continue

            return {
                "grafico": "barra" if len(dados) > 4 else "pizza",
                "titulo": "Distribuição extraída",
                "dados": dados,
                "moeda": "BRL"
            }

        # 🔹 Padrão: Categoria - XX%
        padrao_percentual = re.findall(r'([\w\s]+)[\s\-:]*([\d]{1,3})\s?%', resposta)

        if padrao_percentual:
            for label, valor in padrao_percentual:
                try:
                    valor_formatado = float(valor)
                    dados.append({"categoria": label.strip(), "valor": valor_formatado})
                except:
                    continue

            return {
                "grafico": "pizza",
                "titulo": "Distribuição percentual extraída",
                "dados": dados,
                "moeda": "%"
            }

        # 🔹 Padrão: Tabela (ex: janeiro: 1000, fevereiro: 1200)
        padrao_tabela = re.findall(r'([\wçãéó]+)\s*[:\-]\s*R?\$?\s?([\d\.,]+)', resposta)

        if padrao_tabela:
            for label, valor in padrao_tabela:
                try:
                    data = parser.parse(label + " 2024", fuzzy=True).strftime("%Y-%m")
                    valor_formatado = float(valor.replace('.', '').replace(',', '.'))
                    dados.append({"data": data, "valor": valor_formatado})
                except:
                    continue

            if dados:
                return {
                    "grafico": "linha",
                    "titulo": "Evolução mensal",
                    "dados": dados,
                    "moeda": "BRL"
                }

        return None
