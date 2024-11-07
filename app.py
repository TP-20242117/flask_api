from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

# Cargar el modelo guardado
voting_clf = joblib.load('voting_classifier.joblib')

# Inicializar la aplicación Flask
app = Flask(__name__)

# Función de diagnóstico (asegúrate de tener esta función definida en el mismo archivo o importada)
def diagnosticar_tdah_por_evaluacion(evaluation_data):
    """
    Diagnostica TDAH basado en los datos de una evaluación obtenida.
    Se espera que `evaluation_data` tenga los resultados de Stroop, CPT y SST.
    """
    # Extraer resultados de Stroop, CPT y SST de los datos de la evaluación
    stroop_result = evaluation_data['stroopResults'][0] if evaluation_data['stroopResults'] else None
    cpt_result = evaluation_data['cptResults'][0] if evaluation_data['cptResults'] else None
    sst_result = evaluation_data['sstResults'][0] if evaluation_data['sstResults'] else None

    # Verificar que todos los resultados necesarios estén disponibles
    if not (stroop_result and cpt_result and sst_result):
        raise ValueError("Faltan resultados de Stroop, CPT o SST para esta evaluación")

    # Preparar los datos de entrada en el formato esperado por el modelo
    datos_estudiante = [
        stroop_result['averageResponseTime'],
        stroop_result['correctAnswers'],
        stroop_result['incorrectAnswers'],
        cpt_result['averageResponseTime'],
        cpt_result['omissionErrors'],
        cpt_result['commissionErrors'],
        sst_result['averageResponseTime'],
        sst_result['correctStops'],
        sst_result['incorrectStops'],
        sst_result['ignoredArrows']
    ]

    # Hacer predicción
    prediccion = voting_clf.predict([datos_estudiante])[0]
    
    # Interpretar resultado
    diagnostico = prediccion == 1  # True si es TDAH, False si no

    return diagnostico

# Ruta para hacer predicciones
@app.route('/predict', methods=['POST'])
def predict():
    # Obtener los datos del JSON enviado en la solicitud
    evaluation_data = request.get_json(force=True)

    try:
        # Llamar a la función de diagnóstico
        diagnostico = diagnosticar_tdah_por_evaluacion(evaluation_data)
        return jsonify({"hasTdah": bool(diagnostico)})  # Devuelve true o false como JSON
    
    except ValueError as e:
        # Si falta algún dato, devolver un mensaje de error
        return jsonify({"error": str(e)}), 400

# Ejecutar la aplicación
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)