import sqlite3

def alter_table():
    conn = sqlite3.connect("inspections.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE admin_logs ADD COLUMN admin TEXT;")
        conn.commit()
        print("Coluna 'admin' adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        print("Erro ao alterar a tabela:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    alter_table()
