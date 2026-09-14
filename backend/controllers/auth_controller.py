from database import Database

class AuthController:
    @staticmethod
    def login(dados):
        """
        POST /api/login
        Valida credenciais no banco de dados.
        """
        usuario = dados.get("usuario", "").strip()
        senha = dados.get("senha", "").strip()

        if not usuario or not senha:
            return {"sucesso": False, "mensagem": "Preencha todos os campos."}, 400

        try:
            resultado = Database.executar_consulta(
                "SELECT id FROM admins WHERE usuario = %s AND senha = %s AND ativo = 1",
                (usuario, senha)
            )

            if resultado:
                return {"sucesso": True, "mensagem": "Login realizado com sucesso!"}, 200
            else:
                return {"sucesso": False, "mensagem": "Usuário ou senha incorretos."}, 401

        except Exception as e:
            return {"sucesso": False, "mensagem": "Erro no servidor."}, 500
