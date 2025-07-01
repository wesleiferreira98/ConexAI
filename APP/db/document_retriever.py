import faiss # type: ignore
import json
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class DocumentRetriever:
    def __init__(self, index_path: str, chunk_info_path: str, model_name: str):
        logging.info("Iniciando o DocumentRetriever...")
        self.index_path = index_path
        self.chunk_info_path = chunk_info_path
        self.model_name = model_name
        
        try:
            logging.info(f"Carregando o índice FAISS de '{self.index_path}'...")
            self.index = faiss.read_index(self.index_path)
            
            logging.info(f"Carregando informações dos chunks de '{self.chunk_info_path}'...")
            with open(self.chunk_info_path, 'r', encoding='utf-8') as f:
                self.chunk_info = json.load(f)
            
            logging.info(f"Carregando o modelo de embedding '{self.model_name}'...")
            self.model = SentenceTransformer(self.model_name)
            
            logging.info("✅ DocumentRetriever carregado com sucesso.")
        except Exception as e:
            logging.error(f"Falha ao inicializar o DocumentRetriever: {e}", exc_info=True)
            raise

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """
        Busca os k chunks mais relevantes para uma dada consulta (query).
        """
        logging.info(f"Buscando documentos relevantes para a consulta: '{query[:50]}...'")
        
        # 1. Converte a consulta em um vetor
        query_embedding = self.model.encode([query])
        
        # 2. Busca no índice FAISS
        # D: distâncias, I: índices dos vetores no arquivo .bin
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        # 3. Recupera os chunks de texto correspondentes
        results = []
        for i in indices[0]:
            # Garante que o índice é válido
            if i < len(self.chunk_info):
                results.append(self.chunk_info[i])
        
        logging.info(f"Encontrados {len(results)} chunks relevantes.")
        return results