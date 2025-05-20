import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import text 
from APP.helpers.gerador_grafico import GeradorEstruturaGrafico

class RelatorioGenerator:
    def __init__(self, db_url="sqlite:///contexto_chat.db"):
        self.engine = create_engine(db_url)
        self.kpi_aliases = {
            "faturamento": ["faturamento", "receita", "lucros"],
            "clientes ativos": ["ativos", "clientes em operação"],
            "inadimplência": ["inadimplência", "inadimplentes", "atraso"]
        }
        self.gerador_grafico = GeradorEstruturaGrafico()
        self._criar_tabelas_teste()

    def _criar_tabelas_teste(self):
        with self.engine.connect() as conn:
            # Criação das tabelas com text()
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS Unidades_Negocio (
                    id_unidade INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL
                );
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS KPIs (
                    id_kpi INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL
                );
            '''))
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS Registros (
                    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_kpi INTEGER NOT NULL,
                    id_unidade INTEGER NOT NULL,
                    valor REAL NOT NULL,
                    data_coleta TEXT NOT NULL,
                    FOREIGN KEY (id_kpi) REFERENCES KPIs(id_kpi),
                    FOREIGN KEY (id_unidade) REFERENCES Unidades_Negocio(id_unidade)
                );
            '''))
            
            # Inserção de dados de teste corrigida
            conn.execute(text('''
                INSERT INTO Unidades_Negocio (nome) VALUES 
                ('Unidade A'), ('Unidade B'), ('Unidade C')
            '''))
            
            conn.execute(text('''
                INSERT INTO KPIs (nome) VALUES 
                ('Faturamento'), ('Clientes Ativos'), ('Inadimplência')
            '''))
            
            conn.execute(text('''
                INSERT INTO Registros (id_kpi, id_unidade, valor, data_coleta) VALUES
                (1, 1, 1000.0, '2024-01-01'),
                (1, 2, 1500.0, '2024-02-01'),
                (1, 3, 2000.0, '2024-03-01'),
                (2, 1, 300.0, '2024-01-01'),
                (2, 2, 450.0, '2024-02-01'),
                (3, 1, 100.0, '2024-01-01'),
                (3, 2, 200.0, '2024-02-01')
            '''))
            conn.commit()  # Adicione commit para garantir a persistência
    def _mapear_tipo_kpi(self, tipo):
        tipo = tipo.lower()
        for chave, sinonimos in self.kpi_aliases.items():
            if any(s in tipo for s in sinonimos):
                return chave
        return tipo

    def _normalizar_periodo(self, inicio, fim):
        try:
            data_inicio = pd.to_datetime(inicio, dayfirst=True)
            data_fim = pd.to_datetime(fim, dayfirst=True)
        except Exception:
            hoje = pd.Timestamp.today()
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
        return data_inicio.strftime("%Y-%m-%d"), data_fim.strftime("%Y-%m-%d")

    def gerar_relatorio(self, tipo, formato="xlsx", periodo=("2024-01-01", "2024-12-31"), usuario="anonimo", chat_id=None):
        tipo_kpi = self._mapear_tipo_kpi(tipo)
        inicio, fim = self._normalizar_periodo(*periodo)

        query = f"""
            SELECT u.nome AS unidade, k.nome AS kpi, r.valor, r.data_coleta
            FROM Registros r
            JOIN KPIs k ON k.id_kpi = r.id_kpi
            JOIN Unidades_Negocio u ON u.id_unidade = r.id_unidade
            WHERE LOWER(k.nome) LIKE '%{tipo_kpi}%' AND r.data_coleta BETWEEN '{inicio}' AND '{fim}'
        """

        df = pd.read_sql(query, self.engine)

        if df.empty:
            return {"erro": "Nenhum dado encontrado."}

        df["data_coleta"] = pd.to_datetime(df["data_coleta"])
        df = df.sort_values("data_coleta")

        resumo = df.groupby("unidade")["valor"].describe().round(2).reset_index()

        # Integração com o gerador de gráficos
        texto_resumo = "\n".join([f"{row['unidade']}: R$ {row['mean']:.2f}" for _, row in resumo.iterrows()])
        estrutura_grafico = self.gerador_grafico.extrair_dados_de_resposta(texto_resumo)

        if not estrutura_grafico:
            estrutura_grafico = {
                "grafico": "linha" if df["data_coleta"].nunique() > 1 else "barra",
                "titulo": f"Distribuição de {tipo_kpi.capitalize()}",
                "dados": [{"data": row["data_coleta"].strftime("%Y-%m-%d"), "valor": row["valor"]} for _, row in df.iterrows()],
                "moeda": "BRL"
            }

        if chat_id:
            log_df = pd.DataFrame({
                "usuario": [usuario],
                "chat_id": [chat_id],
                "tipo_kpi": [tipo_kpi],
                "data_geracao": [datetime.now()],
                "periodo_inicio": [inicio],
                "periodo_fim": [fim],
                "linhas": [len(df)]
            })
            try:
                log_df.to_sql("relatorios_log", self.engine, index=False, if_exists="append")
            except Exception as e:
                print(f"Erro ao registrar log de relatório: {e}")

        nome_arquivo = f"relatorio_{tipo_kpi.replace(' ', '_')}_{inicio}_a_{fim}.{formato}"
        caminho_saida = os.path.join("./relatorios", nome_arquivo)
        os.makedirs("./relatorios", exist_ok=True)

        if formato == "xlsx":
            with pd.ExcelWriter(caminho_saida) as writer:
                df.to_excel(writer, index=False, sheet_name="dados")
                resumo.to_excel(writer, index=False, sheet_name="resumo")
        elif formato == "csv":
            df.to_csv(caminho_saida, index=False)
        elif formato == "json":
            df.to_json(caminho_saida, orient="records")

        return {
            "arquivo": caminho_saida,
            "tipo_kpi": tipo_kpi,
            "tipo_grafico": estrutura_grafico["grafico"],
            "linhas": len(df),
            "colunas": list(df.columns),
            "resumo_estatistico": resumo.to_dict(orient="records"),
            "periodo": (inicio, fim),
            "grafico": estrutura_grafico
        }