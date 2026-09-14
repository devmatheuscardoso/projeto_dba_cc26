import os
import sys

# =====================================================================
#  LOADER DE VARIÁVEIS DE AMBIENTE (.env)
# =====================================================================
def carregar_env():
    _env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(_env_path):
        with open(_env_path, 'r', encoding='utf-8-sig') as _f:
            for _linha in _f:
                _linha = _linha.strip()
                if _linha and not _linha.startswith('#') and '=' in _linha:
                    _chave, _valor = _linha.split('=', 1)
                    os.environ[_chave.strip()] = _valor.strip()

carregar_env()

PORTA_SERVIDOR = int(os.getenv("PORTA_SERVIDOR", "8080"))
DB_DRIVER = os.getenv("DB_DRIVER", "mysql").lower()

def conectar():
    carregar_env()
    driver = os.getenv("DB_DRIVER", "mysql").lower()

    if driver == "mysql":
        try:
            import mysql.connector
        except ImportError:
            sys.exit("[ERRO] mysql-connector-python não instalado. Execute: pip install mysql-connector-python")

        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "")
        database = os.getenv("MYSQL_DATABASE", "controle_funcionarios")

        return mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
        )

    elif driver == "sqlite":
        import sqlite3
        sqlite_file = os.getenv("SQLITE_FILE", os.path.join(os.path.dirname(__file__), "controle_funcionarios.db"))
        conn = sqlite3.connect(sqlite_file)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    elif driver == "mssql":
        try:
            import pyodbc
        except ImportError:
            sys.exit("[ERRO] pyodbc não instalado. Execute: pip install pyodbc")

        server = os.getenv("MSSQL_SERVER", "localhost")
        port = os.getenv("MSSQL_PORT", "1433")
        user = os.getenv("MSSQL_USER", "sa")
        password = os.getenv("MSSQL_PASSWORD", "")
        database = os.getenv("MSSQL_DATABASE", "controle_funcionarios")
        driver_name = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")

        conn_str = (
            f"DRIVER={{{driver_name}}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
        )
        return pyodbc.connect(conn_str)

    else:
        sys.exit(f"[ERRO] DB_DRIVER inválido: '{driver}'. Use: mysql, sqlite ou mssql.")
