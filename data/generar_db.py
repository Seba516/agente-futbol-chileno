import sqlite3
import os

# Nombre de la base de datos
db_name = "campeonato_nacional_2025.db"

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

# Equipos (IDs basados en orden alfabético o relevancia para facilitar inserción)
equipos = [
    (1, 'Coquimbo Unido', 'Coquimbo', 'Francisco Sánchez Rumoroso'),
    (2, 'Universidad Católica', 'Santiago', 'San Carlos de Apoquindo'),
    (3, 'O\'Higgins', 'Rancagua', 'El Teniente'),
    (4, 'Universidad de Chile', 'Santiago', 'Nacional'),
    (5, 'Audax Italiano', 'Santiago', 'Bicentenario de La Florida'),
    (6, 'Palestino', 'Santiago', 'Municipal de La Cisterna'),
    (7, 'Cobresal', 'El Salvador', 'El Cobre'),
    (8, 'Colo-Colo', 'Santiago', 'Monumental'),
    (9, 'Huachipato', 'Talcahuano', 'Huachipato-CAP'),
    (10, 'Ñublense', 'Chillán', 'Nelson Oyarzún'),
    (11, 'Deportes Limache', 'Limache', 'Nicolás Chahuán'),
    (12, 'Unión La Calera', 'La Calera', 'Nicolás Chahuán'),
    (13, 'Deportes La Serena', 'La Serena', 'La Portada'),
    (14, 'Everton', 'Viña del Mar', 'Sausalito'),
    (15, 'Deportes Iquique', 'Iquique', 'Tierra de Campeones'),
    (16, 'Unión Española', 'Santiago', 'Santa Laura')
]

cursor.executemany('INSERT INTO equipos VALUES (?,?,?,?)', equipos)

# Resultados destacados de la Temporada 2025
# Se incluyen Fecha 1 (Apertura) y Fecha 30 (Cierre/Definición) como muestra representativa
partidos = [
    # --- FECHA 1 (Inicio 14-16 Feb) ---
    ('2025-02-14', 1, 15, 1, 0, 3), # Iquique 0-3 Coquimbo
    ('2025-02-15', 1, 6, 7, 2, 1),  # Palestino 2-1 Cobresal
    ('2025-02-15', 1, 3, 9, 0, 0),  # O'Higgins 0-0 Huachipato
    ('2025-02-15', 1, 4, 10, 5, 0), # U. de Chile 5-0 Ñublense
    ('2025-02-16', 1, 13, 8, 1, 3), # La Serena 1-3 Colo Colo
    ('2025-02-16', 1, 11, 14, 1, 1),# Limache 1-1 Everton
    ('2025-02-17', 1, 2, 5, 3, 1),  # U. Católica 3-1 Audax
    ('2025-02-17', 1, 12, 16, 4, 0),# La Calera 4-0 U. Española

    # --- FECHA 3 (Feb/Mar) ---
    ('2025-02-28', 3, 11, 1, 1, 2), # Limache 1-2 Coquimbo
    ('2025-03-02', 3, 9, 8, 2, 1),  # Huachipato 2-1 Colo Colo

    # --- FECHA 30 (Definición 6-7 Dic) ---
    ('2025-12-06', 30, 6, 9, 2, 2), # Palestino 2-2 Huachipato
    ('2025-12-06', 30, 15, 4, 2, 3),# Iquique 2-3 U. de Chile
    ('2025-12-06', 30, 1, 16, 4, 2),# Coquimbo 4-2 U. Española (CAMPEÓN)
    ('2025-12-06', 30, 11, 13, 1, 0),# Limache 1-0 La Serena
    ('2025-12-06', 30, 3, 14, 1, 0),# O'Higgins 1-0 Everton
    ('2025-12-06', 30, 2, 12, 2, 1),# U. Católica 2-1 La Calera
    ('2025-12-07', 30, 8, 5, 1, 2), # Colo Colo 1-2 Audax
    ('2025-12-07', 30, 10, 7, 5, 0) # Ñublense 5-0 Cobresal
]

cursor.executemany('''
    INSERT INTO partidos (fecha, jornada, local_id, visita_id, goles_local, goles_visita)
    VALUES (?, ?, ?, ?, ?, ?)
''', partidos)

# Tabla de Posiciones Final (Datos reales temporada 2025)
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

print(f"Base de datos '{db_name}' creada exitosamente.")