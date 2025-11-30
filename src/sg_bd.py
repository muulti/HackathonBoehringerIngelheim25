import sqlite3
from sqlite3 import connect

def printInfo():
    con = sqlite3.connect("../db_hackathon2.db")
    cur = con.cursor()
    cur.execute("PRAGMA table_info(paciente);")
    print(cur.fetchall())
def getPacientes():
    con = sqlite3.connect("../db_hackathon2.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM paciente")
    results = cur.fetchall()
    return results
def getPacientePorID(idPaciente):
    con = sqlite3.connect("../db_hackathon2.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM paciente WHERE idPaciente = ?", (idPaciente,))
    results = cur.fetchall()
    return results

'''
# Asumimos que esta función recibe el diccionario con los datos del formulario
def insertar_datos_paciente(datos_formulario: dict):

    query = """
            INSERT INTO pacientes (age, sex, smoking_level, passive_smoker, occupation_hazard, \
                                   genetic_risk, chronic_lung_disease, air_pollution, alcohol_use, \
                                   obesity, chest_pain, shortness_of_breath, wheezing, \
                                   hemoptysis_level, fatigue, swallowing_difficulty, clubbing_nails, \
                                   weight_loss)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
            """

    # 2. Creamos la tupla de valores extrayendo los datos del diccionario
    # Es importante usar .get() para evitar errores si falta alguna clave
    valores = (
        datos_formulario.get('age'),
        datos_formulario.get('sex'),
        datos_formulario.get('smoking_level'),
        datos_formulario.get('passive_smoker'),
        datos_formulario.get('occupation_hazard'),
        datos_formulario.get('genetic_risk'),
        datos_formulario.get('chronic_lung_disease'),
        datos_formulario.get('air_pollution'),
        datos_formulario.get('alcohol_use'),
        datos_formulario.get('obesity'),
        datos_formulario.get('chest_pain'),
        datos_formulario.get('shortness_of_breath'),
        datos_formulario.get('wheezing'),
        datos_formulario.get('hemoptysis_level'),
        datos_formulario.get('fatigue'),
        datos_formulario.get('swallowing_difficulty'),
        datos_formulario.get('clubbing_nails'),
        datos_formulario.get('weight_loss')
    )

    try:
        # Ajusta la ruta a tu base de datos si es necesario
        with sqlite3.connect("../db_hackathon2.db") as con:
            cursor = con.cursor()
            cursor.execute(query, valores)
            con.commit()

            print(f"Paciente insertado con éxito. ID generado: {cursor.lastrowid}")
            return cursor.lastrowid

    except sqlite3.Error as e:
        print(f"Error de inserción SQLite: {e}")
        return None

    return rows
'''

def crear_paciente_si_no_existe(form: dict):
    sexo = ""
    id_paciente = form.get("id")
    print(f"El ID del paciente debería ser el siguiente: {id_paciente}")
    try:
        with sqlite3.connect("../db_hackathon2.db") as con:
            cursor = con.cursor()

            # Si id está vacío o es None → crear paciente nuevo
            if not id_paciente:
                print("No se envió ID → se creará un paciente nuevo.")

                print(form.get("sex"))
                if form.get("sex") == "1":
                    sexo = "M"
                else:
                    sexo = "H"

                cursor.execute(
                    "INSERT INTO paciente (edad, sexo) VALUES (?, ?)",
                    (form.get("age"), sexo)
                )
                con.commit()

                nuevo_id = cursor.lastrowid
                print("Paciente creado con ID:", nuevo_id)
                return nuevo_id

            # Si id sí existe → comprobar si está en la BD
            cursor.execute("SELECT id FROM paciente WHERE id = ?", (id_paciente,))
            existe = cursor.fetchone()

            if existe:
                return id_paciente

            # Si id viene pero NO existe → crear paciente con ese ID
            cursor.execute(
                "INSERT INTO paciente (id, age, sex) VALUES (?, ?, ?)",
                (id_paciente, form.get("age"), sexo)
            )
            con.commit()

            return id_paciente

    except sqlite3.Error as e:
        print("Error SQLite creando paciente:", e)
        return None


def insertar_datos_paciente(form: dict):

    # 1. Asegurar que el paciente existe (o crearlo)
    id_paciente = crear_paciente_si_no_existe(form)

    if id_paciente is None:
        return None

    # 2. Mapear campos JS → SQL
    datos = {
        'idPaciente': id_paciente,
        'nivel_fumacion': form.get('smoking_level'),
        'fumador_pasivo': form.get('passive_smoker'),
        'occupational_hazard': form.get('occupation_hazard'),
        'riesgo_genetico': form.get('genetic_risk'),
        'epoc': form.get('chronic_lung_disease'),
        'air_pollution_level': form.get('air_pollution'),
        'alcohol': form.get('alcohol_use'),
        'obesity': form.get('obesity'),
        'chest_pain': form.get('chest_pain'),
        'fatigue': form.get('fatigue'),
        'weight_loss': form.get('weight_loss'),
        'heptomisis': form.get('hemoptysis_level'),
        'breath_shortness': form.get('shortness_of_breath'),
        'wheezing': form.get('wheezing'),
        'swallowing_diff': form.get('swallowing_difficulty'),
        'clubbing_nails': form.get('clubbing_nails')
    }

    try:
        with sqlite3.connect("../db_hackathon2.db") as con:
            cursor = con.cursor()

            query = """
                INSERT INTO datos (
                    idPaciente,
                    nivel_fumacion,
                    fumador_pasivo,
                    occupational_hazard,
                    riesgo_genetico,
                    epoc,
                    air_pollution_level,
                    alcohol,
                    obesity,
                    chest_pain,
                    fatigue,
                    weight_loss,
                    heptomisis,
                    breath_shortness,
                    wheezing,
                    swallowing_diff,
                    clubbing_nails
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, tuple(datos.values()))
            con.commit()

            print("Datos médicos insertados correctamente.")
            return cursor.lastrowid

    except sqlite3.Error as e:
        print(f"Error al insertar datos médicos: {e}")
        return None



def getInfoPacientePorID(idPaciente: int):
    con = sqlite3.connect("../db_hackathon2.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    sql = """
    SELECT 
        p.*,
        ep.*,
        d.*
    FROM paciente AS p
    LEFT JOIN paciente_evento AS ep 
        ON ep.idPaciente = p.idPaciente
    LEFT JOIN datos AS d 
        ON d.id = p.idPaciente
    WHERE p.idPaciente = ?;
    """

    cur.execute(sql, (idPaciente,))
    rows = cur.fetchall()
    con.close()

    # Si no existe el paciente → return None
    if not rows:
        return None

    return rows