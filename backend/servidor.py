import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from config import PORTA_SERVIDOR
from utils import TIPOS_MIME, PASTA_FRONTEND

from controllers.auth_controller import AuthController
from controllers.funcionario_controller import FuncionarioController
from controllers.epi_controller import EpiController
from controllers.movimentacao_controller import MovimentacaoController
from controllers.aux_controller import AuxController


# =====================================================
#  HANDLER HTTP — TRATA TODAS AS REQUISIÇÕES
# =====================================================

class ManipuladorHTTP(BaseHTTPRequestHandler):

    def responder_json(self, dados, codigo=200):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def ler_corpo_json(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        corpo_bytes = self.rfile.read(tamanho)
        if not corpo_bytes: return {}
        return json.loads(corpo_bytes.decode("utf-8"))

    def servir_arquivo(self, caminho_relativo):
        if caminho_relativo == "/" or caminho_relativo == "":
            caminho_relativo = "/index.html"
            
        caminho_arquivo = os.path.join(PASTA_FRONTEND, caminho_relativo.lstrip("/"))
        caminho_arquivo = os.path.normpath(caminho_arquivo)
        pasta_real = os.path.normpath(PASTA_FRONTEND)

        if not caminho_arquivo.startswith(pasta_real):
            self.send_response(403)
            self.end_headers()
            return

        if not os.path.isfile(caminho_arquivo):
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>404 — Arquivo não encontrado</h1>".encode("utf-8"))
            return

        _, extensao = os.path.splitext(caminho_arquivo)
        tipo_mime = TIPOS_MIME.get(extensao.lower(), "application/octet-stream")

        with open(caminho_arquivo, "rb") as arquivo:
            conteudo = arquivo.read()

        self.send_response(200)
        self.send_header("Content-Type", tipo_mime)
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)

    def do_GET(self):
        url_parseada = urlparse(self.path)
        caminho = url_parseada.path

        if caminho in ["/api/usuarios", "/api/funcionarios"]:
            dados, codigo = FuncionarioController.listar_usuarios(parse_qs(url_parseada.query))
            self.responder_json(dados, codigo)
        elif caminho in ["/api/usuarios/buscar-cpf", "/api/funcionarios/buscar-cpf"]:
            dados, codigo = FuncionarioController.buscar_por_cpf(parse_qs(url_parseada.query))
            self.responder_json(dados, codigo)
        elif caminho == "/api/profissoes":
            dados, codigo = AuxController.listar_profissoes()
            self.responder_json(dados, codigo)
        elif caminho == "/api/setores":
            dados, codigo = AuxController.listar_setores()
            self.responder_json(dados, codigo)
        elif caminho == "/api/epis":
            dados, codigo = EpiController.listar()
            self.responder_json(dados, codigo)
        elif caminho == "/api/retiradas":
            dados, codigo = MovimentacaoController.listar_retiradas_usuario(parse_qs(url_parseada.query))
            self.responder_json(dados, codigo)
        elif caminho.startswith("/api/"):
            self.responder_json({"sucesso": False, "mensagem": "Endpoint GET não encontrado."}, 404)
        else:
            self.servir_arquivo(caminho)

    def do_POST(self):
        url_parseada = urlparse(self.path)
        caminho = url_parseada.path

        if caminho == "/api/login":
            dados, codigo = AuthController.login(self.ler_corpo_json())
            self.responder_json(dados, codigo)
        elif caminho in ["/api/usuarios", "/api/funcionarios"]:
            dados, codigo = FuncionarioController.adicionar(self.ler_corpo_json())
            self.responder_json(dados, codigo)
        elif caminho in ["/api/usuarios/reativar", "/api/funcionarios/reativar"]:
            dados, codigo = FuncionarioController.reativar(self.ler_corpo_json())
            self.responder_json(dados, codigo)
        elif caminho == "/api/retiradas":
            dados, codigo = MovimentacaoController.registrar_retirada(self.ler_corpo_json())
            self.responder_json(dados, codigo)
        elif caminho == "/api/devolucoes":
            dados, codigo = MovimentacaoController.registrar_devolucao(self.ler_corpo_json())
            self.responder_json(dados, codigo)
        else:
            self.responder_json({"sucesso": False, "mensagem": "Endpoint POST não encontrado."}, 404)

    def do_PUT(self):
        url_parseada = urlparse(self.path)
        caminho = url_parseada.path

        if caminho in ["/api/usuarios", "/api/funcionarios"]:
            dados, codigo = FuncionarioController.atualizar(self.ler_corpo_json())
            self.responder_json(dados, codigo)
        else:
            self.responder_json({"sucesso": False, "mensagem": "Endpoint PUT não encontrado."}, 404)

    def do_DELETE(self):
        url_parseada = urlparse(self.path)
        caminho = url_parseada.path

        if caminho in ["/api/usuarios", "/api/funcionarios"]:
            dados, codigo = FuncionarioController.inativar(self.ler_corpo_json())
            self.responder_json(dados, codigo)
        else:
            self.responder_json({"sucesso": False, "mensagem": "Endpoint DELETE não encontrado."}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# =====================================================
#  INICIALIZAÇÃO DO SERVIDOR
# =====================================================

def iniciar_servidor():
    endereco = ("", PORTA_SERVIDOR)
    httpd = HTTPServer(endereco, ManipuladorHTTP)
    print(f"===========================================================")
    print(f"Servidor rodando na porta {PORTA_SERVIDOR}...")
    print(f"Acesse: http://localhost:{PORTA_SERVIDOR}")
    print(f"===========================================================")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    iniciar_servidor()
