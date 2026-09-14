import re
from utils import formatar_cpf, validar_cpf
from config import DB_DRIVER
from database import Database

class MovimentacaoController:

    @staticmethod
    def listar_retiradas_usuario(parametros):
        cpf = parametros.get("cpf", [""])[0].strip()
        matricula = parametros.get("matricula", [""])[0].strip()
        funcionario_id = parametros.get("funcionario_id", [""])[0].strip()

        termo = cpf or matricula or funcionario_id

        if not termo:
            return {"sucesso": False, "mensagem": "Informe o CPF ou Matrícula do funcionário."}, 400

        cpf_fmt = formatar_cpf(cpf) if validar_cpf(cpf) else cpf
        cpf_num = re.sub(r"\D", "", cpf) if cpf else ""

        try:
            sql = """
                SELECT ir.id as item_retirada_id, e.id as epi_id, e.nome, e.codigo, ir.quantidade, r.data_retirada
                FROM itens_retirada ir
                JOIN retiradas r ON ir.retirada_id = r.id
                JOIN epis e ON ir.epi_id = e.id
                JOIN funcionarios f ON r.funcionario_id = f.id
                WHERE (f.cpf = %s OR REPLACE(REPLACE(f.cpf, '.', ''), '-', '') = %s OR f.matricula = %s OR f.id = %s) 
                  AND ir.status = 'RETIRADO'
                ORDER BY r.data_retirada DESC
            """
            resultado = Database.executar_consulta(sql, (cpf_fmt, cpf_num if cpf_num else termo, termo, termo))
            return {"sucesso": True, "itens": resultado}, 200
        except Exception as e:
            print(f"[ERRO LISTAR RETIRADAS] {e}")
            return {"sucesso": False, "mensagem": "Erro ao buscar retiradas pendentes."}, 500


    @staticmethod
    def registrar_retirada(dados):
        cpf = dados.get("cpf", "").strip()
        matricula = dados.get("matricula", "").strip()
        funcionario_id = dados.get("funcionario_id")
        itens = dados.get("itens", [])

        termo = cpf or matricula or funcionario_id

        if not termo or not itens:
            return {"sucesso": False, "mensagem": "Dados inválidos."}, 400

        cpf_fmt = formatar_cpf(cpf) if validar_cpf(cpf) else cpf
        cpf_num = re.sub(r"\D", "", cpf) if cpf else ""

        conexao = None
        cursor = None

        try:
            conexao = Database.conectar_banco()
            
            if DB_DRIVER == "mysql":
                cursor = conexao.cursor(dictionary=True)
            else:
                cursor = conexao.cursor()

            # Busca ID do funcionário e verifica se está ativo
            q_user = "SELECT id, ativo FROM funcionarios WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s OR matricula = %s OR id = %s)"
            if DB_DRIVER in ["sqlite", "mssql"]: q_user = q_user.replace("%s", "?")
            cursor.execute(q_user, (cpf_fmt, cpf_num if cpf_num else termo, termo, termo))
            user_raw = cursor.fetchone()

            if not user_raw:
                return {"sucesso": False, "mensagem": "Funcionário não encontrado."}, 404

            if DB_DRIVER == "mysql":
                user_id = user_raw["id"]
                ativo = user_raw["ativo"]
            elif DB_DRIVER == "sqlite":
                user_id = user_raw["id"]
                ativo = user_raw["ativo"]
            else:
                colunas = [c[0] for c in cursor.description]
                u_dict = dict(zip(colunas, user_raw))
                user_id = u_dict["id"]
                ativo = u_dict["ativo"]

            if ativo == 0:
                return {"sucesso": False, "mensagem": "Funcionário inativo."}, 400

            # Registra retirada vinculando funcionario_id
            q_ret = "INSERT INTO retiradas (funcionario_id) VALUES (%s)"
            if DB_DRIVER in ["sqlite", "mssql"]: q_ret = q_ret.replace("%s", "?")
            cursor.execute(q_ret, (user_id,))
            
            if DB_DRIVER == "mssql":
                cursor.execute("SELECT @@IDENTITY")
                retirada_id = cursor.fetchone()[0]
            else:
                retirada_id = cursor.lastrowid

            for item in itens:
                epi_id = item.get("epi_id")
                qtd = int(item.get("quantidade", 0))
                if qtd > 0:
                    q_estoque = "SELECT quantidade FROM epis WHERE id = %s"
                    if DB_DRIVER in ["sqlite", "mssql"]: q_estoque = q_estoque.replace("%s", "?")
                    cursor.execute(q_estoque, (epi_id,))
                    est_raw = cursor.fetchone()
                    estoque_atual = est_raw[0] if isinstance(est_raw, tuple) else (est_raw["quantidade"] if isinstance(est_raw, dict) else est_raw[0])
                    
                    if estoque_atual < qtd:
                        raise Exception(f"Estoque insuficiente para o EPI ID {epi_id}.")
                    
                    q_ins = "INSERT INTO itens_retirada (retirada_id, epi_id, quantidade, status) VALUES (%s, %s, %s, 'RETIRADO')"
                    if DB_DRIVER in ["sqlite", "mssql"]: q_ins = q_ins.replace("%s", "?")
                    cursor.execute(q_ins, (retirada_id, epi_id, qtd))
                    
                    q_upd = "UPDATE epis SET quantidade = quantidade - %s WHERE id = %s"
                    if DB_DRIVER in ["sqlite", "mssql"]: q_upd = q_upd.replace("%s", "?")
                    cursor.execute(q_upd, (qtd, epi_id))

            conexao.commit()
            return {"sucesso": True, "mensagem": "Retirada registrada com sucesso!"}, 200

        except Exception as e:
            if conexao: conexao.rollback()
            print(f"[ERRO REGISTRAR RETIRADA] {e}")
            return {"sucesso": False, "mensagem": str(e)}, 500
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()


    @staticmethod
    def registrar_devolucao(dados):
        item_retirada_id = dados.get("item_retirada_id")
        qtd_devolvida = int(dados.get("quantidade", 0))

        if not item_retirada_id or qtd_devolvida <= 0:
            return {"sucesso": False, "mensagem": "Dados inválidos."}, 400

        conexao = None
        cursor = None

        try:
            conexao = Database.conectar_banco()
            
            if DB_DRIVER == "mysql":
                cursor = conexao.cursor(dictionary=True)
            else:
                cursor = conexao.cursor()

            q_item = "SELECT epi_id, quantidade, status FROM itens_retirada WHERE id = %s"
            if DB_DRIVER in ["sqlite", "mssql"]: q_item = q_item.replace("%s", "?")
            cursor.execute(q_item, (item_retirada_id,))
            item_raw = cursor.fetchone()

            if not item_raw:
                return {"sucesso": False, "mensagem": "Item de retirada não encontrado."}, 404
            
            if DB_DRIVER == "mysql":
                item = item_raw
            elif DB_DRIVER == "sqlite":
                item = dict(item_raw)
            else:
                colunas = [column[0] for column in cursor.description]
                item = dict(zip(colunas, item_raw))

            if item["status"] == "DEVOLVIDO":
                return {"sucesso": False, "mensagem": "Este item já foi totalmente devolvido."}, 400

            qtd_original = item["quantidade"]
            epi_id = item["epi_id"]

            if qtd_devolvida > qtd_original:
                return {"sucesso": False, "mensagem": "Quantidade devolvida maior que a retirada."}, 400

            if qtd_devolvida == qtd_original:
                q_upd_status = "UPDATE itens_retirada SET status = 'DEVOLVIDO', data_devolucao = CURRENT_TIMESTAMP WHERE id = %s"
                if DB_DRIVER in ["sqlite", "mssql"]: q_upd_status = q_upd_status.replace("%s", "?")
                cursor.execute(q_upd_status, (item_retirada_id,))
            else:
                nova_qtd_pendente = qtd_original - qtd_devolvida
                q_upd_qtd = "UPDATE itens_retirada SET quantidade = %s WHERE id = %s"
                if DB_DRIVER in ["sqlite", "mssql"]: q_upd_qtd = q_upd_qtd.replace("%s", "?")
                cursor.execute(q_upd_qtd, (nova_qtd_pendente, item_retirada_id))
                
                q_sel_ret = "SELECT retirada_id FROM itens_retirada WHERE id = %s"
                if DB_DRIVER in ["sqlite", "mssql"]: q_sel_ret = q_sel_ret.replace("%s", "?")
                cursor.execute(q_sel_ret, (item_retirada_id,))
                
                ret_raw = cursor.fetchone()
                retirada_id = ret_raw["retirada_id"] if DB_DRIVER == "mysql" else (dict(ret_raw)["retirada_id"] if DB_DRIVER == "sqlite" else dict(zip([c[0] for c in cursor.description], ret_raw))["retirada_id"])
                
                q_ins_dev = "INSERT INTO itens_retirada (retirada_id, epi_id, quantidade, status, data_devolucao) VALUES (%s, %s, %s, 'DEVOLVIDO', CURRENT_TIMESTAMP)"
                if DB_DRIVER in ["sqlite", "mssql"]: q_ins_dev = q_ins_dev.replace("%s", "?")
                cursor.execute(q_ins_dev, (retirada_id, epi_id, qtd_devolvida))

            q_upd_est = "UPDATE epis SET quantidade = quantidade + %s WHERE id = %s"
            if DB_DRIVER in ["sqlite", "mssql"]: q_upd_est = q_upd_est.replace("%s", "?")
            cursor.execute(q_upd_est, (qtd_devolvida, epi_id))

            conexao.commit()
            return {"sucesso": True, "mensagem": "Devolução registrada com sucesso!"}, 200

        except Exception as e:
            if conexao: conexao.rollback()
            print(f"[ERRO REGISTRAR DEVOLUCAO] {e}")
            return {"sucesso": False, "mensagem": "Erro ao registrar devolução."}, 500
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()
