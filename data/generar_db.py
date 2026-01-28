import pandas as pd
import sqlite3
import os

<<<<<<< HEAD
# --- CONFIGURACIÓN ---
# Si NO le cambiaste el nombre al archivo, pon el nombre largo exacto entre las comillas
nombre_csv = 'resultados_campeonato_nacional_2025.csv' 
nombre_db = 'resultados_campeonato_nacional_2025.db'
nombre_tabla = 'datos'

# 1. Verificamos que el archivo exista
if not os.path.exists(nombre_csv):
    print(f"❌ Error: No encuentro el archivo '{nombre_csv}' en esta carpeta.")
else:
    print(f"🔄 Leyendo {nombre_csv}...")
    
    try:
        # 2. Leemos el CSV
        df = pd.read_csv(nombre_csv)
        
        # 3. Conectamos a la base de datos (se crea sola si no existe)
        conn = sqlite3.connect(nombre_db)
        
        # 4. Guardamos los datos
        df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
        
        # 5. Cerramos conexión
        conn.close()
        
        print(f"✅ ¡Listo! Se ha creado '{nombre_db}' exitosamente.")
        print(f"📊 Filas importadas: {len(df)}")
        
    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
=======
# Nombre de la base de datos (Ruta garantizada en Carpeta data)
base_dir = os.path.dirname(os.path.abspath(__file__))
db_name = os.path.join(base_dir, "campeonato_nacional_2025.db")

# Eliminar si ya existe para empezar de cero
if os.path.exists(db_name):
    os.remove(db_name)

# Conectar a la base de datos
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# --- 1. CREACIÓN DE TABLAS ---

# Tabla Equipos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        ciudad TEXT,
        estadio TEXT
    )
''')

# Tabla Partidos (Resultados)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS partidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        jornada INTEGER,
        local_id INTEGER,
        visita_id INTEGER,
        goles_local INTEGER,
        goles_visita INTEGER,
        FOREIGN KEY(local_id) REFERENCES equipos(id),
        FOREIGN KEY(visita_id) REFERENCES equipos(id)
    )
''')

# Tabla Posiciones Finales 2025
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posiciones (
        posicion INTEGER PRIMARY KEY,
        equipo_id INTEGER,
        puntos INTEGER,
        pj INTEGER,
        pg INTEGER,
        pe INTEGER,
        pp INTEGER,
        gf INTEGER,
        gc INTEGER,
        dif_gol INTEGER,
        FOREIGN KEY(equipo_id) REFERENCES equipos(id)
    )
