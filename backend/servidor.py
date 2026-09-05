# =====================================================
#  SERVIDOR HTTP PURO — PYTHON + MySQL
#
#  Sem frameworks. Apenas http.server + mysql.connector.
#
#  Para executar:
#      python servidor.py
#
#  O servidor vai:
#   1) Servir os arquivos do frontend (HTML, CSS, JS)
#   2) Expor uma API REST para o CRUD de usuários
# =====================================================


import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import mysql.connector

from config import DB_CONFIG, PORTA_SERVIDOR
import re


# =====================================================
#  VALIDAÇÃO DE CPF
# =====================================================

def validar_cpf(cpf_str):
    """
    Valida um número de CPF (com ou sem pontuação).
    Verifica se possui 11 dígitos e não é uma sequência repetida.
    """
    if not cpf_str:
        return False

    digitos = re.sub(r"\D", "", str(cpf_str))

    if len(digitos) != 11:
        return False

    if digitos == digitos[0] * 11:
        return False

    return True


def formatar_cpf(cpf_str):
    """
    Retorna o CPF formatado como XXX.XXX.XXX-XX.
    """
    if not cpf_str:
        return ""
    digitos = re.sub(r"\D", "", str(cpf_str))
    if len(digitos) == 11:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"
    return cpf_str


# =====================================================
#  CAMINHO DO FRONTEND
# =====================================================

# O frontend fica na pasta ConsultaUsuarios,
# que está um nível acima da pasta backend.

PASTA_FRONTEND = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "ConsultaUsuarios"
)


# =====================================================
#  TIPOS MIME PARA ARQUIVOS ESTÁTICOS
# =====================================================

TIPOS_MIME = {
    ".html": "text/html; charset=utf-8",
    ".css":  "text/css; charset=utf-8",
    ".js":   "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif":  "image/gif",
    ".svg":  "image/svg+xml",
    ".ico":  "image/x-icon",
}


# =====================================================
#  CONEXÃO COM O MYSQL
# =====================================================

def conectar_banco():
    """
    Cria e retorna uma conexão com o MySQL.
    """
    return mysql.connector.connect(**DB_CONFIG)


