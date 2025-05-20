import sqlite3
from datetime import datetime
import json

class ContextStorage:
    def __init__(self, db_path="contexto_chat2.db"):
        self.conn = sqlite3.connect(db_path)
        self._criar_tabelas()

    def _criar_tabelas(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL,
                    nome_chat TEXT NOT NULL,
                    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS historico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    pergunta TEXT NOT NULL,
                    resposta TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    data TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
                )
            """)

    def criar_chat(self, usuario, nome_chat):
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO chats (usuario, nome_chat) VALUES (?, ?)",
                (usuario, nome_chat)
            )
            return cursor.lastrowid

    def listar_chats(self, usuario):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nome_chat, data_criacao FROM chats WHERE usuario = ? ORDER BY data_criacao DESC",
            (usuario,)
        )
        return cursor.fetchall()

    def adicionar_interacao(self, chat_id, pergunta, resposta, modelo):
        with self.conn:
            self.conn.execute(
                "INSERT INTO historico (chat_id, pergunta, resposta, modelo) VALUES (?, ?, ?, ?)",
                (chat_id, pergunta, resposta, modelo)
            )

    def listar_interacoes(self, usuario):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT h.chat_id, c.nome_chat, h.pergunta, h.resposta, h.data FROM historico h JOIN chats c ON h.chat_id = c.id WHERE c.usuario = ? ORDER BY h.data DESC",
            (usuario,)
        )
        interacoes = []
        for row in cursor.fetchall():
            interacoes.append({
                "chat_id": row[0],
                "nome_chat": row[1],
                "pergunta": row[2],
                "resposta": json.loads(row[3]),  # Desserializa JSON
                "data": row[4]
            })
        return interacoes

    def registrar_interacao(self, chat_id, interacao):
        with self.conn:
            self.conn.execute(
                "INSERT INTO historico (chat_id, pergunta, resposta, modelo, data) VALUES (?, ?, ?, ?, ?)",
                (
                    chat_id,
                    interacao['pergunta'],
                    json.dumps(interacao['resposta']),  # Serializa para JSON
                    interacao['modelo'],
                    interacao['data']
                )
            )

    def recuperar_contexto(self, chat_id, limite=3):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT pergunta, resposta FROM historico WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
            (chat_id, limite)
        )
        return cursor.fetchall()[::-1]  # ordem cronológica

    def limpar_contexto(self, chat_id):
        with self.conn:
            self.conn.execute(
                "DELETE FROM historico WHERE chat_id = ?",
                (chat_id,)
            )
