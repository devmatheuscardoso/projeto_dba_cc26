import os
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

# O frontend fica na pasta ConsultaFuncionarios,
# que está um nível acima da pasta backend.
_pasta_func = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "ConsultaFuncionarios"
)
_pasta_user = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "ConsultaUsuarios"
)
PASTA_FRONTEND = _pasta_func if os.path.exists(_pasta_func) else _pasta_user


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
