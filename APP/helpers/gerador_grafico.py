import re
import json
from dateutil import parser
from dateutil.parser import ParserError # Importa a exceção específica
import logging
from typing import Optional, Dict, Any, List

# Configura o logging para este módulo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeradorEstruturaGrafico:
    def __init__(self):
        # Pré-compilação das expressões regulares para eficiência
        self.regex_percentual = re.compile(r'([\w\sãáéíóúç]+)[\s\-:]*([\d]{1,3}(?:\.\d{1,2})?)\s?%', re.IGNORECASE)
        # Permite datas como DD/MM/AAAA, DD-MM-AAAA, ou palavras seguidas de valor
        self.regex_temporal_data = re.compile(r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]?(\d{2,4})?|\b(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b)\s*[:\-\s]\s*R?\$?\s*([\d\.,]+)', re.IGNORECASE)
        # Mais genérico para Categoria: Valor
        self.regex_categoria_valor = re.compile(r'[\d\.\)]*\s*([\w\sãáéíóúç]+?)\s*[:=]\s*R?\$?\s?([\d\.,]+)', re.IGNORECASE)
        
        logging.info("GeradorEstruturaGrafico inicializado com padrões regex compilados.")


    def _parse_numeric_value(self, value_str: str) -> Optional[float]:
        """Converte uma string (ex: "1.234,56" ou "1,234.56") para float."""
        try:
            # Tenta com vírgula como separador decimal
            if ',' in value_str and '.' not in value_str:
                return float(value_str.replace('.', '').replace(',', '.'))
            # Tenta com ponto como separador decimal
            elif '.' in value_str and ',' not in value_str:
                return float(value_str)
            # Sem separadores ou com ambos, tenta de forma flexível
            else:
                return float(value_str.replace('.', '').replace(',', '.'))
        except ValueError:
            logging.warning(f"Não foi possível converter valor '{value_str}' para float.")
            return None

    def extrair_dados_de_resposta(self, resposta: str) -> Optional[Dict[str, Any]]:
        """
        Analisa a resposta textual da IA e tenta extrair dados estruturados para visualização gráfica.
        Prioriza padrões específicos sobre genéricos.
        """
        logging.info("Tentando extrair dados de gráfico da resposta.")
        
        # 1. Tentar extrair padrões percentuais (mais específicos)
        dados_percentuais = self._extrair_percentuais(resposta)
        if dados_percentuais:
            logging.info("Padrão percentual detectado.")
            return {
                "grafico": "pizza",
                "titulo": "Distribuição Percentual",
                "dados": dados_percentuais,
                "unidade": "%" # Renomeado para 'unidade' para ser mais genérico que 'moeda'
            }

        # 2. Tentar extrair padrões temporais com datas explícitas ou meses
        dados_temporais = self._extrair_temporal(resposta)
        if dados_temporais:
            logging.info("Padrão temporal detectado.")
            return {
                "grafico": "linha",
                "titulo": "Evolução Temporal",
                "dados": dados_temporais,
                "unidade": "BRL" # Assume BRL, pode ser ajustado
            }
            
        # 3. Tentar extrair padrões de categoria-valor genéricos
        dados_categoria_valor = self._extrair_categoria_valor(resposta)
        if dados_categoria_valor:
            logging.info("Padrão Categoria: Valor detectado.")
            return {
                "grafico": "barra" if len(dados_categoria_valor) > 4 else "pizza",
                "titulo": "Distribuição de Categorias",
                "dados": dados_categoria_valor,
                "unidade": "BRL" # Assume BRL, pode ser ajustado
            }
            
        logging.info("Nenhum padrão de gráfico reconhecido.")
        return None

    def _extrair_percentuais(self, resposta: str) -> List[Dict[str, Any]]:
        """Extrai dados no formato Categoria - XX%."""
        dados = []
        matches = self.regex_percentual.findall(resposta)
        for label, valor_str in matches:
            valor = self._parse_numeric_value(valor_str)
            if valor is not None:
                dados.append({"categoria": label.strip(), "valor": valor})
        return dados if dados else []

    def _extrair_temporal(self, resposta: str) -> List[Dict[str, Any]]:
        """Extrai dados no formato Data - Valor ou Mês: Valor."""
        dados = []
        matches = self.regex_temporal_data.findall(resposta)
        
        # Prioriza datas completas e depois nomes de meses
        for label_raw, _, valor_str in matches: # O segundo grupo de captura (ano) é ignorado aqui
            data_formatada = None
            
            # Tenta parser a label como uma data
            try:
                # dateutil.parser é inteligente o suficiente para entender "janeiro" ou "20/01/2023"
                parsed_date = parser.parse(label_raw, fuzzy=True, dayfirst=True)
                data_formatada = parsed_date.strftime("%Y-%m-%d") # Inclui dia para maior precisão
            except ParserError:
                # Se falhou, tenta adicionar um ano default para meses (Ex: "Janeiro")
                try:
                    # Tenta com o ano corrente se não conseguiu parsear a label
                    parsed_date = parser.parse(f"{label_raw} {parser.parse('now').year}", fuzzy=True, dayfirst=True)
                    data_formatada = parsed_date.strftime("%Y-%m-%d")
                except ParserError:
                    logging.debug(f"Não foi possível parsear a data/mês: '{label_raw}'")
                    continue # Pula para o próximo match

            valor = self._parse_numeric_value(valor_str)
            if data_formatada and valor is not None:
                dados.append({"data": data_formatada, "valor": valor})
                
        # Opcional: Ordenar dados temporais para garantir a ordem correta no gráfico de linha
        # Garante que as datas são comparáveis se armazenadas como strings YYYY-MM-DD
        return sorted(dados, key=lambda x: x['data']) if dados else []

    def _extrair_categoria_valor(self, resposta: str) -> List[Dict[str, Any]]:
        """Extrai dados no formato Categoria: Valor (o mais genérico)."""
        dados = []
        matches = self.regex_categoria_valor.findall(resposta)
        for label, valor_str in matches:
            # Ignorar labels que são cabeçalhos de seção
            if any(s in label.lower() for s in ["análise", "ações", "métricas", "objetivo", "plano"]):
                continue

            valor = self._parse_numeric_value(valor_str)
            if valor is not None:
                dados.append({"categoria": label.strip(), "valor": valor})
        return dados if dados else []