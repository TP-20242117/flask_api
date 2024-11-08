from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import os

# Cargar el modelo guardado
voting_clf = joblib.load('voting_classifier.joblib')

# Inicializar la aplicación Flask
app = Flask(__name__)
CORS(app)

# Función de diagnóstico
def diagnosticar_tdah_por_evaluacion(evaluation_data):
    """
    Diagnostica TDAH basado en los datos de una evaluación obtenida.
    Se espera que `evaluation_data` tenga los resultados de Stroop, CPT y SST.
    """
    # Extraer resultados de Stroop, CPT y SST de los datos de la evaluación
    stroop_result = evaluation_data.get('stroopResults', [None])[0]
    cpt_result = evaluation_data.get('cptResults', [None])[0]
    sst_result = evaluation_data.get('sstResults', [None])[0]

    # Verificar que todos los resultados necesarios estén disponibles
    if not stroop_result or not cpt_result or not sst_result:
        return None, "Faltan datos necesarios en stroopResults, cptResults o sstResults"

    # Preparar los datos de entrada en el formato esperado por el modelo
    datos_estudiante = [
        stroop_result.get('averageResponseTime'),
        stroop_result.get('correctAnswers'),
        stroop_result.get('incorrectAnswers'),
        cpt_result.get('averageResponseTime'),
        cpt_result.get('omissionErrors'),
        cpt_result.get('commissionErrors'),
        sst_result.get('averageResponseTime'),
        sst_result.get('correctStops'),
        sst_result.get('incorrectStops'),
        sst_result.get('ignoredArrows')
    ]

    # Verificar que todos los campos de datos_estudiante tengan valores
    if any(dato is None for dato in datos_estudiante):
        return None, "Faltan valores en los resultados de la evaluación"

    # Hacer predicción
    prediccion = voting_clf.predict([datos_estudiante])[0]
    
    # Interpretar resultado
    diagnostico = prediccion == 1  # True si es TDAH, False si no

    return diagnostico, "success"

# Ruta para hacer predicciones
@app.route('/predict', methods=['POST'])
def predict():
    # Obtener los datos del JSON enviado en la solicitud
    evaluation_data = request.get_json(force=True)

    # Llamar a la función de diagnóstico
    diagnostico, status = diagnosticar_tdah_por_evaluacion(evaluation_data)

    if status != "success":
        # Retorna un error de datos incompletos en formato JSON, con código 400
        return jsonify({"hasTdah": None, "status": "failed", "message": status}), 400

    # Si todos los datos están correctos, devuelve el diagnóstico
    return jsonify({"hasTdah": bool(diagnostico), "status": status})

# Ejecutar la aplicación
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
