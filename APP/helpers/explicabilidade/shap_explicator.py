# APP/core/shap_explicator.py
import shap
import numpy as np

class ShapExplicator:
    def __init__(self, model_predict_fn, tokenizer=None, class_names=None):
        # model_predict_fn: A função predict (ou predict_proba) do seu mock_llm_for_explanation
        # tokenizer: O tokenizer do LLM, necessário para o masker de texto
        # class_names: Nomes das classes, para SHAP exibir corretamente
        self.model_predict_fn = model_predict_fn
        self.tokenizer = tokenizer
        self.class_names = class_names
        self.explainer = self._create_explainer()

    def _create_explainer(self):
        # Para explicar modelos de texto que recebem strings, o KernelExplainer com TextMasker é comum.
        # O masker precisa de um tokenizer ou uma função que tokenize e destokenize.
        if self.tokenizer:
            # Masker para texto: Substitui tokens aleatoriamente por um token de máscara
            # A função predict_fn do masker é o self.model_predict_fn
            masker = shap.maskers.Text(self.tokenizer, mask_token=self.tokenizer.mask_token if hasattr(self.tokenizer, 'mask_token') else self.tokenizer.unk_token)
            return shap.Explainer(self.model_predict_fn, masker, output_names=self.class_names)
        else:
            # Fallback ou erro se não houver tokenizer para text explainer
            # Para Llama.cpp sem tokenizer, isso é mais complexo, exigindo um masker customizado de string.
            # Por simplicidade, vamos assumir que o tokenizer é sempre fornecido para text explainers SHAP.
            raise ValueError("Tokenizer é necessário para inicializar ShapExplicator para explicação de texto.")

    def explicar(self, entrada_textual: str):
        # shap_values = self.explainer([entrada_textual]) espera uma lista de strings
        shap_values = self.explainer([entrada_textual])
        return shap_values