from config import conectar, DB_DRIVER

# =====================================================
#  CONEXÃO COM O BANCO DE DADOS (Multi-DB)
# =====================================================

class Database:
    @staticmethod
    def conectar_banco():
        """
        Cria e retorna uma conexão usando a factory do config.py.
        """
        return conectar()

    @staticmethod
    def executar_consulta(sql, parametros=None, retornar_dados=True):
        """
        Executa uma query SQL e retorna os resultados.

        Se retornar_dados=True, retorna lista de dicionários.
        Se retornar_dados=False, retorna o número de linhas afetadas.
        """
        conexao = None
        cursor = None

        try:
            conexao = Database.conectar_banco()
            
            # MySQL precisa de dictionary=True para retornar dicts, SQLite e SQL Server não têm esse parâmetro.
            if DB_DRIVER == "mysql":
                cursor = conexao.cursor(dictionary=True)
            else:
                cursor = conexao.cursor()

            # Substituir os %s do MySQL por ? para SQLite e SQL Server se necessário
            if DB_DRIVER in ["sqlite", "mssql"] and "%s" in sql:
                sql = sql.replace("%s", "?")

            cursor.execute(sql, parametros or ())

            if retornar_dados:
                resultado = cursor.fetchall()
                
                # Converter resultados para lista de dicionários se não for MySQL
                if DB_DRIVER == "sqlite":
                    resultado = [dict(row) for row in resultado]
                elif DB_DRIVER == "mssql":
                    colunas = [column[0] for column in cursor.description]
                    resultado = [dict(zip(colunas, row)) for row in resultado]
                    
                return resultado
            else:
                conexao.commit()
                return cursor.rowcount

        except Exception as erro:
            print(f"[ERRO DB] {erro}")
            raise

        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()
