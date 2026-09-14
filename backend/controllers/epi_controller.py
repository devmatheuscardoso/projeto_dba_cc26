from database import Database

class EpiController:
    @staticmethod
    def listar():
        """
        GET /api/epis
        Retorna todos os EPIs ativos e com quantidade > 0 no estoque.
        """
        try:
            resultado = Database.executar_consulta(
                "SELECT id, codigo, nome, tamanho, quantidade FROM epis WHERE ativo = 1 AND quantidade > 0 ORDER BY nome"
            )
            return {"sucesso": True, "epis": resultado}, 200
        except Exception:
            return {"sucesso": False, "mensagem": "Erro ao consultar EPIs no estoque."}, 500
