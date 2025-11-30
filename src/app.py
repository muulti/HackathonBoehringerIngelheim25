from flask import Flask, render_template, jsonify, request
from src import PatientInfoManager as patientManager
from src.CalculadoraRiesgo import getRiesgo
import pandas as pd
import numpy as np
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluacion.html')
def evaluacion():
    return render_template('evaluacion.html')

@app.route('/listado.html')
def listado():
    return render_template('listado.html')

@app.get("/api/pacientes")
def get_pacientes():
    listaJSON = patientManager.getListaPacientes()
    return jsonify(listaJSON)

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/paciente/<int:id>')
def paciente_detail(id):
    return render_template('paciente_detail.html', paciente_id=id)

@app.route('/api/paciente/<int:id>/journey')
def get_paciente_journey(id):
    journey_data = patientManager.getPatientJourneyAnalysis(id)
    if journey_data is None:
        return jsonify({"error": "Paciente no encontrado"}), 404
    return jsonify(journey_data)

@app.route("/api/total-pacientes")
def total_pacientes():
    valores = patientManager.getKPIAnalytics()
    return valores
@app.route("/api/medias-fases")
def medias_fases():
    valores = patientManager.getMediasFases()
    return valores

@app.route("/procesar-paciente", methods=["POST"])
def procesar_paciente():
    data = request.get_json()  # recibe el JSON
    patientManager.addPaciente(data)
    return getRiesgo(data)

app.run()