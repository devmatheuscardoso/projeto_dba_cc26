from database import Database

class EpiController:
    @staticmethod
    def listar():
        """
        GET /api/epis
        Retorna todos os EPIs ativos no estoque com ca e estoque_minimo.
        """
        try:
            resultado = Database.executar_consulta(
                "SELECT id, codigo, nome, ca, tamanho, quantidade, estoque_minimo FROM epis WHERE ativo = 1 ORDER BY nome"
            )
            return {"sucesso": True, "epis": resultado}, 200
        except Exception as e:
            print(f"[ERRO LISTAR EPIS] {e}")
            return {"sucesso": False, "mensagem": "Erro ao consultar EPIs no estoque."}, 500
