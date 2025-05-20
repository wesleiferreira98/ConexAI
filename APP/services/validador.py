import re
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from typing import Tuple, Dict
from APP.core.constantes import CONFIG
class ValidadorPergunta:
    def __init__(self, config: dict):
        self.config = config
        self.modelos = self._carregar_modelos()
        self.embeddings = self._carregar_embeddings()
        self._compilar_regex()
        logging.basicConfig(level=logging.INFO)

    def _carregar_modelos(self) -> dict:
        print ("Carrega os modelos de embedding")
        return {
            't5': SentenceTransformer(CONFIG['modelo_mpnet']),
            'mpnet': SentenceTransformer(CONFIG['modelo_mpnet']),
            'distil': SentenceTransformer(CONFIG['modelo_distil'])
        }

    def _carregar_embeddings(self) -> dict:
        print("Carrega os embeddings pré-calculados")
        return {
            't5': np.load(CONFIG['embeddings_mpnet']).astype(np.float32),
            'mpnet': np.load(CONFIG['embeddings_mpnet']).astype(np.float32),
            'distil': np.load(CONFIG['embeddings_distil']).astype(np.float32)
        }

    def _compilar_regex(self):
        """Pré-compila expressões regulares para filtro léxico"""
        self.regex_termos = [
            re.compile(padrao, re.IGNORECASE) 
            for padrao in CONFIG['termos_bloqueio']
        ]

    def validar_pergunta(self, pergunta: str) -> Tuple[bool, Dict]:
        """Fluxo completo de validação"""
        try:
            # Etapa 1: Filtro léxico
            if not self._filtrar_termos_tecnicos(pergunta):
                return False, {'motivo': 'Termos técnicos detectados'}

            # Etapa 2: Validação semântica
            resultado = self._validar_semantica(pergunta)
            
            # Etapa 3: Validação contextual se necessário
            if resultado['precisa_validar_llm']:
                if not self._validar_contexto(pergunta):
                    return False, {'motivo': 'Fora do escopo contextual'}
            
            return resultado['valido'], resultado
        
        except Exception as e:
            logging.error(f"Erro na validação: {str(e)}")
            return False, {'erro': str(e)}

    def _filtrar_termos_tecnicos(self, pergunta: str) -> bool:
        """Aplica filtro léxico"""
        return not any(
            padrao.search(pergunta) 
            for padrao in self.regex_termos
        )

    def _validar_semantica(self, pergunta: str) -> Dict:
        """Executa sistema de votação com embeddings"""
        embeddings = self._gerar_embeddings(pergunta)
        scores = self._calcular_similaridades(embeddings)
        
        return {
            'valido': self._verificar_votos(scores),
            'scores': scores,
            'precisa_validar_llm': self._deve_validar_com_llm(scores)
        }

    def _gerar_embeddings(self, pergunta: str) -> Dict:
        """Gera embeddings para todos os modelos"""
        return {
            modelo: encoder.encode(
                pergunta, 
                normalize_embeddings=True
            ).astype(np.float32)
            for modelo, encoder in self.modelos.items()
        }

    def _calcular_similaridades(self, embeddings: Dict) -> Dict:
        """Calcula similaridades com dataset de referência"""
        return {
            modelo: np.max(self.embeddings[modelo] @ embedding.T)
            for modelo, embedding in embeddings.items()
        }

    def _verificar_votos(self, scores: Dict) -> bool:
        """Verifica votação dos modelos"""
        votos = sum(
            score >= CONFIG['limiares'][modelo]
            for modelo, score in scores.items()
        )
        return votos >= 2

    def _deve_validar_com_llm(self, scores: Dict) -> bool:
        """Determina se precisa de validação contextual"""
        return any(
            CONFIG['limiar_llm'] < score < CONFIG['limiares'][modelo]
            for modelo, score in scores.items()
        )

    def _validar_contexto(self, pergunta: str) -> bool:
        """Validação final com LLM (simulado)"""
        # Implementação real usaria API de LLM
        termos_chave = ['gestão', 'estrategia', 'financeiro', 'RH']
        return any(
            termo in pergunta.lower() 
            for termo in termos_chave
        )