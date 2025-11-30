import json
from flask import jsonify
from src import sg_bd as database
from src import kpi
import pandas as pd

def getListaPacientes():
    pacientes = database.getPacientes()  # [(1, 69, 'H'), ...]
    if pacientes is None:
        print("Lista pacientes vacía")
        return []  # prevenir errores
    lista_dicts = [{"id": x[0], "edad": x[1], "sexo": x[2]} for x in pacientes]
    return lista_dicts  # retorna json

def addPaciente(data):

    database.insertar_datos_paciente(data)
    return 0

def getInfoPaciente(idPaciente):
    paciente = database.getInfoPacientePorID(idPaciente)  # lista de dicts
    if not paciente:
        print("No se encontró paciente")
        return None
    eventosPaciente = [dict(r) for r in paciente]
    lista = [ev for ev in eventosPaciente]
    return lista  # devuelve lista de diccionarios

def getKPIAnalytics():
    #DEBE ESTAR EN JSON!!!!!
    medias, total, numPacientes = kpi.calcularTiempoMedioFase()

    valores = {
        "tiempoPromedio": total,
        "totalPacientes": numPacientes,
        "riesgo": 33,
        "extra": 44
        #Cualquier otra cosa que querais
    }
    valores = jsonify(valores)
    print(valores)
    return valores

def getMediasFases():
    print("Getting means")
    medias, total, numPacientes = kpi.calcularTiempoMedioFase()
    medias_json = [{f"TiempoFase{i + 1}": medias[i]} for i in range(len(medias))]
    print(medias_json)
    medias_json = jsonify(medias_json)
    return medias_json


