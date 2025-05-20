import lime
import lime.lime_tabular
import numpy as np

class LimeExplicator:
    def __init__(self, model, feature_names=None, class_names=None):
        self.model = model
        self.feature_names = feature_names
        self.class_names = class_names
        self.explainer = None

    def explicar(self, entrada, num_features=5):
        if self.explainer is None:
            self.explainer = lime.lime_tabular.LimeTabularExplainer(
                training_data=np.array(entrada),
                feature_names=self.feature_names,
                class_names=self.class_names,
                mode="classification"
            )
        exp = self.explainer.explain_instance(np.array(entrada[0]), self.model.predict_proba, num_features=num_features)
        return exp.as_list()
