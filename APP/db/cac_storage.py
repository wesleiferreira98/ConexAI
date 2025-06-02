# APP/db/cac_storage.py (Novo arquivo)
import aiosqlite # type: ignore
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CacStorage:
    def __init__(self, db_path: str = "cac_reports.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        logging.info(f"CacStorage inicializado para DB: {self.db_path}")

    async def connect(self):
        """Abre a conexão com o banco de dados (assíncrono)."""
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.db_path, check_same_thread=False)
            logging.info(f"Conexão com o DB '{self.db_path}' aberta para CAC.")
            await self._criar_tabelas()
        
    async def close(self):
        """Fecha a conexão com o banco de dados (assíncrono)."""
        if self._conn:
            await self._conn.close()
            self._conn = None
            logging.info(f"Conexão com o DB '{self.db_path}' fechada para CAC.")

    async def _criar_tabelas(self):
        """Cria as tabelas `despesas` e `clientes` se não existirem."""
        async with self._conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data_competencia TEXT NOT NULL,
                    data_criacao TEXT NOT NULL,
                    eh_fixa INTEGER NOT NULL DEFAULT 0,
                    considerar_no_cac INTEGER NOT NULL DEFAULT 0,
                    percentual_cac REAL NOT NULL DEFAULT 100.0
                )
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data_cadastro TEXT NOT NULL,
                    data_primeira_venda_pagante TEXT NULL
                )
            """)
            await self._conn.commit()
        logging.info("Tabelas de CAC verificadas/criadas.")

    # --- Funções para Gerenciar Despesas ---

    async def adicionar_despesa(self, descricao: str, valor: float, data_competencia: str, data_criacao: str, eh_fixa: bool = False, considerar_no_cac: bool = False, percentual_cac: float = 100.0) -> int:
        """Adiciona uma nova despesa."""
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO despesas (descricao, valor, data_competencia, data_criacao, eh_fixa, considerar_no_cac, percentual_cac)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (descricao, valor, data_competencia, data_criacao, int(eh_fixa), int(considerar_no_cac), percentual_cac)
            )
            await self._conn.commit()
            despesa_id = cursor.lastrowid
            logging.info(f"Despesa '{descricao}' (ID: {despesa_id}) adicionada.")
            return despesa_id

    async def atualizar_despesa_cac_flag(self, despesa_id: int, considerar_no_cac: bool, percentual_cac: float = 100.0):
        """Atualiza a flag 'considerar_no_cac' e 'percentual_cac' de uma despesa."""
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE despesas SET considerar_no_cac = ?, percentual_cac = ? WHERE id = ?",
                (int(considerar_no_cac), percentual_cac, despesa_id)
            )
            await self._conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Despesa ID {despesa_id} atualizada para CAC: {considerar_no_cac}.")
            else:
                logging.warning(f"Despesa ID {despesa_id} não encontrada para atualização.")

    async def atualizar_despesas_em_lote_cac_flag(self, despesa_ids: List[int], considerar_no_cac: bool, percentual_cac: float = 100.0):
        """Atualiza a flag CAC para múltiplas despesas em lote."""
        if not despesa_ids:
            return
        placeholders = ','.join('?' * len(despesa_ids))
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                f"UPDATE despesas SET considerar_no_cac = ?, percentual_cac = ? WHERE id IN ({placeholders})",
                (int(considerar_no_cac), percentual_cac, *despesa_ids)
            )
            await self._conn.commit()
            logging.info(f"{cursor.rowcount} despesas atualizadas em lote para CAC.")

    # --- Funções para Gerenciar Clientes ---

    async def adicionar_cliente(self, nome: str, data_cadastro: str) -> int:
        """Adiciona um novo cliente."""
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO clientes (nome, data_cadastro) VALUES (?, ?)",
                (nome, data_cadastro)
            )
            await self._conn.commit()
            cliente_id = cursor.lastrowid
            logging.info(f"Cliente '{nome}' (ID: {cliente_id}) adicionado.")
            return cliente_id

    async def registrar_primeira_venda_pagante_cliente(self, cliente_id: int, data_venda: str):
        """
        Registra a data da primeira venda pagante de um cliente.
        Esta função deve ser chamada quando uma venda para este cliente
        (com valor > 0 e status 'pago') for identificada como a primeira.
        Deve-se garantir que data_venda seja anterior ou igual à data_primeira_venda_pagante já existente,
        ou se não existir, preenchê-la.
        """
        async with self._conn.cursor() as cursor:
            # Recupera a data_primeira_venda_pagante atual para comparar
            await cursor.execute("SELECT data_primeira_venda_pagante FROM clientes WHERE id = ?", (cliente_id,))
            current_first_sale_date_raw = await cursor.fetchone()
            current_first_sale_date = current_first_sale_date_raw[0] if current_first_sale_date_raw else None

            should_update = False
            if current_first_sale_date is None:
                should_update = True
            elif data_venda < current_first_sale_date: # A nova data é anterior à registrada
                should_update = True
            
            if should_update:
                await cursor.execute(
                    "UPDATE clientes SET data_primeira_venda_pagante = ? WHERE id = ?",
                    (data_venda, cliente_id)
                )
                await self._conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Cliente ID {cliente_id}: data da primeira venda pagante atualizada para {data_venda}.")
                else:
                    logging.warning(f"Cliente ID {cliente_id} não encontrado para registrar primeira venda pagante.")
            else:
                logging.debug(f"Cliente ID {cliente_id}: data da primeira venda pagante ({current_first_sale_date}) já é anterior ou igual a {data_venda}.")


    # --- Funções para Relatórios ---

    async def calcular_total_despesas_cac_mensal(self, ano_mes: str) -> float:
        """
        Calcula o total das despesas consideradas no CAC para um dado mês (YYYY-MM).
        Usa data_competencia, com fallback para data_criacao.
        """
        async with self._conn.cursor() as cursor:
            # Coalesce: usa data_competencia se não for nula, senão usa data_criacao
            await cursor.execute(
                """
                SELECT SUM(d.valor * (d.percentual_cac / 100.0))
                FROM despesas d
                WHERE d.considerar_no_cac = 1
                  AND SUBSTR(COALESCE(d.data_competencia, d.data_criacao), 1, 7) = ?
                """,
                (ano_mes,)
            )
            total = (await cursor.fetchone())[0]
            logging.info(f"Total de despesas CAC para {ano_mes}: {total or 0.0:.2f}.")
            return total if total is not None else 0.0

    async def contar_novos_clientes_mensal(self, ano_mes: str) -> int:
        """
        Conta o número de novos clientes pagantes para um dado mês (YYYY-MM).
        Considera a data da primeira venda pagante.
        """
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT COUNT(id)
                FROM clientes
                WHERE SUBSTR(data_primeira_venda_pagante, 1, 7) = ?
                """,
                (ano_mes,)
            )
            count = (await cursor.fetchone())[0]
            logging.info(f"Novos clientes pagantes para {ano_mes}: {count or 0}.")
            return count if count is not None else 0

    async def calcular_cac_mensal(self, ano_mes: str) -> float:
        """
        Calcula o CAC para um dado mês (YYYY-MM).
        Retorna 0 se não houver novos clientes.
        """
        total_despesas = await self.calcular_total_despesas_cac_mensal(ano_mes)
        num_novos_clientes = await self.contar_novos_clientes_mensal(ano_mes)

        if num_novos_clientes == 0:
            logging.info(f"CAC para {ano_mes}: 0.0 (nenhum novo cliente).")
            return 0.0
        
        cac = total_despesas / num_novos_clientes
        logging.info(f"CAC para {ano_mes}: {cac:.2f}.")
        return cac