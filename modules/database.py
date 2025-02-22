# modules/database.py
import sqlite3
import os
import json

# Nome do arquivo de banco de dados (será criado na raiz do projeto)
DB_NAME = "inspections.db"

def get_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Permite acessar as colunas pelo nome
    return conn

def init_db():
    """Cria as tabelas necessárias se elas não existirem.
    *Não* insere automaticamente o usuário admin, permitindo sua exclusão definitiva.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Tabela de inspeções
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            km TEXT NOT NULL,
            items TEXT,
            observacoes TEXT,
            mecanico TEXT,
            pdf_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')
    # Tabela de logs de ações administrativas com coluna "admin"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT,
            admin TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_inspection(placa, km, items, observacoes, mecanico, pdf_path):
    """
    Insere um registro de inspeção no banco de dados.
    Armazena o dicionário de itens como uma string JSON.
    Retorna o ID da inspeção inserida.
    """
    conn = get_connection()
    cursor = conn.cursor()
    items_json = json.dumps(items)
    cursor.execute('''
        INSERT INTO inspections (placa, km, items, observacoes, mecanico, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (placa, km, items_json, observacoes, mecanico, pdf_path))
    conn.commit()
    inspection_id = cursor.lastrowid
    conn.close()
    return inspection_id

# FUNÇÕES PARA GERENCIAR PLACAS E USUÁRIOS

def get_distinct_plates():
    """
    Retorna uma lista com todas as placas distintas registradas na tabela de inspeções.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT placa FROM inspections")
    rows = cursor.fetchall()
    conn.close()
    return [row["placa"] for row in rows]

def delete_inspections_by_plate(plate):
    """
    Exclui todos os registros da tabela de inspeções que possuem a placa especificada (case-insensitive).
    Retorna o número de registros excluídos.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inspections WHERE LOWER(placa) = LOWER(?)", (plate,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count

def get_all_users():
    """
    Retorna uma lista de usuários cadastrados no banco de dados.
    Cada usuário é representado por um dicionário: {"username": ..., "role": ...}.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [{"username": row["username"], "role": row["role"]} for row in rows]

def update_user_credentials(old_username, new_username, new_password):
    """
    Atualiza as credenciais do usuário no banco de dados.
    Retorna o número de registros atualizados (1 se sucesso, 0 se falhar).
    Agora permite alterar o usuário 'admin'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET username = ?, password = ? WHERE username = ?",
            (new_username, new_password, old_username)
        )
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        return 0
    finally:
        conn.close()

# FUNÇÕES PARA REGISTROS (LOGS) DE AÇÕES ADMINISTRATIVAS

def log_admin_action(action, details, admin_user):
    """
    Registra uma ação administrativa no banco de dados com data e horário,
    incluindo o administrador que executou a ação.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admin_logs (action, details, admin) VALUES (?, ?, ?)",
                   (action, details, admin_user))
    conn.commit()
    conn.close()

def get_admin_logs():
    """
    Retorna todos os registros de ações administrativas em ordem decrescente de data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return logs
