from database import Database

class AuxController:
    @staticmethod
    def listar_profissoes():
        """
        GET /api/profissoes
        Retorna todas as profissões ativas.
        """
        try:
            resultado = Database.executar_consulta(
                "SELECT id, nome, descricao FROM profissoes WHERE ativo = 1 ORDER BY nome"
            )
            return {"sucesso": True, "profissoes": resultado}, 200
        except Exception as e:
            print(f"[ERRO LISTAR PROFISSOES] {e}")
            return {"sucesso": False, "mensagem": "Erro ao consultar profissões."}, 500

    @staticmethod
    def listar_setores():
        """
        GET /api/setores
        Retorna todos os setores ativos.
        """
        try:
            resultado = Database.executar_consulta(
                "SELECT id, nome, descricao FROM setores WHERE ativo = 1 ORDER BY nome"
            )
            return {"sucesso": True, "setores": resultado}, 200
        except Exception as e:
            print(f"[ERRO LISTAR SETORES] {e}")
            return {"sucesso": False, "mensagem": "Erro ao consultar setores."}, 500
