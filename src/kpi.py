import pandas as pd
from src import sg_bd as database

import pandas as pd
from src import sg_bd as database

def calcularTiempoMedioFase():
    pacientes = database.getPacientes()
    if not pacientes:
        print("No hay pacientes en la base.")
        return

    # 6 fases: (1→2), (3→4), …, (11→12)
    fases = [[] for _ in range(6)]

    # Para los desplazamientos (eventos 6,7,8,9)
#    desplazamientos_pacientes = []

    for p in pacientes:
        idPaciente = p[0]
        eventos = database.getInfoPacientePorID(idPaciente)
        if not eventos:
            continue

        df = pd.DataFrame([dict(ev) for ev in eventos])
        df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")

        # ---------- DESPLAZAMIENTOS EVENTOS 6,7,8,9 ----------
    #    df_6789 = df[df["idEvento"].isin([6, 7, 8, 9])].copy()
#
 #       if not df_6789.empty:
  #          # Solo nos quedamos con el día (ignoramos la hora)
   #         df_6789["fecha_dia"] = df_6789["fecha_inicio"].dt.date
#
 #           # Nº de días distintos = nº de desplazamientos
  #          num_desplazamientos = df_6789["fecha_dia"].nunique()
   #         desplazamientos_pacientes.append(num_desplazamientos)

        # ---------- TIEMPOS ENTRE FASES ----------
        for fase_idx, evento_i in enumerate(range(1, 12, 2)):
            fechas_e1 = df.loc[df["idEvento"] == evento_i, "fecha_inicio"].dropna().values
            fechas_e2 = df.loc[df["idEvento"] == (evento_i + 1), "fecha_inicio"].dropna().values

            if len(fechas_e1) == 0 or len(fechas_e2) == 0:
                continue

            fecha1 = pd.to_datetime(fechas_e1[0])
            candidatos = [pd.to_datetime(f) for f in fechas_e2 if pd.to_datetime(f) >= fecha1]
            if not candidatos:
                continue

            fecha2 = min(candidatos)
            diff = (fecha2 - fecha1).total_seconds() / 86400.0

            if diff >= 0:
                fases[fase_idx].append(diff)

    # ---------- MÁXIMO TIEMPO ENTRE FASES ----------
  #  max_tiempo = None
   # max_fase = None

#    for i, tiempos in enumerate(fases):
 #       if tiempos:
  #          max_fase_tiempo = max(tiempos)
   #         if max_tiempo is None or max_fase_tiempo > max_tiempo:
    #            max_tiempo = max_fase_tiempo
     #           max_fase = i + 1

#    if max_tiempo is not None:
 #       print(f"El tiempo más alto es: {round(max_tiempo,2)} días")
  #      print(f"Ocurre en la fase: {max_fase} (evento {max_fase*2 - 1} → {max_fase*2})")
   # else:
    #    print("No hay datos suficientes para calcular el tiempo máximo.")

    # ---------- MEDIAS POR FASE ----------
    medias = []
    for vals in fases:
        if vals:
            medias.append(round(sum(vals) / len(vals)))
        else:
            medias.append(None)

    medias_validas = [round(m) for m in medias if m is not None]
    tiempo_medio_total = sum(medias_validas) if medias_validas else None

    return medias, tiempo_medio_total, len(pacientes)

    # ---------- NUEVO: TIEMPO MEDIO TOTAL SIN FASE 1 ----------
#    medias_sin_fase1 = [round(m) for m in medias[1:] if m is not None]
#
 #   if medias_sin_fase1:
  #      tiempo_medio_sin_fase1 = sum(medias_sin_fase1)
   #     print("Tiempo medio total SIN fase 1 (días):", tiempo_medio_sin_fase1)
    #else:
     #   tiempo_medio_sin_fase1 = None
      #  print("No hay datos suficientes para calcular el tiempo sin fase 1.")

    # ---------- MEDIA DE DESPLAZAMIENTOS ----------
    #if desplazamientos_pacientes:
    #    media_desplazamientos = sum(desplazamientos_pacientes) / len(desplazamientos_pacientes)
    #    print("Media de desplazamientos por paciente (eventos 6–9):", round(media_desplazamientos, 2))
    #else:
    #    media_desplazamientos = None
#        print("No hay datos suficientes para calcular la media de desplazamientos.")

 #   return medias, tiempo_medio_total, tiempo_medio_sin_fase1, len(pacientes), max_tiempo, max_fase, media_desplazamientos
