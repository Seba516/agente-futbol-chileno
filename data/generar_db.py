import pandas as pd
import sqlite3
import os

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