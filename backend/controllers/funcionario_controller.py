import re
from database import Database
from utils import validar_cpf, formatar_cpf

def gerar_descricao_profissao(nome_prof):
    nome_lower = nome_prof.lower()
    if any(k in nome_lower for k in ["softw", "dev", "programad", "sistem", "ti", "computa", "analista de ti"]):
        return "Atividades de Tecnologia da Informação e Desenvolvimento de Software"
    elif any(k in nome_lower for k in ["engenhe", "engenha"]):
        return "Atividades de Engenharia, Planejamento e Projetos Técnicos"
    elif any(k in nome_lower for k in ["operad", "produ", "auxiliar de produ"]):
        return "Responsável por atividades relacionadas à produção"
    elif any(k in nome_lower for k in ["seguran", "tst", "prevenc"]):
        return "Responsável pelas atividades de segurança do trabalho"
    elif any(k in nome_lower for k in ["manuten", "mecân", "mecan", "elétr", "eletr", "técnico"]):
        return "Responsável pela manutenção de máquinas e equipamentos"
    elif any(k in nome_lower for k in ["almoxar", "estoq", "logíst", "logist", "expedi"]):
        return "Responsável pelo controle e armazenamento de materiais"
    elif any(k in nome_lower for k in ["supervis", "gerent", "coordenad", "líd", "lid", "diretor"]):
        return "Atividades de liderança, gestão e supervisão de equipe"
    elif any(k in nome_lower for k in ["admin", "rh", "recurs", "finan", "contáb", "secretár", "assistente"]):
        return "Atividades administrativas, financeiras e gestão de recursos"
    elif any(k in nome_lower for k in ["qualid", "auditor", "inspetor"]):
        return "Atividades de controle, garantia da qualidade e inspeção"
    elif any(k in nome_lower for k in ["venda", "comercia", "market", "atend"]):
        return "Atividades de vendas, atendimento comercial e relacionamento"
    elif any(k in nome_lower for k in ["enferm", "médic", "medic", "saúd", "saud", "socorr"]):
        return "Atividades de assistência à saúde e atendimento ambulatorial"
    else:
        return f"Atividades e responsabilidades pertinentes à profissão de {nome_prof}"

def obter_ou_criar_profissao(profissao_val):
    if not profissao_val:
        return None
    
    if isinstance(profissao_val, int) or (isinstance(profissao_val, str) and profissao_val.isdigit()):
        return int(profissao_val)

    nome_prof = str(profissao_val).strip()
    if not nome_prof:
        return None

    res = Database.executar_consulta("SELECT id FROM profissoes WHERE LOWER(nome) = LOWER(%s)", (nome_prof,))
    if res:
        return res[0]["id"]
    
    desc = gerar_descricao_profissao(nome_prof)
    Database.executar_consulta(
        "INSERT INTO profissoes (nome, descricao, ativo) VALUES (%s, %s, 1)",
        (nome_prof, desc),
        retornar_dados=False
    )
    
    res_novo = Database.executar_consulta("SELECT id FROM profissoes WHERE LOWER(nome) = LOWER(%s)", (nome_prof,))
    if res_novo:
        return res_novo[0]["id"]
    
    return None