def executar_consulta(sql, parametros=None, retornar_dados=True):
    """
    Executa uma query SQL e retorna os resultados.

    Se retornar_dados=True, retorna lista de dicionários.
    Se retornar_dados=False, retorna o número de linhas afetadas.
    """
    conexao = None
    cursor = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(sql, parametros or ())

        if retornar_dados:
            resultado = cursor.fetchall()
            return resultado
        else:
            conexao.commit()
            return cursor.rowcount

    except mysql.connector.Error as erro:
        print(f"[ERRO MySQL] {erro}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


# =====================================================
#  HANDLER HTTP — TRATA TODAS AS REQUISIÇÕES
# =====================================================

class ManipuladorHTTP(BaseHTTPRequestHandler):

    # -------------------------------------------------
    #  Utilidades de resposta
    # -------------------------------------------------

    def responder_json(self, dados, codigo=200):
        """
        Envia uma resposta JSON.
        """
        corpo = json.dumps(
            dados, ensure_ascii=False
        ).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)


    def ler_corpo_json(self):
        """
        Lê o corpo da requisição e retorna como dicionário.
        """
        tamanho = int(
            self.headers.get("Content-Length", 0)
        )

        corpo_bytes = self.rfile.read(tamanho)

        if not corpo_bytes:
            return {}

        return json.loads(
            corpo_bytes.decode("utf-8")
        )


    # -------------------------------------------------
    #  Servir arquivos estáticos (frontend)
    # -------------------------------------------------

    def servir_arquivo(self, caminho_relativo):
        """
        Serve um arquivo estático da pasta do frontend.
        """

        # Se o caminho é "/", serve index.html
        if caminho_relativo == "/" or caminho_relativo == "":
            caminho_relativo = "/index.html"

        # Monta o caminho completo
        caminho_arquivo = os.path.join(
            PASTA_FRONTEND,
            caminho_relativo.lstrip("/")
        )

        # Normaliza para evitar path traversal
        caminho_arquivo = os.path.normpath(caminho_arquivo)

        # Verifica se está dentro da pasta do frontend
        pasta_real = os.path.normpath(PASTA_FRONTEND)

        if not caminho_arquivo.startswith(pasta_real):
            self.send_response(403)
            self.end_headers()
            return

        # Verifica se o arquivo existe
        if not os.path.isfile(caminho_arquivo):
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<h1>404 — Arquivo não encontrado</h1>".encode("utf-8")
            )
            return

        # Determina o tipo MIME
        _, extensao = os.path.splitext(caminho_arquivo)
        tipo_mime = TIPOS_MIME.get(
            extensao.lower(),
            "application/octet-stream"
        )

        # Lê e envia o arquivo
        with open(caminho_arquivo, "rb") as arquivo:
            conteudo = arquivo.read()

        self.send_response(200)
        self.send_header("Content-Type", tipo_mime)
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)


    # -------------------------------------------------
    #  API — LOGIN
    # -------------------------------------------------

    def api_login(self):
        """
        POST /api/login

        Corpo: { "usuario": "...", "senha": "..." }

        Valida credenciais no banco de dados.
        """
        dados = self.ler_corpo_json()

        usuario = dados.get("usuario", "").strip()
        senha = dados.get("senha", "").strip()

        if not usuario or not senha:
            self.responder_json(
                {"sucesso": False, "mensagem": "Preencha todos os campos."},
                400
            )
            return

        try:
            resultado = executar_consulta(
                "SELECT id FROM admins WHERE usuario = %s AND senha = %s AND ativo = 1",
                (usuario, senha)
            )

            if resultado:
                self.responder_json(
                    {"sucesso": True, "mensagem": "Login realizado com sucesso!"}
                )
            else:
                self.responder_json(
                    {"sucesso": False, "mensagem": "Usuário ou senha incorretos."},
                    401
                )

        except Exception:
            self.responder_json(
                {"sucesso": False, "mensagem": "Erro no servidor."},
                500
            )


    # -------------------------------------------------
    #  API — LISTAR / BUSCAR USUÁRIOS (POR NOME OU CPF)
    # -------------------------------------------------

    def api_listar_usuarios(self):
        """
        GET /api/usuarios
        GET /api/usuarios?nome=João
        GET /api/usuarios?busca=123.456.789-01

        Retorna todos os usuários ativos ou filtra por nome ou CPF.
        """
        url_parseada = urlparse(self.path)
        parametros = parse_qs(url_parseada.query)

        filtro = (
            parametros.get("busca", [""])[0] or
            parametros.get("nome", [""])[0]
        ).strip()

        try:
            if filtro:
                filtro_numeros = re.sub(r"\D", "", filtro)
                resultado = executar_consulta(
                    "SELECT cpf, nome, profissao FROM usuarios WHERE (nome LIKE %s OR cpf LIKE %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') LIKE %s) AND ativo = 1 ORDER BY nome",
                    (f"%{filtro}%", f"%{filtro}%", f"%{filtro_numeros}%" if filtro_numeros else f"%{filtro}%")
                )
            else:
                resultado = executar_consulta(
                    "SELECT cpf, nome, profissao FROM usuarios WHERE ativo = 1 ORDER BY nome"
                )

            self.responder_json(
                {"sucesso": True, "usuarios": resultado}
            )

        except Exception:
            self.responder_json(
                {"sucesso": False, "mensagem": "Erro ao consultar usuários."},
                500
            )


    # -------------------------------------------------
    #  API — BUSCAR USUÁRIO POR CPF (PARA EDIÇÃO)
    # -------------------------------------------------

    def api_buscar_usuario_cpf(self):
        """
        GET /api/usuarios/buscar-cpf?cpf=...

        Retorna os dados de um usuário pelo CPF.
        Se inativo, retorna inativo: True e mensagem de confirmação.
        """
        url_parseada = urlparse(self.path)
        parametros = parse_qs(url_parseada.query)

        cpf = parametros.get("cpf", [""])[0].strip()

        if not cpf:
            self.responder_json(
                {"sucesso": False, "mensagem": "Informe o CPF."},
                400
            )
            return

        if not validar_cpf(cpf):
            self.responder_json(
                {"sucesso": False, "mensagem": "CPF inválido. Verifique os números digitados."},
                400
            )
            return

        cpf_fmt = formatar_cpf(cpf)
        cpf_num = re.sub(r"\D", "", cpf)

        try:
            resultado = executar_consulta(
                "SELECT cpf, nome, profissao, ativo FROM usuarios WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s)",
                (cpf_fmt, cpf_num)
            )

            if resultado:
                user = resultado[0]
                if user.get("ativo") == 1:
                    self.responder_json(
                        {"sucesso": True, "usuario": user}
                    )
                else:
                    self.responder_json(
                        {
                            "sucesso": False,
                            "inativo": True,
                            "mensagem": "Usuário encontrado, mas inativo. Deseja reativá-lo?",
                            "usuario": user
                        },
                        200
                    )
            else:
                self.responder_json(
                    {"sucesso": False, "mensagem": "Usuário não encontrado."},
                    404
                )

        except Exception:
            self.responder_json(
                {"sucesso": False, "mensagem": "Erro ao buscar usuário por CPF."},
                500
            )


    # -------------------------------------------------
    #  API — ADICIONAR USUÁRIO
    # -------------------------------------------------

    def api_adicionar_usuario(self):
        """
        POST /api/usuarios

        Corpo: { "cpf": "...", "nome": "...", "profissao": "..." }
        """
        dados = self.ler_corpo_json()

        cpf = dados.get("cpf", "").strip()
        nome = dados.get("nome", "").strip()
        profissao = dados.get("profissao", "").strip()

        if not cpf or not nome or not profissao:
            self.responder_json(
                {"sucesso": False, "mensagem": "Preencha todos os campos."},
                400
            )
            return

        if not validar_cpf(cpf):
            self.responder_json(
                {"sucesso": False, "mensagem": "CPF inválido. Verifique os números digitados."},
                400
            )
            return

        cpf_fmt = formatar_cpf(cpf)
        cpf_num = re.sub(r"\D", "", cpf)

        try:
            # Verifica se já existe
            existente = executar_consulta(
                "SELECT cpf, nome, profissao, ativo FROM usuarios WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s)",
                (cpf_fmt, cpf_num)
            )

            if existente:
                user = existente[0]
                if user.get("ativo") == 1:
                    self.responder_json(
                        {"sucesso": False, "mensagem": "Já existe um usuário ativo com esse CPF."},
                        409
                    )
                    return
                else:
                    # Usuário inativo existente: NÃO sobrescreve automaticamente
                    self.responder_json(
                        {
                            "sucesso": False,
                            "inativo": True,
                            "mensagem": "Usuário encontrado, mas inativo. Deseja reativá-lo?",
                            "usuario": user
                        },
                        409
                    )
                    return

            # Insere novo
            executar_consulta(
                "INSERT INTO usuarios (cpf, nome, profissao, ativo) VALUES (%s, %s, %s, 1)",
                (cpf_fmt, nome, profissao),
                retornar_dados=False
            )

            self.responder_json(
                {"sucesso": True, "mensagem": "Usuário adicionado com sucesso!"},
                201
            )

        except Exception:
            self.responder_json(
                {"sucesso": False, "mensagem": "Erro ao adicionar usuário."},
                500
            )


    # -------------------------------------------------
    #  API — ATUALIZAR USUÁRIO
    # -------------------------------------------------

    def api_atualizar_usuario(self):
        """
        PUT /api/usuarios

        Corpo: { "cpf": "...", "nome": "...", "profissao": "..." }
        """
        dados = self.ler_corpo_json()

        cpf = dados.get("cpf", "").strip()
        nome = dados.get("nome", "").strip()
        profissao = dados.get("profissao", "").strip()

        if not cpf or not nome or not profissao:
            self.responder_json(
                {"sucesso": False, "mensagem": "Preencha todos os campos."},
                400
            )
            return

        if not validar_cpf(cpf):
            self.responder_json(
                {"sucesso": False, "mensagem": "CPF inválido. Verifique os números digitados."},
                400
            )
            return

        cpf_fmt = formatar_cpf(cpf)
        cpf_num = re.sub(r"\D", "", cpf)

        try:
            existente = executar_consulta(
                "SELECT cpf, ativo FROM usuarios WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s)",
                (cpf_fmt, cpf_num)
            )

            if not existente:
                self.responder_json(
                    {"sucesso": False, "mensagem": "Usuário não encontrado."},
                    404
                )
                return

            if existente[0].get("ativo") == 0:
                self.responder_json(
                    {
                        "sucesso": False,
                        "inativo": True,
                        "mensagem": "Usuário encontrado, mas inativo. Deseja reativá-lo?"
                    },
                    400
                )
                return

            executar_consulta(
                "UPDATE usuarios SET nome = %s, profissao = %s WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s) AND ativo = 1",
                (nome, profissao, cpf_fmt, cpf_num),
                retornar_dados=False
            )

            self.responder_json(
                {"sucesso": True, "mensagem": "Cadastro atualizado com sucesso!"}
            )

        except Exception:
            self.responder_json(
                {"sucesso": False, "mensagem": "Erro ao atualizar usuário."},
                500
            )


    # -------------------------------------------------
    #  API — REATIVAR USUÁRIO
    # -------------------------------------------------

    def api_reativar_usuario(self):
        """
        POST /api/usuarios/reativar

        Corpo: { "cpf": "...", "nome": "...", "profissao": "..." }
        Reativa um usuário inativo e atualiza nome/profissão se fornecidos.
        """
        dados = self.ler_corpo_json()

        cpf = dados.get("cpf", "").strip()
        nome = dados.get("nome", "").strip()
        profissao = dados.get("profissao", "").strip()

        if not cpf:
            self.responder_json(
                {"sucesso": False, "mensagem": "Informe o CPF."},
                400
            )
            return

        if not validar_cpf(cpf):
            self.responder_json(
                {"sucesso": False, "mensagem": "CPF inválido. Verifique os números digitados."},
                400
            )
            return

        cpf_fmt = formatar_cpf(cpf)
        cpf_num = re.sub(r"\D", "", cpf)

        try:
            existente = executar_consulta(
                "SELECT cpf, nome, profissao, ativo FROM usuarios WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s)",
                (cpf_fmt, cpf_num)
            )

            if not existente:
                self.responder_json(
                    {"sucesso": False, "mensagem": "Usuário não encontrado."},
                    404
                )
                return

            user = existente[0]
            cpf_existente = user.get("cpf")
            novo_nome = nome if nome else user.get("nome")
            nova_profissao = profissao if profissao else user.get("profissao")

            executar_consulta(
                "UPDATE usuarios SET nome = %s, profissao = %s, ativo = 1 WHERE cpf = %s",
                (novo_nome, nova_profissao, cpf_existente),
                retornar_dados=False
            )

            self.responder_json(
                {"sucesso": True, "mensagem": "Usuário reativado com sucesso!"}
            )

        except Exception:
            self.responder_json(
                {"sucesso": False, "mensagem": "Erro ao reativar usuário."},
                500
            )


    # -------------------------------------------------
    #  API — DELETAR USUÁRIO (INATIVAÇÃO)
    # -------------------------------------------------

    def api_deletar_usuario(self):
        """
        DELETE /api/usuarios

        Corpo: { "cpf": "..." }
        """
        dados = self.ler_corpo_json()

        cpf = dados.get("cpf", "").strip()

        if not cpf:
            self.responder_json(
                {"sucesso": False, "mensagem": "Informe o CPF do usuário."},
                400
            )
            return

        if not validar_cpf(cpf):
            self.responder_json(
                {"sucesso": False, "mensagem": "CPF inválido. Verifique os números digitados."},
                400
            )
            return

        cpf_fmt = formatar_cpf(cpf)
        cpf_num = re.sub(r"\D", "", cpf)

        try:
            existente = executar_consulta(
                "SELECT cpf, ativo FROM usuarios WHERE (cpf = %s OR REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s)",
                (cpf_fmt, cpf_num)
            )

            if not existente:
                self.responder_json(
                    {"sucesso": False, "mensagem": "Usuário não encontrado."},
                    404
                )
                return

            if existente[0].get("ativo") == 0:
                self.responder_json(
                    {"sucesso": False, "inativo": True, "mensagem": "Usuário já se encontra inativo."},
                    400
                )
                return

            # Soft delete: marca ativo = 0
            linhas = executar_consulta(
                "UPDATE usuarios SET ativo = 0 WHERE (cpf = %s OR REPLACE(REPLACE(REPLACE(cpf, '.', ''), '-', ''), ' ', '') = %s) AND ativo = 1",
                (cpf_fmt, cpf_num),
                retornar_dados=False
            )

            if linhas == 0:
                self.responder_json(
                    {"sucesso": False, "mensagem": "Usuário não encontrado ou já inativo."},
                    404
                )
            else:
                self.responder_json(
                    {"sucesso": True, "mensagem": "Usuário inativado com sucesso!"}
                )

        except Exception as erro:
            print(f"[ERRO DELETAR] {erro}")
            self.responder_json(
                {"sucesso": False, "mensagem": "Erro ao inativar usuário."},
                500
            )


    # -------------------------------------------------
    #  ROTEAMENTO — GET
    # -------------------------------------------------

    def do_GET(self):
        """
        Trata requisições GET.

        Se começa com /api/, direciona para a API.
        Caso contrário, serve arquivo estático.
        """
        url_parseada = urlparse(self.path)
        caminho = url_parseada.path

        if caminho == "/api/usuarios":
            self.api_listar_usuarios()

        elif caminho == "/api/usuarios/buscar-cpf":
            self.api_buscar_usuario_cpf()

        else:
            # Serve arquivo do frontend
            self.servir_arquivo(caminho)


    # -------------------------------------------------
    #  ROTEAMENTO — POST
    # -------------------------------------------------

    def do_POST(self):
        """
        Trata requisições POST.
        """
        caminho = urlparse(self.path).path

        if caminho == "/api/login":
            self.api_login()

        elif caminho == "/api/usuarios":
            self.api_adicionar_usuario()

        elif caminho == "/api/usuarios/reativar":
            self.api_reativar_usuario()

        else:
            self.responder_json(
                {"erro": "Rota não encontrada."},
                404
            )


    # -------------------------------------------------
    #  ROTEAMENTO — PUT
    # -------------------------------------------------

    def do_PUT(self):
        """
        Trata requisições PUT.
        """
        caminho = urlparse(self.path).path

        if caminho == "/api/usuarios":
            self.api_atualizar_usuario()

        else:
            self.responder_json(
                {"erro": "Rota não encontrada."},
                404
            )


    # -------------------------------------------------
    #  ROTEAMENTO — DELETE
    # -------------------------------------------------

    def do_DELETE(self):
        """
        Trata requisições DELETE.
        """
        caminho = urlparse(self.path).path

        if caminho == "/api/usuarios":
            self.api_deletar_usuario()

        else:
            self.responder_json(
                {"erro": "Rota não encontrada."},
                404
            )


    # -------------------------------------------------
    #  ROTEAMENTO — OPTIONS (CORS)
    # -------------------------------------------------

    def do_OPTIONS(self):
        """
        Responde pré-flight requests do CORS.
        """
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


    # -------------------------------------------------
    #  LOG SIMPLIFICADO
    # -------------------------------------------------

    def log_message(self, formato, *args):
        """
        Sobrescreve o log padrão para um formato mais limpo.
        """
        print(f"[{self.log_date_time_string()}] {args[0]}")