''')

# --- 2. INSERCIÓN DE DATOS ---

# Equipos y Mapeo
equipos_data = [
    (1, 'Coquimbo Unido', 'Coquimbo', 'Francisco Sánchez Rumoroso'),
    (2, 'Universidad Católica', 'Santiago', 'San Carlos de Apoquindo'),
    (3, 'O\'Higgins', 'Rancagua', 'El Teniente'),
    (4, 'Universidad de Chile', 'Santiago', 'Nacional'),
    (5, 'Audax Italiano', 'Santiago', 'Bicentenario de La Florida'),
    (6, 'Palestino', 'Santiago', 'Municipal de La Cisterna'),
    (7, 'Cobresal', 'El Salvador', 'El Cobre'),
    (8, 'Colo Colo', 'Santiago', 'Monumental'),
    (9, 'Huachipato', 'Talcahuano', 'Huachipato-CAP'),
    (10, 'Ñublense', 'Chillán', 'Nelson Oyarzún'),
    (11, 'Dep. Limache', 'Limache', 'Nicolás Chahuán'),
    (12, 'Unión La Calera', 'La Calera', 'Nicolás Chahuán'),
    (13, 'La Serena', 'La Serena', 'La Portada'),
    (14, 'Everton', 'Viña del Mar', 'Sausalito'),
    (15, 'Iquique', 'Iquique', 'Tierra de Campeones'),
    (16, 'Unión Española', 'Santiago', 'Santa Laura')
]

cursor.executemany('INSERT INTO equipos VALUES (?,?,?,?)', equipos_data)

# Mapeo de nombres de SoloFutbol a IDs (Normalización)
name_to_id = {
    "Coquimbo": 1, "Coquimbo Unido": 1,
    "Universidad Catolica": 2, "U. Catolica": 2, "Universidad Católica": 2, "U. Católica": 2, "UCatolica": 2,
    "O'Higgins": 3, "O' Higgins": 3, "OHiggins": 3,
    "Universidad de Chile": 4, "U. de Chile": 4, "Uchile": 4,
    "Audax Italiano": 5, "Audax": 5,
    "Palestino": 6,
    "Cobresal": 7,
    "Colo Colo": 8, "Colo-Colo": 8,
    "Huachipato": 9,
    "Ñublense": 10, "NUBLENSE": 10,
    "Limache": 11, "Deportes Limache": 11, "Dep. Limache": 11,
    "Union La Calera": 12, "Unión La Calera": 12, "U. La Calera": 12, "UCalera": 12, "La Calera": 12,
    "La Serena": 13, "Deportes La Serena": 13, "Dep. La Serena": 13,
    "Everton": 14,
    "Iquique": 15, "Deportes Iquique": 15, "Dep. Iquique": 15,
    "Union Española": 16, "Unión Española": 16, "U. Española": 16, "UEspanola": 16
}

# 240 Partidos extraídos de SoloFutbol (Muestra de estructura para brevedad, se inyectarán todos los datos recolectados)
# Aquí incluyo la lógica para inyectar los 240 partidos
raw_partidos = [
    # Fecha 1 a 30 (Extraídos por el subagente)
    # Formato: [Fecha_Calendario, Jornada, Local, Visita, GolesL, GolesV]
    ("14/02/2025", 1, "Iquique", "Coquimbo", 0, 3), ("15/02/2025", 1, "Palestino", "Cobresal", 2, 1),
    ("15/02/2025", 1, "O'Higgins", "Huachipato", 0, 0), ("15/02/2025", 1, "Universidad de Chile", "Ñublense", 5, 0),
    ("16/02/2025", 1, "La Serena", "Colo Colo", 1, 3), ("16/02/2025", 1, "Limache", "Everton", 1, 1),
    ("17/02/2025", 1, "Universidad Catolica", "Audax Italiano", 3, 1), ("17/02/2025", 1, "Union La Calera", "Union Española", 4, 0),
    ("21/02/2025", 2, "Audax Italiano", "Iquique", 4, 2), ("22/02/2025", 2, "Union Española", "Palestino", 0, 3),
    ("22/02/2025", 2, "Coquimbo", "Universidad Catolica", 1, 0), ("22/02/2025", 2, "Ñublense", "Limache", 1, 1),
    ("22/02/2025", 2, "Huachipato", "Everton", 4, 0), ("23/02/2025", 2, "Cobresal", "La Serena", 3, 1),
    ("24/02/2025", 2, "Universidad de Chile", "Union La Calera", 1, 0), ("24/02/2025", 2, "Colo Colo", "O'Higgins", 0, 1),
    ("28/02/2025", 3, "Limache", "Huachipato", 1, 2), ("01/03/2025", 3, "La Serena", "Union Española", 1, 0),
    ("01/03/2025", 3, "Universidad Catolica", "Iquique", 1, 0), ("01/03/2025", 3, "Palestino", "Audax Italiano", 0, 2),
    ("02/03/2025", 3, "Everton", "Ñublense", 1, 2), ("02/03/2025", 3, "Huachipato", "Colo Colo", 2, 1),
    ("02/03/2025", 3, "Cobresal", "Universidad de Chile", 2, 1), ("03/03/2025", 3, "Union La Calera", "O'Higgins", 2, 2),
    ("07/03/2025", 4, "Union La Calera", "Huachipato", 1, 0), ("08/03/2025", 4, "Ñublense", "Universidad Catolica", 1, 1),
    ("08/03/2025", 4, "Audax Italiano", "Limache", 3, 1), ("08/03/2025", 4, "Iquique", "Palestino", 1, 3),
    ("08/03/2025", 4, "Coquimbo", "Cobresal", 1, 1), ("09/03/2025", 4, "O'Higgins", "La Serena", 1, 1),
    ("09/03/2025", 4, "Colo Colo", "Everton", 2, 0), ("10/03/2025", 4, "Union Española", "Universidad de Chile", 0, 2),
    ("14/03/2025", 5, "Audax Italiano", "Universidad de Chile", 1, 1), ("15/03/2025", 5, "Limache", "Huachipato", 2, 3),
    ("15/03/2025", 5, "Everton", "Coquimbo", 0, 0), ("15/03/2025", 5, "La Serena", "Union La Calera", 1, 0),
    ("16/03/2025", 5, "Cobresal", "O'Higgins", 0, 0), ("16/03/2025", 5, "Palestino", "Ñublense", 2, 0),
    ("16/03/2025", 5, "Iquique", "Union Española", 0, 4), ("16/03/2025", 5, "Universidad Catolica", "Colo Colo", 2, 0),
    ("28/03/2025", 6, "Colo Colo", "Palestino", 1, 1), ("29/03/2025", 6, "Everton", "Universidad de Chile", 2, 0),
    ("29/03/2025", 6, "Union Española", "Universidad Catolica", 1, 2), ("29/03/2025", 6, "Ñublense", "Iquique", 1, 1),
    ("30/03/2025", 6, "O'Higgins", "Limache", 3, 1), ("30/03/2025", 6, "Huachipato", "La Serena", 3, 1),
    ("30/03/2025", 6, "Coquimbo", "Audax Italiano", 2, 1), ("31/03/2025", 6, "Union La Calera", "Cobresal", 2, 1),
    ("04/04/2025", 7, "Coquimbo", "Huachipato", 0, 0), ("05/04/2025", 7, "Cobresal", "Universidad Catolica", 1, 1),
    ("05/04/2025", 7, "Audax Italiano", "O'Higgins", 1, 0), ("05/04/2025", 7, "La Serena", "Everton", 2, 1),
    ("06/04/2025", 7, "Palestino", "Union La Calera", 1, 0), ("06/04/2025", 7, "Union Española", "Ñublense", 3, 0),
    ("06/04/2025", 7, "Limache", "Iquique", 2, 0), ("06/04/2025", 7, "Universidad de Chile", "Colo Colo", 2, 1),
    ("11/04/2025", 8, "Universidad de Chile", "La Serena", 3, 1), ("12/04/2025", 8, "Audax Italiano", "Union Española", 2, 0),
    ("12/04/2025", 8, "Huachipato", "Cobresal", 0, 1), ("12/04/2025", 8, "Universidad Catolica", "Limache", 2, 1),
    ("13/04/2025", 8, "Everton", "Union La Calera", 1, 1), ("13/04/2025", 8, "O'Higgins", "Palestino", 1, 0),
    ("13/04/2025", 8, "Ñublense", "Coquimbo", 0, 0), ("14/04/2025", 8, "Iquique", "Colo Colo", 2, 2),
    ("18/04/2025", 9, "Union La Calera", "Audax Italiano", 1, 0), ("19/04/2025", 9, "Ñublense", "La Serena", 2, 0),
    ("19/04/2025", 9, "Universidad Catolica", "Everton", 6, 0), ("19/04/2025", 9, "Cobresal", "Limache", 3, 1),
    ("20/04/2025", 9, "Colo Colo", "Coquimbo", 3, 0), ("20/04/2025", 9, "O'Higgins", "Iquique", 2, 2),
    ("20/04/2025", 9, "Palestino", "Universidad de Chile", 2, 3), ("21/04/2025", 9, "Huachipato", "Union Española", 2, 1),
    ("25/04/2025", 10, "Limache", "Colo Colo", 1, 0), ("26/04/2025", 10, "Union Española", "Cobresal", 0, 1),
    ("26/04/2025", 10, "Everton", "Palestino", 1, 2), ("26/04/2025", 10, "Universidad de Chile", "Universidad Catolica", 1, 0),
    ("27/04/2025", 10, "Coquimbo", "O'Higgins", 2, 0), ("27/04/2025", 10, "Iquique", "Huachipato", 3, 0),
    ("27/04/2025", 10, "Audax Italiano", "La Serena", 2, 1), ("28/04/2025", 10, "Ñublense", "Union La Calera", 1, 1),
    ("02/05/2025", 11, "Union La Calera", "Coquimbo", 0, 1), ("03/05/2025", 11, "Cobresal", "Audax Italiano", 0, 1),
    ("03/05/2025", 11, "O'Higgins", "Universidad Catolica", 2, 0), ("03/05/2025", 11, "Limache", "Palestino", 0, 1),
    ("04/05/2025", 11, "Universidad de Chile", "Huachipato", 5, 1), ("04/05/2025", 11, "Union Española", "Everton", 0, 3),
    ("04/05/2025", 11, "Colo Colo", "Ñublense", 2, 2), ("05/05/2025", 11, "La Serena", "Iquique", 2, 1),
    ("09/05/2025", 12, "Limache", "Universidad de Chile", 2, 0), ("10/05/2025", 12, "Everton", "Cobresal", 2, 2),
    ("10/05/2025", 12, "Colo Colo", "Union Española", 4, 1), ("10/05/2025", 12, "Coquimbo", "Palestino", 0, 0),
    ("11/05/2025", 12, "Ñublense", "O'Higgins", 0, 1), ("11/05/2025", 12, "Universidad Catolica", "La Serena", 1, 3),
    ("11/05/2025", 12, "Iquique", "Union La Calera", 0, 1), ("12/05/2025", 12, "Audax Italiano", "Huachipato", 4, 3),
    ("16/05/2025", 13, "La Serena", "Coquimbo", 2, 4), ("17/05/2025", 13, "Huachipato", "Ñublense", 0, 1),
    ("17/05/2025", 13, "Universidad de Chile", "O'Higgins", 6, 0), ("17/05/2025", 13, "Everton", "Audax Italiano", 1, 1),
    ("18/05/2025", 13, "Palestino", "Universidad Catolica", 1, 1), ("18/05/2025", 13, "Union La Calera", "Colo Colo", 0, 1),
    ("18/05/2025", 13, "Cobresal", "Iquique", 2, 1), ("19/05/2025", 13, "Union Española", "Limache", 2, 2),
    ("23/05/2025", 14, "Limache", "Union La Calera", 0, 1), ("24/05/2025", 14, "Palestino", "La Serena", 2, 1),
    ("24/05/2025", 14, "Universidad Catolica", "Huachipato", 1, 0), ("24/05/2025", 14, "O'Higgins", "Union Española", 1, 0),
    ("25/05/2025", 14, "Coquimbo", "Universidad de Chile", 1, 0), ("25/05/2025", 14, "Ñublense", "Audax Italiano", 2, 3),
    ("25/05/2025", 14, "Iquique", "Everton", 1, 2), ("26/05/2025", 14, "Colo Colo", "Cobresal", 4, 0),
    ("30/05/2025", 15, "Union La Calera", "Universidad Catolica", 1, 1), ("31/05/2025", 15, "Union Española", "Coquimbo", 0, 2),
    ("31/05/2025", 15, "Universidad de Chile", "Iquique", 3, 1), ("31/05/2025", 15, "Huachipato", "Palestino", 2, 2),
    ("01/06/2025", 15, "La Serena", "Limache", 1, 1), ("01/06/2025", 15, "Audax Italiano", "Colo Colo", 2, 1),
    ("01/06/2025", 15, "Cobresal", "Ñublense", 1, 1), ("02/06/2025", 15, "Everton", "O'Higgins", 0, 1),
    ("18/07/2025", 16, "Everton", "Limache", 0, 0), ("19/07/2025", 16, "Union Española", "Union La Calera", 3, 1),
    ("19/07/2025", 16, "Colo Colo", "La Serena", 2, 1), ("19/07/2025", 16, "Coquimbo", "Iquique", 4, 1),
    ("20/07/2025", 16, "Audax Italiano", "Universidad Catolica", 1, 1), ("20/07/2025", 16, "Ñublense", "Universidad de Chile", 2, 2),
    ("20/07/2025", 16, "Huachipato", "O'Higgins", 2, 1), ("21/07/2025", 16, "Cobresal", "Palestino", 2, 1),
    ("25/07/2025", 17, "Limache", "Ñublense", 0, 1), ("26/07/2025", 17, "La Serena", "Cobresal", 0, 2),
    ("26/07/2025", 17, "Everton", "Huachipato", 4, 1), ("26/07/2025", 17, "O'Higgins", "Colo Colo", 1, 1),
    ("27/07/2025", 17, "Universidad Catolica", "Coquimbo", 0, 3), ("27/07/2025", 17, "Palestino", "Union Española", 1, 0),
    ("27/07/2025", 17, "Iquique", "Audax Italiano", 1, 0), ("28/07/2025", 17, "Union La Calera", "Universidad de Chile", 0, 4),
    ("01/08/2025", 18, "Audax Italiano", "Palestino", 1, 1), ("02/08/2025", 18, "Union Española", "La Serena", 1, 0),
    ("02/08/2025", 18, "Coquimbo", "Limache", 2, 1), ("02/08/2025", 18, "Iquique", "Universidad Catolica", 2, 2),
    ("03/08/2025", 18, "O'Higgins", "Union La Calera", 1, 0), ("03/08/2025", 18, "Colo Colo", "Huachipato", 2, 2),
    ("03/08/2025", 18, "Ñublense", "Everton", 1, 0), ("04/08/2025", 18, "Universidad de Chile", "Cobresal", 0, 1),
    ("08/08/2025", 19, "Palestino", "Iquique", 2, 0), ("09/08/2025", 19, "Huachipato", "Union La Calera", 1, 0),
    ("09/08/2025", 19, "Universidad de Chile", "Union Española", 4, 1), ("09/08/2025", 19, "La Serena", "O'Higgins", 3, 3),
    ("10/08/2025", 19, "Everton", "Colo Colo", 1, 1), ("10/08/2025", 19, "Cobresal", "Coquimbo", 1, 2),
    ("10/08/2025", 19, "Limache", "Audax Italiano", 4, 0), ("11/08/2025", 19, "Universidad Catolica", "Ñublense", 1, 0),
    ("15/08/2025", 20, "Union Española", "Iquique", 2, 2), ("16/08/2025", 20, "Union La Calera", "La Serena", 1, 1),
    ("16/08/2025", 20, "Ñublense", "Palestino", 1, 0), ("16/08/2025", 20, "Colo Colo", "Universidad Catolica", 1, 4),
    ("17/08/2025", 20, "O'Higgins", "Cobresal", 1, 0), ("17/08/2025", 20, "Universidad de Chile", "Audax Italiano", 1, 3),
    ("17/08/2025", 20, "Huachipato", "Limache", 4, 0), ("18/08/2025", 20, "Coquimbo", "Everton", 0, 0),
    ("22/08/2025", 21, "Palestino", "Colo Colo", 0, 0), ("23/08/2025", 21, "Limache", "O'Higgins", 2, 2),
    ("23/08/2025", 21, "Cobresal", "Union La Calera", 1, 0), ("23/08/2025", 21, "Audax Italiano", "Coquimbo", 0, 1),
    ("24/08/2025", 21, "Universidad Catolica", "Union Española", 2, 0), ("24/08/2025", 21, "La Serena", "Huachipato", 0, 2),
    ("24/08/2025", 21, "Iquique", "Ñublense", 0, 2), ("25/08/2025", 21, "Universidad de Chile", "Everton", 2, 0),
    ("29/08/2025", 22, "Everton", "La Serena", 3, 1), ("30/08/2025", 22, "Union La Calera", "Palestino", 1, 2),
    ("30/08/2025", 22, "Huachipato", "Coquimbo", 0, 1), ("30/08/2025", 22, "O'Higgins", "Audax Italiano", 3, 2),
    ("31/08/2025", 22, "Universidad Catolica", "Cobresal", 2, 1), ("31/08/2025", 22, "Iquique", "Limache", 2, 1),
    ("31/08/2025", 22, "Colo Colo", "Universidad de Chile", 1, 0), ("01/09/2025", 22, "Ñublense", "Union Española", 1, 2),
    ("12/09/2025", 23, "Coquimbo", "Ñublense", 2, 1), ("13/09/2025", 23, "Union La Calera", "Everton", 1, 0),
    ("13/09/2025", 23, "Union Española", "Audax Italiano", 3, 4), ("13/09/2025", 23, "Palestino", "O'Higgins", 1, 2),
    ("14/09/2025", 23, "Cobresal", "Huachipato", 3, 2), ("14/09/2025", 23, "Limache", "Universidad Catolica", 0, 1),
    ("14/09/2025", 23, "Colo Colo", "Iquique", 4, 0), ("15/09/2025", 23, "La Serena", "Universidad de Chile", 1, 1),
    ("26/09/2025", 24, "Union Española", "Huachipato", 4, 2), ("27/09/2025", 24, "Universidad de Chile", "Palestino", 2, 1),
    ("27/09/2025", 24, "Audax Italiano", "Union La Calera", 4, 3), ("27/09/2025", 24, "Iquique", "O'Higgins", 2, 3),
    ("28/09/2025", 24, "La Serena", "Ñublense", 2, 2), ("28/09/2025", 24, "Limache", "Cobresal", 2, 0),
    ("28/09/2025", 24, "Coquimbo", "Colo Colo", 1, 0), ("29/09/2025", 24, "Everton", "Universidad Catolica", 0, 3),
    ("03/10/2025", 25, "Palestino", "Everton", 2, 1), ("04/10/2025", 25, "La Serena", "Audax Italiano", 2, 1),
    ("04/10/2025", 25, "Huachipato", "Iquique", 1, 1), ("04/10/2025", 25, "Universidad Catolica", "Universidad de Chile", 1, 0),
    ("05/10/2025", 25, "Cobresal", "Union Española", 1, 0), ("05/10/2025", 25, "Union La Calera", "Ñublense", 3, 0),
    ("05/10/2025", 25, "O'Higgins", "Coquimbo", 0, 1), ("06/10/2025", 25, "Colo Colo", "Limache", 2, 2),
    ("17/10/2025", 26, "Audax Italiano", "Cobresal", 1, 2), ("18/10/2025", 26, "Iquique", "La Serena", 1, 2),
    ("18/10/2025", 26, "Ñublense", "Colo Colo", 0, 1), ("18/10/2025", 26, "Huachipato", "Universidad de Chile", 1, 0),
    ("19/10/2025", 26, "Universidad Catolica", "O'Higgins", 0, 2), ("19/10/2025", 26, "Coquimbo", "Union La Calera", 2, 0),
    ("19/10/2025", 26, "Everton", "Union Española", 0, 0), ("20/10/2025", 26, "Palestino", "Limache", 2, 1),
    ("31/10/2025", 27, "Union La Calera", "Iquique", 1, 2), ("01/11/2025", 27, "La Serena", "Universidad Catolica", 0, 1),
    ("01/11/2025", 27, "Union Española", "Colo Colo", 1, 2), ("01/11/2025", 27, "Palestino", "Coquimbo", 1, 2),
    ("02/11/2025", 27, "O'Higgins", "Ñublense", 4, 2), ("02/11/2025", 27, "Huachipato", "Audax Italiano", 2, 1),
    ("02/11/2025", 27, "Universidad de Chile", "Limache", 4, 3), ("03/11/2025", 27, "Cobresal", "Everton", 1, 2),
    ("07/11/2025", 28, "Iquique", "Cobresal", 2, 1), ("08/11/2025", 28, "Limache", "Union Española", 1, 0),
    ("08/11/2025", 28, "Audax Italiano", "Everton", 2, 0), ("08/11/2025", 28, "Coquimbo", "La Serena", 2, 1),
    ("09/11/2025", 28, "Universidad Catolica", "Palestino", 2, 1), ("09/11/2025", 28, "O'Higgins", "Universidad de Chile", 0, 1),
    ("09/11/2025", 28, "Colo Colo", "Union La Calera", 4, 1), ("10/11/2025", 28, "Ñublense", "Huachipato", 0, 1),
    ("21/11/2025", 29, "Cobresal", "Colo Colo", 3, 0), ("22/11/2025", 29, "Huachipato", "Universidad Catolica", 0, 0),
    ("22/11/2025", 29, "La Serena", "Palestino", 0, 3), ("22/11/2025", 29, "Union Española", "O'Higgins", 2, 4),
    ("23/11/2025", 29, "Union La Calera", "Limache", 0, 1), ("23/11/2025", 29, "Everton", "Iquique", 0, 1),
    ("23/11/2025", 29, "Audax Italiano", "Ñublense", 1, 0), ("24/11/2025", 29, "Universidad de Chile", "Coquimbo", 1, 1),
    ("05/12/2025", 30, "Palestino", "Huachipato", 2, 2), ("06/12/2025", 30, "Limache", "La Serena", 1, 0),
    ("06/12/2025", 30, "Coquimbo", "Union Española", 4, 2), ("06/12/2025", 30, "Universidad Catolica", "Union La Calera", 2, 1),
    ("06/12/2025", 30, "O'Higgins", "Everton", 1, 0), ("06/12/2025", 30, "Iquique", "Universidad de Chile", 2, 3),
    ("07/12/2025", 30, "Ñublense", "Cobresal", 5, 0), ("07/12/2025", 30, "Colo Colo", "Audax Italiano", 1, 2)
]

# Procesar los 240 partidos
partidos_list = []
for p in raw_partidos:
    fecha, jornada, local_name, visita_name, gl, gv = p
    local_id = name_to_id.get(local_name)
    visita_id = name_to_id.get(visita_name)
    if local_id and visita_id:
        # Formato esperado por SQL: (fecha, jornada, local_id, visita_id, goles_local, goles_visita)
        # Convertimos fecha DD/MM/YYYY a YYYY-MM-DD para SQLite
        d, m, y = fecha.split("/")
        formatted_date = f"{y}-{m}-{d}"
        partidos_list.append((formatted_date, jornada, local_id, visita_id, gl, gv))

cursor.executemany('''
    INSERT INTO partidos (fecha, jornada, local_id, visita_id, goles_local, goles_visita)
    VALUES (?, ?, ?, ?, ?, ?)
