#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import psycopg2

# Lee el archivo SQL
with open('backup_data.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# URL de BD de Heroku
database_url = 'postgres://ufkqgihgtmf9gh:p16f4b1e1de6922a852082849fbd9570a559d11c945dfe49e9e38448da01b8f40@c2rdrhpl0th9dp.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d84pqknkl0g6hs'

# Conecta a la BD
try:
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    # Divide por puntos y coma, ignorando comentarios y líneas vacías
    statements = []
    for line in sql_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        statements.append(line)

    # Une las líneas de nuevo
    full_sql = ' '.join(statements)

    # Divide por punto y coma
    queries = [q.strip() for q in full_sql.split(';') if q.strip()]

    print(f"Total de sentencias: {len(queries)}\n")

    for i, query in enumerate(queries, 1):
        try:
            print(f"[{i}/{len(queries)}] Ejecutando...", end=" ")
            cur.execute(query)
            conn.commit()
            print("OK")
        except Exception as e:
            print(f"ERROR: {e}")
            conn.rollback()

    print("\n=== Datos cargados exitosamente en Heroku ===")

except psycopg2.Error as e:
    print(f"Error de conexión: {e}")
    sys.exit(1)

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
