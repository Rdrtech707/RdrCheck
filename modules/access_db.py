# RdrCheck/modules/access_db.py
import pyodbc
import pandas as pd

def get_connection(mdb_file: str, password: str):
    """
    Cria uma conexão com o banco de dados .mdb usando o driver do Access.
    Certifique-se de que o driver "Microsoft Access Driver (*.mdb, *.accdb)" esteja instalado.
    """
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=" + mdb_file + ";"
        r"PWD=" + password + ";"
    )
    return pyodbc.connect(conn_str)

def fetch_ordems_by_modelo(mdb_file: str, password: str, modelo: str) -> pd.DataFrame:
    """
    Lê a tabela ORDEMS buscando registros onde MODELO não é nulo e, em Python, filtra
    aqueles cujo MODELO normalizado (sem hífens, espaços e em minúsculas) seja igual a 'modelo'.
    Retorna um DataFrame com as colunas CODIGO, SAIDA, SITUACAO, MODELO e KILOMET.
    """
    conn = get_connection(mdb_file, password)
    query = """
    SELECT CODIGO, SAIDA, SITUACAO, MODELO, KILOMET 
    FROM ORDEMS 
    WHERE MODELO IS NOT NULL
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Normaliza a coluna MODELO e filtra os registros conforme o valor informado
    df['MODELO_NORMALIZADO'] = df['MODELO'].apply(
        lambda x: x.replace('-', '').replace(' ', '').lower() if isinstance(x, str) else ''
    )
    df = df[df['MODELO_NORMALIZADO'] == modelo]
    return df

def fetch_os_pecas_by_cod(mdb_file: str, password: str, cod_os: str) -> pd.DataFrame:
    """
    Lê a tabela OS_PECAS filtrando pelo COD_OS informado e retorna um DataFrame
    com as colunas DESCRICAO, QTD e COD_OS.
    """
    conn = get_connection(mdb_file, password)
    query = "SELECT DESCRICAO, QTD, COD_OS FROM OS_PECAS WHERE COD_OS = ?"
    df = pd.read_sql(query, conn, params=[cod_os])
    conn.close()
    return df

def fetch_os_servicos_by_osnum(mdb_file: str, password: str, os_num: str) -> pd.DataFrame:
    """
    Lê a tabela OS_SERVICOS filtrando pelo OS_NUM informado e retorna um DataFrame
    com as colunas DESCRICAO e OS_NUM.
    """
    conn = get_connection(mdb_file, password)
    query = "SELECT DESCRICAO, OS_NUM FROM OS_SERVICOS WHERE OS_NUM = ?"
    df = pd.read_sql(query, conn, params=[os_num])
    conn.close()
    return df