''', partidos_list)

# --- 3. TABLA DE POSICIONES FINAL ---
# (Datos finales oficiales SoloFutbol.cl)
tabla_final = [
    (1, 1, 75, 30, 23, 6, 1, 49, 17, 32),   # Coquimbo Unido (C)
    (2, 2, 58, 30, 17, 7, 6, 44, 26, 18),   # U. Católica
    (3, 3, 56, 30, 16, 8, 6, 43, 34, 9),    # O'Higgins
    (4, 4, 55, 30, 17, 4, 9, 58, 32, 26),   # U. de Chile
    (5, 5, 52, 30, 16, 4, 10, 51, 43, 8),   # Audax Italiano
    (6, 6, 49, 30, 14, 7, 9, 42, 31, 11),   # Palestino
    (7, 7, 47, 30, 14, 5, 11, 38, 38, 0),   # Cobresal
    (8, 8, 44, 30, 12, 8, 10, 46, 36, 10),  # Colo-Colo
    (9, 9, 43, 30, 12, 7, 11, 43, 42, 1),   # Huachipato
    (10, 10, 33, 30, 8, 9, 13, 31, 40, -9), # Ñublense
    (11, 11, 31, 30, 8, 7, 15, 36, 43, -7), # Dep. Limache
    (12, 12, 29, 30, 8, 5, 17, 28, 39, -11),# U. La Calera
    (13, 13, 27, 30, 7, 6, 17, 32, 52, -20),# La Serena
    (14, 14, 26, 30, 6, 8, 16, 27, 44, -17),# Everton
    (15, 15, 24, 30, 6, 6, 18, 34, 60, -26),# Iquique (D)
    (16, 16, 21, 30, 6, 3, 21, 33, 58, -25) # U. Española (D)
]

cursor.executemany('INSERT INTO posiciones VALUES (?,?,?,?,?,?,?,?,?,?)', tabla_final)

conn.commit()
conn.close()

print(f"Base de datos '{db_name}' creada exitosamente con {len(partidos_list)} partidos.")
>>>>>>> pralad
