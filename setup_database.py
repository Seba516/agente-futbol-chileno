import sqlite3
import os

# Asegurar que la carpeta data existe
if not os.path.exists("data"):
    os.makedirs("data")

db_path = os.path.join("data", "futbol_chileno.db")

def create_database():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabla de Posiciones 2024 (Simulada para el ejercicio)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posiciones (
        id INTEGER PRIMARY KEY,
        equipo TEXT NOT NULL,
        puntos INTEGER,
        partidos_jugados INTEGER,
        ganados INTEGER,
        empatados INTEGER,
        perdidos INTEGER,
        diferencia_gol INTEGER
    )
    ''')

    # Datos: Equipo, Pts, PJ, PG, PE, PP, DIF
    equipos = [
        (1, 'Colo-Colo', 60, 28, 19, 3, 6, 25),
        (2, 'Universidad de Chile', 58, 28, 17, 7, 4, 20),
        (3, 'Universidad Catolica', 45, 28, 13, 6, 9, 10),
        (4, 'Deportes Iquique', 42, 28, 12, 6, 10, 5),
        (5, 'Union Espanola', 40, 28, 11, 7, 10, 2)
    ]

    cursor.executemany('INSERT OR REPLACE INTO posiciones VALUES (?,?,?,?,?,?,?,?)', equipos)
    conn.commit()
    conn.close()
    print(f"✅ Base de datos creada en: {db_path}")

if __name__ == "__main__":
    create_database()