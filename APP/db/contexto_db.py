#import aiosqlite # type: ignore
from datetime import datetime
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from APP.schemas.perfil_schema import PerfilUsuarioSchema, ConfiguracoesSchema
import aiosqlite  # type: ignore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ContextStorage:
    def __init__(self, db_path: str = "contexto_chat2.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        logging.info(f"ContextStorage inicializado para DB: {self.db_path}")

    async def connect(self):
        """Abre a conexão com o banco de dados (assíncrono)."""
        if self._conn is None:
            # Use aiosqlite.connect para uma conexão assíncrona e thread-safe.
            # check_same_thread=False é para permitir o uso da conexão em diferentes threads/tasks
            # em cenários avançados (como pools de conexão), mas aiosqlite já lida bem com isso.
            self._conn = await aiosqlite.connect(self.db_path, check_same_thread=False)
            logging.info(f"Conexão com o DB '{self.db_path}' aberta.")
            await self._criar_tabelas()
        
    async def close(self):
        """Fecha a conexão com o banco de dados (assíncrono)."""
        if self._conn:
            await self._conn.close()
            self._conn = None
            logging.info(f"Conexão com o DB '{self.db_path}' fechada.")

    async def _criar_tabelas(self):
        """Cria as tabelas se não existirem."""
        async with self._conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL,
                    nome_chat TEXT NOT NULL,
                    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS perfis_usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE, -- O mesmo 'usuario' da tabela 'chats'
                    preferencias TEXT,             -- Armazenaremos uma lista como JSON
                    configuracoes TEXT,            -- Armazenaremos um objeto como JSON
                    data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Tabela historico atualizada para armazenar todos os novos campos
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    pergunta TEXT NOT NULL,
                    resposta_llm_bruta TEXT NOT NULL, -- Resposta bruta do LLM
                    valido INTEGER NOT NULL,           -- Booleano (0 ou 1)
                    detalhes_validacao TEXT,           -- JSON string para Dict
                    explicacao_lime TEXT,              -- String
                    explicacao_shap TEXT,              -- String
                    dados_grafico TEXT,                -- JSON string para Dict
                    modelo TEXT NOT NULL,
                    data TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
                )
            """)
            await self._conn.commit() # Commita as alterações de esquema
        logging.info("Tabelas do DB verificadas/criadas.")

    async def criar_chat(self, usuario: str, nome_chat: str) -> int:
        """Cria um novo chat e retorna seu ID."""
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO chats (usuario, nome_chat) VALUES (?, ?)",
                (usuario, nome_chat)
            )
            await self._conn.commit()
            chat_id = cursor.lastrowid
            logging.info(f"Chat '{nome_chat}' criado para '{usuario}' com ID: {chat_id}")
            return chat_id

    async def listar_chats(self, usuario: str, skip: int = 0, limit: int = 100) -> List[Tuple[int, str, str]]:
        """
        Lista os chats de um usuário com suporte a paginação.
        Args:
            usuario (str): Nome do usuário.
            skip (int): Número de itens a pular (offset).
            limit (int): Número máximo de itens a retornar (page size).
        """
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, nome_chat, data_criacao FROM chats WHERE usuario = ? ORDER BY data_criacao DESC LIMIT ? OFFSET ?",
                (usuario, limit, skip)
            )
            chats = await cursor.fetchall()
            logging.info(f"Chats listados para '{usuario}' (skip={skip}, limit={limit}): {len(chats)} encontrados.")
            return chats


    async def registrar_interacao(self, chat_id: int, interacao: Dict[str, Any]):
        """
        Registra uma interação completa do chat.
        `interacao` deve ser um dicionário com todos os campos necessários.
        """
        try:
            # Serializa campos complexos para JSON
            detalhes_validacao_json = json.dumps(interacao.get('detalhes_validacao'))
            dados_grafico_json = json.dumps(interacao.get('dados_grafico'))
            
            async with self._conn.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO historico (
                        chat_id, pergunta, resposta_llm_bruta, valido, detalhes_validacao, 
                        explicacao_lime, explicacao_shap, dados_grafico, modelo, data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chat_id,
                        interacao['pergunta'],
                        interacao['resposta_raw'], # Armazena a resposta bruta
                        1 if interacao['valido'] else 0, # SQLite armazena booleanos como 0/1
                        detalhes_validacao_json,
                        interacao.get('explicacao_lime'),
                        interacao.get('explicacao_shap'),
                        dados_grafico_json,
                        interacao['modelo'],
                        interacao['data']
                    )
                )
                await self._conn.commit()
            logging.info(f"Interação registrada no chat {chat_id}.")
        except Exception as e:
            logging.error(f"Erro ao registrar interação no chat {chat_id}: {e}", exc_info=True)
            raise # Re-lança para que o erro seja tratado na camada superior

    async def listar_interacoes(self, usuario: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lista todas as interações detalhadas de um usuário com suporte a paginação.
        Args:
            usuario (str): Nome do usuário.
            skip (int): Número de itens a pular (offset).
            limit (int): Número máximo de itens a retornar (page size).
        """
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT 
                    h.chat_id, c.nome_chat, h.pergunta, h.resposta_llm_bruta, 
                    h.valido, h.detalhes_validacao, h.explicacao_lime, 
                    h.explicacao_shap, h.dados_grafico, h.modelo, h.data
                FROM historico h 
                JOIN chats c ON h.chat_id = c.id 
                WHERE c.usuario = ? 
                ORDER BY h.data DESC
                LIMIT ? OFFSET ?
                """,
                (usuario, limit, skip)
            )
            rows = await cursor.fetchall()
        
        interacoes = []
        for row in rows:
            # Desserializa os campos JSON
            detalhes_validacao = json.loads(row[5]) if row[5] else None
            dados_grafico = json.loads(row[8]) if row[8] else None

            interacoes.append({
                "chat_id": row[0],
                "nome_chat": row[1],
                "pergunta": row[2],
                "resposta_llm_bruta": row[3],
                "valido": bool(row[4]), # Converte 0/1 para booleano
                "detalhes_validacao": detalhes_validacao,
                "explicacao_lime": row[6],
                "explicacao_shap": row[7],
                "dados_grafico": dados_grafico,
                "modelo": row[9],
                "data": row[10]
            })
        logging.info(f"Interações listadas para '{usuario}' (skip={skip}, limit={limit}): {len(interacoes)} encontradas.")
        return interacoes

    async def recuperar_contexto(self, chat_id: int, limite: int = 3) -> List[Dict[str, str]]:
        """
        Recupera o contexto (pergunta e resposta bruta) de um chat.
        Retorna uma lista de dicionários no formato [{"pergunta": "", "resposta": ""}]
        """
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "SELECT pergunta, resposta_llm_bruta FROM historico WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (chat_id, limite)
            )
            # Reverte a ordem para cronológica, e formata para [{"pergunta": "", "resposta": ""}]
            contexto = [{"pergunta": row[0], "resposta": row[1]} for row in (await cursor.fetchall())[::-1]]
            logging.info(f"Contexto recuperado para chat {chat_id}: {len(contexto)} interações.")
            return contexto

    async def limpar_contexto(self, chat_id: int):
        """Limpa todo o histórico de um chat específico."""
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                "DELETE FROM historico WHERE chat_id = ?",
                (chat_id,)
            )
            await self._conn.commit()
        logging.info(f"Histórico limpo para chat {chat_id}.")


    async def contar_total_chats_usuario(self, usuario: str) -> int:
            """Conta o total de chats para um usuário."""
            async with self._conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT COUNT(id) FROM chats WHERE usuario = ?",
                    (usuario,)
                )
                total = (await cursor.fetchone())[0]
                return total if total is not None else 0
            
    async def contar_total_interacoes_usuario(self, usuario: str) -> int:
        """Conta o total de interações para um usuário."""
        async with self._conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT COUNT(h.id) FROM historico h JOIN chats c ON h.chat_id = c.id WHERE c.usuario = ?
                """,
                (usuario,)
            )
            total = (await cursor.fetchone())[0]
            return total if total is not None else 0
    
    

    async def atualizar_perfil(self, perfil_data: PerfilUsuarioSchema):
        """
        Cria ou atualiza o perfil de um usuário na tabela perfis_usuarios.
        Utiliza a sintaxe 'INSERT ... ON CONFLICT' (UPSERT) para simplificar a lógica.

        Args:
            perfil_data: Um objeto PerfilUsuarioSchema com os dados a serem salvos.
        """
        # Serializa os campos complexos para strings JSON
        preferencias_json = json.dumps(perfil_data.preferencias)
        # Usa o método .dict() do Pydantic para converter o sub-modelo em um dicionário
        configuracoes_json = json.dumps(perfil_data.configuracoes.dict())
        
        sql = """
            INSERT INTO perfis_usuarios (usuario, preferencias, configuracoes, data_atualizacao)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(usuario) DO UPDATE SET
                preferencias = excluded.preferencias,
                configuracoes = excluded.configuracoes,
                data_atualizacao = excluded.data_atualizacao;
        """
        
        try:
            await self.connect() # Garante que a conexão está ativa
            async with self._conn.cursor() as cursor:
                await cursor.execute(
                    sql,
                    (
                        perfil_data.id_usuario,
                        preferencias_json,
                        configuracoes_json,
                        datetime.now().isoformat()
                    )
                )
                await self._conn.commit()
            logging.info(f"Perfil do usuário '{perfil_data.id_usuario}' atualizado com sucesso.")
        except Exception as e:
            logging.error(f"Falha ao atualizar o perfil do usuário '{perfil_data.id_usuario}': {e}", exc_info=True)
            # Você pode querer propagar o erro dependendo da sua estratégia de tratamento
            raise

    async def obter_perfil_completo(self, usuario: str, chat_id: Optional[int] = None, limite_historico: int = 3) -> PerfilUsuarioSchema:
        """
        Monta o perfil completo de um usuário, combinando dados da tabela
        'perfis_usuarios' (preferências/configurações) e 'historico' (interações recentes).

        Args:
            usuario: O ID do usuário para buscar o perfil.
            chat_id: O ID do chat atual para buscar o histórico relevante.
            limite_historico: O número de interações recentes a serem incluídas.

        Returns:
            Um objeto PerfilUsuarioSchema preenchido com todos os dados do usuário.
        """
        await self.connect() # Garante que a conexão está ativa
        
        # Valores padrão caso o perfil não exista
        preferencias = []
        configuracoes = ConfiguracoesSchema() # Pydantic nos dá um objeto com os padrões

        # 1. Busca as preferências e configurações na tabela de perfis
        try:
            async with self._conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT preferencias, configuracoes FROM perfis_usuarios WHERE usuario = ?",
                    (usuario,)
                )
                row = await cursor.fetchone()

            if row:
                # Desserializa os dados do banco de dados
                preferencias = json.loads(row[0]) if row[0] else []
                config_dict = json.loads(row[1]) if row[1] else {}
                configuracoes = ConfiguracoesSchema(**config_dict)
                logging.info(f"Preferências e configurações carregadas para o usuário '{usuario}'.")
            else:
                logging.info(f"Nenhum perfil encontrado para '{usuario}'. Usando valores padrão.")

        except Exception as e:
            logging.error(f"Erro ao buscar perfil de '{usuario}': {e}. Usando valores padrão.", exc_info=True)

        # 2. Busca o histórico de interações (reutilizando seu método existente)
        historico = []
        if chat_id:
            try:
                # Seu método já retorna o histórico no formato [{"pergunta": "", "resposta": ""}]
                historico = await self.recuperar_contexto(chat_id, limite=limite_historico)
                logging.info(f"Histórico de interações carregado para o chat '{chat_id}'.")
            except Exception as e:
                logging.error(f"Erro ao recuperar contexto para o chat '{chat_id}': {e}", exc_info=True)

        # 3. Monta e retorna o objeto de perfil completo
        perfil_final = PerfilUsuarioSchema(
            id_usuario=usuario,
            preferencias=preferencias,
            configuracoes=configuracoes,
            historico_interacoes=historico  # O schema espera uma lista, mas seu método retorna o formato correto
        )
        return perfil_final