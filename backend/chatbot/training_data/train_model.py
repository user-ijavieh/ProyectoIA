"""
Script de entrenamiento para el clasificador de pedidos
Usa el dataset de ejemplos para fine-tuning de un modelo DistilBERT

Requisitos adicionales:
    pip install datasets scikit-learn

Uso:
    python train_model.py
"""

import json
import os
from pathlib import Path


def cargar_dataset():
    """Carga el dataset de entrenamiento BALANCEADO"""
    dataset_path = Path(__file__).parent / "pedidos_dataset_balanced.json"
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"No se encontró el dataset: {dataset_path}")
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def preparar_datos_intencion(data):
    """Prepara datos para clasificación de intención"""
    ejemplos = data['ejemplos_entrenamiento']
    
    textos = []
    etiquetas = []
    
    for ej in ejemplos:
        textos.append(ej['entrada'])
        etiquetas.append(ej['intencion'])
    
    return textos, etiquetas


def preparar_datos_productos(data):
    """Prepara datos para extracción de productos"""
    ejemplos = data['ejemplos_entrenamiento']
    
    datos_entrenamiento = []
    
    for ej in ejemplos:
        # El dataset balanceado no tiene 'productos', solo el original
        if ej['intencion'] == 'pedido' and 'productos' in ej and ej['productos']:
            for prod in ej['productos']:
                datos_entrenamiento.append({
                    'texto': ej['entrada'],
                    'producto': prod['nombre'],
                    'cantidad': prod['cantidad'],
                    'nota': prod['nota']
                })
    
    return datos_entrenamiento


