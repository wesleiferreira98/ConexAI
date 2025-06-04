# APP/services/topico_classificador.py
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import logging
# Importa a configuração centralizada
from APP.core.config import CONFIG 

class TopicoClassificador:
    def __init__(self):
        self.config = CONFIG.EMBEDDINGS_CONFIG # Acessa a parte relevante da configuração
        self.modelos_embedding = self._carregar_modelos_embedding()
        self.embeddings_referencia = self._carregar_embeddings_referencia()
        self.limiares_similaridade = self.config['limiares']
        
        # Definir as classes/tópicos que você quer classificar.
        # Exemplo: "fora de escopo", "sobre gestão"
        self.class_names = ["Fora_de_Escopo_Gestao", "Sobre_Gestao"]
        logging.info("✅ TopicoClassificador inicializado.")

    def _carregar_modelos_embedding(self) -> Dict[str, SentenceTransformer]:
        """Carrega os modelos de embedding."""
        logging.info("🔄 Carregando modelos de embedding para TopicoClassificador...")
        return {
            't5': SentenceTransformer(self.config['modelo_mpnet']),
            'mpnet': SentenceTransformer(self.config['modelo_mpnet']),
            'distil': SentenceTransformer(self.config['modelo_distil'])
        }

    def _carregar_embeddings_referencia(self) -> Dict[str, np.ndarray]:
        """Carrega os embeddings de referência pré-calculados."""
        logging.info("🔄 Carregando embeddings de referência para TopicoClassificador...")
        return {
            't5': np.load(self.config['embeddings_mpnet']).astype(np.float32),
            'mpnet': np.load(self.config['embeddings_mpnet']).astype(np.float32),
            'distil': np.load(self.config['embeddings_distil']).astype(np.float32)
        }

    def classificar_texto(self, texto: str) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Classifica um texto em termos de tópicos (ex: gestão vs. não gestão).
        Retorna as probabilidades [prob_nao_gestao, prob_gestao] e os scores de similaridade.
        """
        if not texto:
            return np.array([0.5, 0.5]), {'t5': 0.0, 'mpnet': 0.0, 'distil': 0.0} # Retorna neutro para texto vazio

        embeddings_texto = self._gerar_embeddings(texto)
        scores_similaridade = self._calcular_similaridades(embeddings_texto)

        # Usar uma lógica de agregação ou votação para obter uma probabilidade final.
        # Por simplicidade, vamos usar a média das similaridades relevantes e normalizá-la.
        # Uma abordagem mais robusta envolveria treinar um pequeno modelo (ex: logistic regression)
        # sobre esses scores para mapear para probabilidades de classe.
        
        # Exemplo simplificado: Pegar o score do modelo 'mpnet' como base
        base_score = scores_similaridade.get('mpnet', 0.0) 

        # Mapeamento linear/sigmoid simples para probabilidade:
        # Assumimos que scores mais altos indicam "Sobre_Gestao".
        # Ajuste esses valores para calibrar a probabilidade.
        # Ex: score 0.6 -> 0.5 prob, score 0.8 -> 0.9 prob
        prob_sobre_gestao = (base_score - 0.5) * 2 # Mapeia 0.5->0, 1.0->1
        prob_sobre_gestao = np.clip(prob_sobre_gestao, 0.0, 1.0) # Garante que está entre 0 e 1

        prob_fora_de_escopo = 1.0 - prob_sobre_gestao

        # Garantir que as probabilidades somam 1
        probs = np.array([prob_fora_de_escopo, prob_sobre_gestao])
        probs = probs / probs.sum() if probs.sum() > 0 else np.array([0.5, 0.5])

        return probs, scores_similaridade

    def _gerar_embeddings(self, texto: str) -> Dict[str, np.ndarray]:
        """Gera embeddings para um texto usando todos os modelos."""
        return {
            modelo: encoder.encode(texto, normalize_embeddings=True).astype(np.float32)
            for modelo, encoder in self.modelos_embedding.items()
        }

    def _calcular_similaridades(self, embeddings_texto: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Calcula similaridades com o dataset de referência para cada modelo."""
        return {
            modelo: float(np.max(self.embeddings_referencia[modelo] @ embedding.T))
            for modelo, embedding in embeddings_texto.items()
        }