def getPatientJourneyAnalysis(idPaciente):
    """
    Analiza el journey completo de un paciente individual
    Retorna tiempos por fase, eventos, desplazamientos y cuellos de botella
    """
    # Obtener datos del paciente
    paciente_info = database.getPacientePorID(idPaciente)
    if not paciente_info:
        return None

    eventos = database.getInfoPacientePorID(idPaciente)
    if not eventos:
        return {
            "paciente": {
                "id": paciente_info[0][0],
                "edad": paciente_info[0][1],
                "sexo": paciente_info[0][2]
            },
            "eventos": [],
            "fases": [],
            "resumen": {
                "tiempoTotal": 0,
                "faseMasLenta": None,
                "desplazamientos": 0
            }
        }

    # Convertir eventos a DataFrame
    df = pd.DataFrame([dict(ev) for ev in eventos])
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")

    # Obtener datos básicos del paciente
    paciente_data = {
        "id": paciente_info[0][0],
        "edad": paciente_info[0][1],
        "sexo": "Masculino" if paciente_info[0][2] == "H" else "Femenino"
    }

    # Calcular desplazamientos (eventos 6, 7, 8, 9)
    df_desplazamientos = df[df["idEvento"].isin([1, 2, 3, 4, 5, 6, 7, 8, 9])].copy()
    num_desplazamientos = 0
    if not df_desplazamientos.empty:
        df_desplazamientos["fecha_dia"] = df_desplazamientos["fecha_inicio"].dt.date
        num_desplazamientos = df_desplazamientos["fecha_dia"].nunique()

    # Calcular tiempos entre fases (1→2, 3→4, ..., 11→12)
    fases_data = []
    eventos_lista = []
    tiempo_total = 0
    max_tiempo_fase = 0
    fase_mas_lenta = None

    nombres_fases = [
        "Atención Primaria",
        "Análisis Básico",
        "Análisis Completo",
        "Neumología",
        "Pruebas Avanzadas",
        "Diagnóstico Final"
    ]

    # Variable para rastrear si encontramos una fase incompleta
    fase_bloqueada = False

    for fase_idx, evento_inicio in enumerate(range(1, 12, 2)):
        evento_fin = evento_inicio + 1

        # Buscar fechas de inicio y fin de la fase
        fechas_inicio = df.loc[df["idEvento"] == evento_inicio, "fecha_inicio"].dropna().values
        fechas_fin = df.loc[df["idEvento"] == evento_fin, "fecha_inicio"].dropna().values

        # Si ya hay una fase bloqueada, todas las siguientes están pendientes
        if fase_bloqueada:
            fases_data.append({
                "numero": fase_idx + 1,
                "nombre": nombres_fases[fase_idx],
                "eventoInicio": evento_inicio,
                "eventoFin": evento_fin,
                "fechaInicio": None,
                "fechaFin": None,
                "dias": None,
                "estado": "pendiente"
            })
            continue

        # Si no hay evento de inicio, la fase no ha comenzado
        if len(fechas_inicio) == 0:
            fase_bloqueada = True
            fases_data.append({
                "numero": fase_idx + 1,
                "nombre": nombres_fases[fase_idx],
                "eventoInicio": evento_inicio,
                "eventoFin": evento_fin,
                "fechaInicio": None,
                "fechaFin": None,
                "dias": None,
                "estado": "no_iniciada"
            })
            continue

        fecha_inicio = pd.to_datetime(fechas_inicio[0])

        # Si no hay evento de fin, la fase está en curso
        if len(fechas_fin) == 0:
            fase_bloqueada = True
            fases_data.append({
                "numero": fase_idx + 1,
                "nombre": nombres_fases[fase_idx],
                "eventoInicio": evento_inicio,
                "eventoFin": evento_fin,
                "fechaInicio": fecha_inicio.strftime("%Y-%m-%d %H:%M"),
                "fechaFin": None,
                "dias": None,
                "estado": "en_curso"
            })
            continue

        # Buscar la primera fecha de fin posterior a la fecha de inicio
        candidatos = [pd.to_datetime(f) for f in fechas_fin if pd.to_datetime(f) >= fecha_inicio]
        if not candidatos:
            fase_bloqueada = True
            fases_data.append({
                "numero": fase_idx + 1,
                "nombre": nombres_fases[fase_idx],
                "eventoInicio": evento_inicio,
                "eventoFin": evento_fin,
                "fechaInicio": fecha_inicio.strftime("%Y-%m-%d %H:%M"),
                "fechaFin": None,
                "dias": None,
                "estado": "en_curso"
            })
            continue

        # La fase está completada
        fecha_fin = min(candidatos)
        dias = (fecha_fin - fecha_inicio).total_seconds() / 86400.0

        if dias >= 0:
            tiempo_total += dias

            # Identificar fase más lenta
            if dias > max_tiempo_fase:
                max_tiempo_fase = dias
                fase_mas_lenta = {
                    "numero": fase_idx + 1,
                    "nombre": nombres_fases[fase_idx],
                    "dias": round(dias, 2)
                }

            fases_data.append({
                "numero": fase_idx + 1,
                "nombre": nombres_fases[fase_idx],
                "eventoInicio": evento_inicio,
                "eventoFin": evento_fin,
                "fechaInicio": fecha_inicio.strftime("%Y-%m-%d %H:%M"),
                "fechaFin": fecha_fin.strftime("%Y-%m-%d %H:%M"),
                "dias": round(dias, 2),
                "estado": "completada"
            })
        else:
            # Caso edge: si los días son negativos, marcar como error
            fase_bloqueada = True
            fases_data.append({
                "numero": fase_idx + 1,
                "nombre": nombres_fases[fase_idx],
                "eventoInicio": evento_inicio,
                "eventoFin": evento_fin,
                "fechaInicio": fecha_inicio.strftime("%Y-%m-%d %H:%M"),
                "fechaFin": None,
                "dias": None,
                "estado": "en_curso"
            })

    # Lista de todos los eventos registrados
    for _, row in df.iterrows():
        if pd.notna(row["fecha_inicio"]):
            eventos_lista.append({
                "idEvento": int(row["idEvento"]),
                "fecha": row["fecha_inicio"].strftime("%Y-%m-%d %H:%M"),
                "descripcion": obtener_descripcion_evento(int(row["idEvento"]))
            })

    # Ordenar eventos por fecha
    eventos_lista.sort(key=lambda x: x["fecha"])

    # Obtener promedios generales para comparación - CORRECCIÓN AQUÍ
    medias_generales, _, _ = kpi.calcularTiempoMedioFase()

    # Comparar con promedios
    comparacion_fases = []
    for fase in fases_data:
        if fase["dias"] is not None and fase["numero"] <= len(medias_generales):
            promedio_general = medias_generales[fase["numero"] - 1]
            if promedio_general is not None:
                diferencia = fase["dias"] - promedio_general
                comparacion_fases.append({
                    "fase": fase["numero"],
                    "nombre": fase["nombre"],
                    "tiempoPaciente": fase["dias"],
                    "tiempoPromedio": round(promedio_general, 2),
                    "diferencia": round(diferencia, 2),
                    "porcentaje": round((diferencia / promedio_general * 100), 1) if promedio_general > 0 else 0,
                    "estado": "retrasado" if diferencia > promedio_general * 0.2 else "normal"
                })

    return {
        "paciente": paciente_data,
        "eventos": eventos_lista,
        "fases": fases_data,
        "comparacion": comparacion_fases,
        "resumen": {
            "tiempoTotal": round(tiempo_total, 2),
            "faseMasLenta": fase_mas_lenta,
            "desplazamientos": num_desplazamientos,
            "fasesCompletadas": len([f for f in fases_data if f["estado"] == "completada"]),
            "fasesEnCurso": len([f for f in fases_data if f["estado"] == "en_curso"]),
            "fasesNoIniciadas": len([f for f in fases_data if f["estado"] in ["no_iniciada", "pendiente"]])
        }
    }


def obtener_descripcion_evento(id_evento):
    """Retorna una descripción legible del evento"""
    eventos = {
        1: "Primera visita AP - Primera consulta en atención primaria",
        2: "Analítica básica - Analítica de sangre estándar",
        3: "Analítica completa - Analítica de sangre ampliada",
        4: "Radiografía tórax - Radiografía simple de tórax",
        5: "Derivación a Neumología - Paciente remitido a especialista en Neumología",
        6: "TAC torácico - Tomografía axial computarizada del tórax",
        7: "PET-TAC - PET-TAC para estudio metabólico",
        8: "Biopsia - Obtención de muestra para análisis",
        9: "Anatomía patológica - Análisis de la muestra en anatomía patológica",
        10: "Diagnóstico final - Conclusión diagnóstica del proceso",
        11: "Cita con Oncología - Consulta con oncólogo para valorar tratamiento",
        12: "Inicio tratamiento - Comienzo del tratamiento oncológico"
    }
    return eventos.get(id_evento, f"Evento {id_evento}")