def entrenar_clasificador_intencion(textos, etiquetas):
    """
    Entrena un clasificador de intención simple usando sklearn
    Para producción, usar transformers con fine-tuning
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import Pipeline
        from sklearn.model_selection import cross_val_score
        import pickle
        
        # Crear pipeline
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ('clf', MultinomialNB())
        ])
        
        # Entrenar
        pipeline.fit(textos, etiquetas)
        
        # Evaluar con validación cruzada
        scores = cross_val_score(pipeline, textos, etiquetas, cv=3)
        print(f"Precisión promedio: {scores.mean():.2f} (+/- {scores.std() * 2:.2f})")
        
        # Guardar modelo
        model_path = Path(__file__).parent / "intent_classifier_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(pipeline, f)
        
        print(f"Modelo guardado en: {model_path}")
        return pipeline
        
    except ImportError:
        print("Instala sklearn: pip install scikit-learn")
        return None


def crear_reglas_desde_dataset(data):
    """
    Crea reglas de extracción basadas en patrones del dataset
    Esto mejora el procesador sin necesidad de modelo de ML
    """
    ejemplos = data['ejemplos_entrenamiento']
    
    # Extraer patrones de productos
    patrones_producto = {}
    
    for ej in ejemplos:
        if ej['intencion'] == 'pedido' and 'productos' in ej:
            texto = ej['entrada'].lower()
            for prod in ej['productos']:
                nombre = prod['nombre']
                if nombre not in patrones_producto:
                    patrones_producto[nombre] = {
                        'ejemplos': [],
                        'notas_comunes': set()
                    }
                
                patrones_producto[nombre]['ejemplos'].append(texto)
                if prod['nota']:
                    patrones_producto[nombre]['notas_comunes'].add(prod['nota'])
    
    # Generar archivo de reglas
    reglas = {
        'productos': {},
        'sinonimos_detectados': [],
        'modificadores_comunes': set()
    }
    
    for nombre, info in patrones_producto.items():
        reglas['productos'][nombre] = {
            'num_ejemplos': len(info['ejemplos']),
            'notas': list(info['notas_comunes'])
        }
        
        # Detectar modificadores comunes
        for nota in info['notas_comunes']:
            palabras = nota.split()
            for palabra in palabras:
                if palabra in ['con', 'sin', 'extra', 'mucho', 'poco', 'grande', 'pequeño']:
                    reglas['modificadores_comunes'].add(palabra)
    
    reglas['modificadores_comunes'] = list(reglas['modificadores_comunes'])
    
    # Guardar reglas
    reglas_path = Path(__file__).parent / "reglas_extraidas.json"
    with open(reglas_path, 'w', encoding='utf-8') as f:
        json.dump(reglas, f, ensure_ascii=False, indent=2)
    
    print(f"Reglas extraídas guardadas en: {reglas_path}")
    return reglas


def generar_sinonimos_ampliados(data):
    """Genera diccionario de sinónimos expandido basado en el dataset"""
    productos_base = data.get('metadata', {}).get('categorias_productos', [
        "pizza", "hamburguesa", "tacos", "ensalada", "zumo", 
        "pasta", "pan", "hot dog", "refresco", "coca cola"
    ])
    
    sinonimos = {
        # Plurales
        "pizzas": "pizza",
        "hamburguesas": "hamburguesa",
        "ensaladas": "ensalada",
        "pastas": "pasta",
        "panes": "pan",
        "refrescos": "refresco",
        "zumos": "zumo",
        
        # Variaciones coca cola
        "coca": "coca cola",
        "cocas": "coca cola",
        "cola": "coca cola",
        "colas": "coca cola",
        "coca colas": "coca cola",
        "cocacola": "coca cola",
        "cocacolas": "coca cola",
        "coca light": "coca cola",
        "coca zero": "coca cola",
        
        # Variaciones hot dog
        "hotdog": "hot dog",
        "hotdogs": "hot dog",
        "hot dogs": "hot dog",
        "perrito": "hot dog",
        "perritos": "hot dog",
        "perrito caliente": "hot dog",
        "perritos calientes": "hot dog",
        
        # Variaciones zumo/jugo
        "jugo": "zumo",
        "jugos": "zumo",
        
        # Variaciones taco
        "taco": "tacos",
    }
    
    sinonimos_path = Path(__file__).parent / "sinonimos_ampliados.json"
    with open(sinonimos_path, 'w', encoding='utf-8') as f:
        json.dump(sinonimos, f, ensure_ascii=False, indent=2)
    
    print(f"Sinónimos ampliados guardados en: {sinonimos_path}")
    return sinonimos


def main():
    """Función principal de entrenamiento"""
    print("=" * 50)
    print("Entrenamiento del Clasificador de Pedidos")
    print("=" * 50)
    
    # Cargar dataset
    print("\n1. Cargando dataset...")
    data = cargar_dataset()
    print(f"   - {len(data['ejemplos_entrenamiento'])} ejemplos cargados")
    
    # Contar intenciones únicas
    intenciones = set(ej['intencion'] for ej in data['ejemplos_entrenamiento'])
    print(f"   - {len(intenciones)} tipos de intención")
    
    # Preparar datos
    print("\n2. Preparando datos...")
    textos, etiquetas = preparar_datos_intencion(data)
    datos_productos = preparar_datos_productos(data)
    print(f"   - {len(textos)} ejemplos de intención")
    print(f"   - {len(datos_productos)} ejemplos de productos")
    
    # Entrenar clasificador de intención
    print("\n3. Entrenando clasificador de intención...")
    modelo = entrenar_clasificador_intencion(textos, etiquetas)
    
    # Extraer reglas
    print("\n4. Extrayendo reglas del dataset...")
    reglas = crear_reglas_desde_dataset(data)
    
    # Generar sinónimos
    print("\n5. Generando diccionario de sinónimos...")
    sinonimos = generar_sinonimos_ampliados(data)
    
    print("\n" + "=" * 50)
    print("¡Entrenamiento completado!")
    print("=" * 50)
    
    # Probar el modelo
    if modelo:
        print("\n6. Probando el modelo...")
        pruebas = [
            "Quiero 2 pizzas con mucho queso",
            "Hola buenos días",
            "¿Cuánto cuesta la hamburguesa?",
            "El servicio es terrible",
            "Gracias, todo perfecto"
        ]
        
        for prueba in pruebas:
            prediccion = modelo.predict([prueba])[0]
            print(f"   '{prueba}' -> {prediccion}")


if __name__ == "__main__":
    main()