# =====================================================
#  INICIAR O SERVIDOR
# =====================================================

def iniciar_servidor():
    """
    Inicia o servidor HTTP na porta configurada.
    """

    # Testa a conexao com o banco antes de iniciar
    print("=" * 55)
    print("  SERVIDOR - CONTROLE DE USUARIOS")
    print("=" * 55)
    print()

    print("[1/3] Testando conexao com o MySQL...")

    try:
        conexao = conectar_banco()
        conexao.close()
        print("      [OK] Conexao com o MySQL OK!")
    except mysql.connector.Error as erro:
        print(f"      [ERRO] {erro}")
        print()
        print("      Verifique:")
        print("      - O MySQL esta rodando?")
        print("      - As credenciais em config.py estao corretas?")
        print("      - O banco 'controle_usuarios' foi criado? (execute init_db.sql)")
        print()
        sys.exit(1)


    print(f"[2/3] Frontend: {os.path.abspath(PASTA_FRONTEND)}")

    if not os.path.isdir(PASTA_FRONTEND):
        print("      [ERRO] Pasta do frontend nao encontrada!")
        sys.exit(1)
    else:
        print("      [OK] Pasta do frontend encontrada!")


    print(f"[3/3] Iniciando servidor na porta {PORTA_SERVIDOR}...")
    print()
    print(f"      >>> http://localhost:{PORTA_SERVIDOR}")
    print()
    print("      Pressione Ctrl+C para parar.")
    print()
    print("-" * 55)


    servidor = HTTPServer(
        ("", PORTA_SERVIDOR),
        ManipuladorHTTP
    )

    try:
        servidor.serve_forever()

    except KeyboardInterrupt:
        print()
        print("[SERVIDOR] Encerrado pelo usuário.")
        servidor.server_close()


# =====================================================
#  PONTO DE ENTRADA
# =====================================================

if __name__ == "__main__":
    iniciar_servidor()
