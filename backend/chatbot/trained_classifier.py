"""
Clasificador de intención entrenado con sklearn
Usa el modelo entrenado localmente para mayor precisión
"""

import pickle
from pathlib import Path


class TrainedIntentClassifier:
    """Clasificador de intención usando modelo entrenado"""
    
    def __init__(self):
        """Carga el modelo entrenado"""
        self.model = None
        self._cargar_modelo()
    
    def _cargar_modelo(self):
        """Intenta cargar el modelo pre-entrenado"""
        model_path = Path(__file__).parent / "training_data" / "intent_classifier_model.pkl"
        
        if model_path.exists():
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print("✓ Modelo de intención cargado correctamente")
            except Exception as e:
                print(f"⚠ Error cargando modelo: {e}")
                self.model = None
        else:
            print(f"⚠ Modelo no encontrado en: {model_path}")
            self.model = None
    
    def clasificar(self, texto):
        """
        Clasifica la intención del texto
        
        Args:
            texto (str): Mensaje del usuario
            
        Returns:
            str: Tipo de intención (pedido, saludo, queja, etc.)
        """
        if not self.model or not texto:
            return None
        
        try:
            prediccion = self.model.predict([texto])[0]
            return prediccion
        except Exception as e:
            print(f"Error en clasificación: {e}")
            return None
    
    def obtener_probabilidades(self, texto):
        """
        Obtiene las probabilidades de cada intención
        
        Returns:
            dict: {intencion: probabilidad}
        """
        if not self.model or not texto:
            return {}
        
        try:
            clases = self.model.classes_
            probabilidades = self.model.predict_proba([texto])[0]
            
            return {
                clase: float(prob) 
                for clase, prob in zip(clases, probabilidades)
            }
        except Exception as e:
            print(f"Error obteniendo probabilidades: {e}")
            return {}
    
    def esta_disponible(self):
        """Verifica si el modelo está cargado"""
        return self.model is not None