class UsuarioController:
    
    @staticmethod
    def listar_usuarios(parametros):
        filtro = (
            parametros.get("busca", [""])[0] or
            parametros.get("nome", [""])[0] or
            parametros.get("cpf", [""])[0] or
            parametros.get("matricula", [""])[0]
        ).strip()

        try:
            if filtro:
                filtro_numeros = re.sub(r"\D", "", filtro)
                resultado = Database.executar_consulta(
                    """
                    SELECT f.id, f.matricula, f.nome, f.cpf, f.email, f.telefone, 
                           f.profissao_id, COALESCE(p.nome, '') AS profissao_nome, COALESCE(p.nome, '') AS profissao,
                           f.setor_id, COALESCE(s.nome, '') AS setor_nome, COALESCE(s.nome, '') AS setor
                    FROM funcionarios f
                    LEFT JOIN profissoes p ON f.profissao_id = p.id
                    LEFT JOIN setores s ON f.setor_id = s.id
                    WHERE (f.nome LIKE %s OR f.cpf LIKE %s OR f.matricula LIKE %s OR f.email LIKE %s OR REPLACE(REPLACE(f.cpf, '.', ''), '-', '') LIKE %s) 
                      AND f.ativo = 1 
                    ORDER BY f.nome
                    """,
                    (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro_numeros}%" if filtro_numeros else f"%{filtro}%")
                )
            else:
                resultado = Database.executar_consulta(
                    """
                    SELECT f.id, f.matricula, f.nome, f.cpf, f.email, f.telefone, 
                           f.profissao_id, COALESCE(p.nome, '') AS profissao_nome, COALESCE(p.nome, '') AS profissao,
                           f.setor_id, COALESCE(s.nome, '') AS setor_nome, COALESCE(s.nome, '') AS setor
                    FROM funcionarios f
                    LEFT JOIN profissoes p ON f.profissao_id = p.id
                    LEFT JOIN setores s ON f.setor_id = s.id
                    WHERE f.ativo = 1 
                    ORDER BY f.nome
                    """
                )

            return {"sucesso": True, "usuarios": resultado, "funcionarios": resultado}, 200

        except Exception as e:
            print(f"[ERRO LISTAR FUNCIONARIOS] {e}")
            return {"sucesso": False, "mensagem": "Erro ao consultar funcionários."}, 500


    @staticmethod
    def buscar_por_cpf(parametros):
        termo = (
            parametros.get("cpf", [""])[0] or 
            parametros.get("matricula", [""])[0] or 
            parametros.get("busca", [""])[0]
        ).strip()

        if not termo:
            return {"sucesso": False, "mensagem": "Informe o CPF ou Matrícula."}, 400

        termo_fmt = formatar_cpf(termo) if validar_cpf(termo) else termo
        termo_num = re.sub(r"\D", "", termo)

        try:
            resultado = Database.executar_consulta(
                """
                SELECT f.id, f.matricula, f.nome, f.cpf, f.email, f.telefone, 
                       f.profissao_id, COALESCE(p.nome, '') AS profissao_nome, COALESCE(p.nome, '') AS profissao,
                       f.setor_id, COALESCE(s.nome, '') AS setor_nome, COALESCE(s.nome, '') AS setor, f.ativo
                FROM funcionarios f
                LEFT JOIN profissoes p ON f.profissao_id = p.id
                LEFT JOIN setores s ON f.setor_id = s.id
                WHERE (f.cpf = %s OR REPLACE(REPLACE(f.cpf, '.', ''), '-', '') = %s OR f.matricula = %s)
                """,
                (termo_fmt, termo_num if termo_num else termo, termo)
            )

            if resultado:
                user = resultado[0]
                if user.get("ativo") == 1:
                    return {"sucesso": True, "usuario": user, "funcionario": user}, 200
                else:
                    return {
                        "sucesso": False,
                        "inativo": True,
                        "mensagem": "Funcionário encontrado, mas inativo. Deseja reativá-lo?",
                        "usuario": user,
                        "funcionario": user
                    }, 200
            else:
                return {"sucesso": False, "mensagem": "Funcionário não encontrado."}, 404

        except Exception as e:
            print(f"[ERRO BUSCAR FUNCIONARIO] {e}")
            return {"sucesso": False, "mensagem": "Erro ao buscar funcionário."}, 500


    @staticmethod
    def adicionar(dados):
        matricula = dados.get("matricula", "").strip()
        nome = dados.get("nome", "").strip()
        cpf = dados.get("cpf", "").strip()
        email = dados.get("email", "").strip()
        telefone = dados.get("telefone", "").strip()
        setor_id = dados.get("setor_id")

        profissao_input = dados.get("profissao") or dados.get("profissao_id")
        profissao_id = obter_ou_criar_profissao(profissao_input)

        if not setor_id and dados.get("setor"):
            set_res = Database.executar_consulta("SELECT id FROM setores WHERE nome = %s", (dados.get("setor").strip(),))
            if set_res: setor_id = set_res[0]["id"]

        if not nome or not cpf or not profissao_id or not setor_id:
            return {"sucesso": False, "mensagem": "Preencha todos os campos obrigatórios (Nome, CPF, Setor, Profissão)."}, 400

        if not validar_cpf(cpf):
            return {"sucesso": False, "mensagem": "CPF inválido. Verifique os números digitados."}, 400

        cpf_fmt = formatar_cpf(cpf)
        cpf_num = re.sub(r"\D", "", cpf)

        if not matricula:
            ult = Database.executar_consulta("SELECT MAX(id) as max_id FROM funcionarios")
            prox_id = (ult[0]["max_id"] or 0) + 1 if ult else 1
            matricula = f"FUNC-{prox_id:03d}"

        if not email:
            email = f"{cpf_num}@empresa.com"

        try:
            existente = Database.executar_consulta(
                """
                SELECT f.id, f.matricula, f.nome, f.cpf, f.email, f.telefone, 
                       f.profissao_id, COALESCE(p.nome, '') AS profissao_nome, f.setor_id, COALESCE(s.nome, '') AS setor_nome, f.ativo 
                FROM funcionarios f
                LEFT JOIN profissoes p ON f.profissao_id = p.id
                LEFT JOIN setores s ON f.setor_id = s.id
                WHERE (f.cpf = %s OR REPLACE(REPLACE(f.cpf, '.', ''), '-', '') = %s OR f.matricula = %s OR f.email = %s)
                """,
                (cpf_fmt, cpf_num, matricula, email)
            )

            if existente:
                user = existente[0]
                if user.get("ativo") == 1:
                    return {"sucesso": False, "mensagem": "Já existe um funcionário ativo com este CPF, Matrícula ou E-mail."}, 409
                else:
                    return {
                        "sucesso": False,
                        "inativo": True,
                        "mensagem": "Funcionário encontrado, mas inativo. Deseja reativá-lo?",
                        "usuario": user,
                        "funcionario": user
                    }, 409

            Database.executar_consulta(
                """
                INSERT INTO funcionarios (matricula, nome, cpf, email, telefone, profissao_id, setor_id, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """,
                (matricula, nome, cpf_fmt, email, telefone, int(profissao_id), int(setor_id)),
                retornar_dados=False
            )

            return {"sucesso": True, "mensagem": "Funcionário cadastrado com sucesso!"}, 201

        except Exception as e:
            print(f"[ERRO ADICIONAR FUNCIONARIO] {e}")
            return {"sucesso": False, "mensagem": f"Erro ao adicionar funcionário: {str(e)}"}, 500


    @staticmethod
    def atualizar(dados):
        cpf = dados.get("cpf", "").strip()
        matricula = dados.get("matricula", "").strip()
        nome = dados.get("nome", "").strip()
        email = dados.get("email", "").strip()
        telefone = dados.get("telefone", "").strip()
        setor_id = dados.get("setor_id")

        termo_busca = cpf or matricula
        if not termo_busca or not nome:
            return {"sucesso": False, "mensagem": "Informe o CPF/Matrícula e o Nome."}, 400

        profissao_input = dados.get("profissao") or dados.get("profissao_id")

        cpf_fmt = formatar_cpf(cpf) if validar_cpf(cpf) else cpf
        cpf_num = re.sub(r"\D", "", cpf)

        try:
            existente = Database.executar_consulta(
                "SELECT id, cpf, matricula, ativo, profissao_id, setor_id, email, telefone FROM funcionarios WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s OR matricula = %s)",
                (cpf_fmt, cpf_num if cpf_num else cpf, matricula)
            )

            if not existente:
                return {"sucesso": False, "mensagem": "Funcionário não encontrado."}, 404
            
            user = existente[0]
            prof_id = obter_ou_criar_profissao(profissao_input) if profissao_input else user["profissao_id"]
            set_id = int(setor_id) if setor_id else user["setor_id"]
            mat_val = matricula if matricula else user["matricula"]
            email_val = email if email else user["email"]
            tel_val = telefone if telefone is not None else user["telefone"]

            if user.get("ativo") == 0:
                Database.executar_consulta(
                    """
                    UPDATE funcionarios 
                    SET matricula = %s, nome = %s, email = %s, telefone = %s, profissao_id = %s, setor_id = %s, ativo = 1 
                    WHERE id = %s
                    """,
                    (mat_val, nome, email_val, tel_val, prof_id, set_id, user.get("id")),
                    retornar_dados=False
                )
                return {"sucesso": True, "mensagem": "Funcionário reativado e atualizado com sucesso!"}, 200

            Database.executar_consulta(
                """
                UPDATE funcionarios 
                SET matricula = %s, nome = %s, email = %s, telefone = %s, profissao_id = %s, setor_id = %s 
                WHERE id = %s
                """,
                (mat_val, nome, email_val, tel_val, prof_id, set_id, user.get("id")),
                retornar_dados=False
            )
            return {"sucesso": True, "mensagem": "Cadastro do funcionário atualizado com sucesso!"}, 200

        except Exception as e:
            print(f"[ERRO ATUALIZAR FUNCIONARIO] {e}")
            return {"sucesso": False, "mensagem": "Erro ao atualizar funcionário."}, 500


    @staticmethod
    def inativar(dados):
        cpf = dados.get("cpf", "").strip()
        matricula = dados.get("matricula", "").strip()

        termo = cpf or matricula
        if not termo:
            return {"sucesso": False, "mensagem": "Informe o CPF ou Matrícula."}, 400

        cpf_fmt = formatar_cpf(cpf) if validar_cpf(cpf) else cpf
        cpf_num = re.sub(r"\D", "", cpf)

        try:
            linhas_afetadas = Database.executar_consulta(
                "UPDATE funcionarios SET ativo = 0 WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s OR matricula = %s)",
                (cpf_fmt, cpf_num if cpf_num else cpf, matricula),
                retornar_dados=False
            )

            if linhas_afetadas > 0:
                return {"sucesso": True, "mensagem": "Funcionário inativado com sucesso."}, 200
            else:
                return {"sucesso": False, "mensagem": "Funcionário não encontrado."}, 404

        except Exception as e:
            print(f"[ERRO INATIVAR FUNCIONARIO] {e}")
            return {"sucesso": False, "mensagem": "Erro ao inativar funcionário."}, 500

    @staticmethod
    def reativar(dados):
        return UsuarioController.atualizar(dados)

FuncionarioController = UsuarioController

