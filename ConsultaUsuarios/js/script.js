console.log("SCRIPT CARREGADO");

/* =====================================================
   SISTEMA DE CONSULTA DE USUÁRIOS
   Front-end — HTML + CSS + JavaScript

   Conectado ao backend Python via API REST.
   Todas as operações (login, consulta, CRUD)
   são feitas via fetch() para o servidor.
===================================================== */


/* =====================================================
   ENDEREÇO DA API
===================================================== */

const API_URL = window.location.origin + "/api";


/* =====================================================
   LOGIN
===================================================== */

function fazerLogin() {

    const campoUsuario =
        document.getElementById("usuario");

    const campoSenha =
        document.getElementById("senha");

    const mensagem =
        document.getElementById("mensagem-login");


    if (!campoUsuario || !campoSenha || !mensagem) {
        return;
    }


    const usuario =
        campoUsuario.value.trim();

    const senha =
        campoSenha.value.trim();


    if (usuario === "" || senha === "") {

        mensagem.textContent =
            "Preencha todos os campos.";

        mensagem.style.color = "red";

        return;
    }


    /*
       Envia as credenciais para o backend.
    */

    fetch(API_URL + "/login", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            usuario: usuario,
            senha: senha
        })

    })
    .then(function (resposta) {

        return resposta.json();

    })
    .then(function (dados) {

        mensagem.textContent = dados.mensagem;

        if (dados.sucesso) {

            mensagem.style.color = "green";

            setTimeout(function () {

                window.location.href =
                    "telas/consulta.html";

            }, 500);

        } else {

            mensagem.style.color = "red";

        }

    })
    .catch(function (erro) {

        console.error("Erro no login:", erro);

        mensagem.textContent =
            "Erro ao conectar com o servidor.";

        mensagem.style.color = "red";

    });

}


/* =====================================================
   MOSTRAR / OCULTAR SENHA
===================================================== */

function mostrarSenha() {

    const campoSenha =
        document.getElementById("senha");


    if (!campoSenha) {
        return;
    }


    if (campoSenha.type === "password") {

        campoSenha.type = "text";

    } else {

        campoSenha.type = "password";

    }

}


/* =====================================================
   MÁSCARA AUTOMÁTICA DE CPF
===================================================== */

function aplicarMascaraCPF(input) {

    if (!input) return;

    let valor = input.value.replace(/\D/g, "");

    if (valor.length > 11) {
        valor = valor.slice(0, 11);
    }

    if (valor.length > 9) {
        valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})$/, "$1.$2.$3-$4");
    } else if (valor.length > 6) {
        valor = valor.replace(/^(\d{3})(\d{3})(\d{1,6})$/, "$1.$2.$3");
    } else if (valor.length > 3) {
        valor = valor.replace(/^(\d{3})(\d{1,3})$/, "$1.$2");
    }

    input.value = valor;

}


/* =====================================================
   VALIDAÇÃO DE CPF (DÍGITOS VERIFICADORES)
===================================================== */

function validarCPF(cpfStr) {

    if (!cpfStr) return false;

    const digitos = String(cpfStr).replace(/\D/g, "");

    if (digitos.length !== 11) return false;

    if (/^(\d)\1{10}$/.test(digitos)) return false;

    return true;

}


/* =====================================================
   LOGOUT / SAIR
===================================================== */

function fazerLogout() {

    sessionStorage.clear();

    window.location.href = "../index.html";

}


/* =====================================================
   NAVEGAÇÃO ENTRE TELAS
===================================================== */

function abrirEdicao() {

    window.location.href = "editar.html";

}


function abrirAdicionar() {

    window.location.href = "adicionar.html";

}


function abrirAtualizar() {

    window.location.href = "atualizar.html";

}


function abrirDeletar() {

    window.location.href = "deletar.html";

}


function voltarConsulta() {

    window.location.href = "consulta.html";

}



/* =====================================================
   CONSULTAR USUÁRIO
===================================================== */

function consultarUsuario() {

    console.log("CONSULTAR FOI EXECUTADA");

    const campo = document.getElementById("nome-pesquisa");

    if (!campo) {
        return;
    }

    const nomePesquisa = campo.value.trim();

    if (nomePesquisa === "") {

        alert("Digite um nome para realizar a consulta.");

        return;
    }

    sessionStorage.setItem(
        "ultimaPesquisa",
        nomePesquisa
    );

    window.location.href = "resultados.html";
}


/* =====================================================
   MOSTRAR RESULTADOS
===================================================== */

function carregarResultados() {

    const tabela =
        document.getElementById("tabela-usuarios");

    const textoPesquisa =
        document.getElementById("texto-pesquisa");

    const total =
        document.getElementById("total-resultados");


    /*
       Se não estamos na tela de resultados,
       não faz nada.
    */

    if (!tabela) {
        return;
    }


    /*
       Recupera a pesquisa realizada na tela anterior.
    */

    const pesquisa =
        sessionStorage.getItem("ultimaPesquisa") || "";


    if (textoPesquisa) {

        textoPesquisa.textContent =
            `"${pesquisa}"`;

    }


    /*
       Busca os usuários na API do backend.
    */

    fetch(API_URL + "/usuarios?nome=" + encodeURIComponent(pesquisa))

    .then(function (resposta) {

        return resposta.json();

    })
    .then(function (dados) {

        if (!dados.sucesso) {

            tabela.innerHTML = `
                <tr>
                    <td
                        colspan="3"
                        style="text-align:center;"
                    >
                        Erro ao buscar usuários.
                    </td>
                </tr>
            `;

            return;
        }


        const resultados = dados.usuarios;


        /*
           Limpa a tabela antes de preencher.
        */

        tabela.innerHTML = "";


        /*
           Cria uma linha para cada usuário encontrado.
        */

        resultados.forEach(function (usuario) {

            const linha =
                document.createElement("tr");


            linha.innerHTML = `

                <td>${usuario.cpf}</td>

                <td>${usuario.nome}</td>

                <td>${usuario.profissao}</td>

            `;


            tabela.appendChild(linha);

        });


        /*
           Mostra o número de resultados.
        */

        if (total) {

            total.textContent =
                resultados.length;

        }


        /*
           Caso nenhum usuário seja encontrado.
        */

        if (resultados.length === 0) {

            tabela.innerHTML = `

                <tr>

                    <td
                        colspan="3"
                        style="text-align:center;"
                    >
                        Nenhum usuário encontrado.
                    </td>

                </tr>

            `;

        }

    })
    .catch(function (erro) {

        console.error("Erro ao carregar resultados:", erro);

        tabela.innerHTML = `
            <tr>
                <td
                    colspan="3"
                    style="text-align:center;"
                >
                    Erro ao conectar com o servidor.
                </td>
            </tr>
        `;

    });

}


/* =====================================================
   BUSCAR USUÁRIO POR CPF (ETAPA 1 DA EDIÇÃO)
===================================================== */

function buscarUsuarioPorCPF() {

    const campoCPF =
        document.getElementById("cpf");

    const campoNome =
        document.getElementById("nome");

    const campoProfissao =
        document.getElementById("profissao");

    const mensagem =
        document.getElementById("mensagem-edicao");


    if (!campoCPF || !mensagem) {
        return;
    }


    const cpf =
        campoCPF.value.trim();


    if (cpf === "") {

        mensagem.textContent =
            "Digite o CPF para buscar os dados.";

        mensagem.style.color = "red";

        return;

    }


    if (!validarCPF(cpf)) {

        mensagem.textContent =
            "CPF inválido. Verifique os números digitados.";

        mensagem.style.color = "red";

        return;

    }


    fetch(API_URL + "/usuarios/buscar-cpf?cpf=" + encodeURIComponent(cpf))

    .then(function (resposta) {

        return resposta.json();

    })
    .then(function (dados) {

        if (dados.sucesso) {

            if (campoNome) {
                campoNome.value = dados.usuario.nome;
            }

            if (campoProfissao) {
                campoProfissao.value = dados.usuario.profissao;
            }

            mensagem.textContent =
                "Usuário encontrado! Altere o nome e a profissão e clique em 'Salvar Alterações'.";

            mensagem.style.color = "green";

        } else {

            mensagem.textContent = dados.mensagem;

            mensagem.style.color = "red";

        }

    })
    .catch(function (erro) {

        console.error("Erro ao buscar por CPF:", erro);

        mensagem.textContent =
            "Erro ao conectar com o servidor.";

        mensagem.style.color = "red";

    });

}


/* =====================================================
   VERIFICAR USUÁRIO PARA DELETAR
===================================================== */

function buscarUsuarioParaDeletar() {

    const campoCPF =
        document.getElementById("cpf");

    const mensagem =
        document.getElementById("mensagem-edicao");

    const secaoDeletar =
        document.getElementById("secao-dados-deletar");

    const spanNome =
        document.getElementById("deletar-nome");

    const spanProfissao =
        document.getElementById("deletar-profissao");


    if (!campoCPF || !mensagem) {
        return;
    }


    const cpf =
        campoCPF.value.trim();


    if (cpf === "") {

        mensagem.textContent =
            "Digite o CPF para verificar os dados.";

        mensagem.style.color = "red";

        return;

    }


    if (!validarCPF(cpf)) {

        mensagem.textContent =
            "CPF inválido. Verifique os números digitados.";

        mensagem.style.color = "red";

        return;

    }


    fetch(API_URL + "/usuarios/buscar-cpf?cpf=" + encodeURIComponent(cpf))

    .then(function (resposta) {

        return resposta.json();

    })
    .then(function (dados) {

        if (dados.sucesso) {

            if (secaoDeletar) {
                secaoDeletar.style.display = "block";
            }

            if (spanNome) {
                spanNome.textContent = dados.usuario.nome;
            }

            if (spanProfissao) {
                spanProfissao.textContent = dados.usuario.profissao;
            }

            mensagem.textContent =
                "Usuário encontrado! Clique abaixo para inativar.";

            mensagem.style.color = "green";

        } else {

            if (secaoDeletar) {
                secaoDeletar.style.display = "none";
            }

            mensagem.textContent = dados.mensagem;

            mensagem.style.color = "red";

        }

    })
    .catch(function (erro) {

        console.error("Erro ao buscar para deletar:", erro);

        mensagem.textContent =
            "Erro ao conectar com o servidor.";

        mensagem.style.color = "red";

    });

}


/* =====================================================
   ADICIONAR USUÁRIO
===================================================== */

function adicionarUsuario() {

    const campoCPF =
        document.getElementById("cpf");

    const campoNome =
        document.getElementById("nome");

    const campoProfissao =
        document.getElementById("profissao");

    const mensagem =
        document.getElementById("mensagem-edicao");


    if (
        !campoCPF ||
        !campoNome ||
        !campoProfissao ||
        !mensagem
    ) {
        return;
    }


    const cpf =
        campoCPF.value.trim();

    const nome =
        campoNome.value.trim();

    const profissao =
        campoProfissao.value.trim();


    if (
        cpf === "" ||
        nome === "" ||
        profissao === ""
    ) {

        mensagem.textContent =
            "Preencha todos os campos.";

        mensagem.style.color = "red";

        return;

    }


    if (!validarCPF(cpf)) {

        mensagem.textContent =
            "CPF inválido. Verifique os números digitados.";

        mensagem.style.color = "red";

        return;

    }


    fetch(API_URL + "/usuarios", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            cpf: cpf,
            nome: nome,
            profissao: profissao
        })

    })
    .then(function (resposta) {

        return resposta.json();

    })
    .then(function (dados) {

        mensagem.textContent = dados.mensagem;

        if (dados.sucesso) {

            mensagem.style.color = "green";

            limparCampos();

        } else {

            mensagem.style.color = "red";

        }

    })
    .catch(function (erro) {

        console.error("Erro ao adicionar:", erro);

        mensagem.textContent =
            "Erro ao conectar com o servidor.";

        mensagem.style.color = "red";

    });

}


/* =====================================================
   ATUALIZAR USUÁRIO
===================================================== */

function atualizarUsuario() {

    const campoCPF =
        document.getElementById("cpf");

    const campoNome =
        document.getElementById("nome");

    const campoProfissao =
        document.getElementById("profissao");

    const mensagem =
        document.getElementById("mensagem-edicao");


    if (
        !campoCPF ||
        !campoNome ||
        !campoProfissao ||
        !mensagem
    ) {
        return;
    }


    const cpf =
        campoCPF.value.trim();

    const nome =
        campoNome.value.trim();

    const profissao =
        campoProfissao.value.trim();


    if (
        cpf === "" ||
        nome === "" ||
        profissao === ""
    ) {

        mensagem.textContent =
            "Preencha todos os campos (CPF, Nome e Profissão).";

        mensagem.style.color = "red";

        return;

    }


    if (!validarCPF(cpf)) {

        mensagem.textContent =
            "CPF inválido. Verifique os números digitados.";

        mensagem.style.color = "red";

        return;

    }


    fetch(API_URL + "/usuarios", {

        method: "PUT",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            cpf: cpf,
            nome: nome,
            profissao: profissao
        })

    })
    .then(function (resposta) {

        return resposta.json();

    })
    .then(function (dados) {

        mensagem.textContent = dados.mensagem;

        if (dados.sucesso) {

            mensagem.style.color = "green";

            limparCampos();

        } else {

            mensagem.style.color = "red";

        }

    })
    .catch(function (erro) {

        console.error("Erro ao atualizar:", erro);

        mensagem.textContent =
            "Erro ao conectar com o servidor.";

        mensagem.style.color = "red";

    });

}


/* =====================================================
   DELETAR USUÁRIO (INATIVAÇÃO POR CPF)
===================================================== */

function deletarUsuario() {

    const campoCPF =
        document.getElementById("cpf");

    const mensagem =
        document.getElementById("mensagem-edicao");


    if (!campoCPF || !mensagem) {
        return;
    }


    const cpf =
        campoCPF.value.trim();


    if (cpf === "") {

        mensagem.textContent =
            "Digite o CPF do usuário que deseja inativar.";

        mensagem.style.color = "red";

        return;

    }


    if (!validarCPF(cpf)) {

        mensagem.textContent =
            "CPF inválido. Verifique os números digitados.";

        mensagem.style.color = "red";

        return;

    }


    const confirmar =
        confirm(
            `Tem certeza que deseja inativar o usuário com CPF: ${cpf}?`
        );


    if (!confirmar) {
        return;
    }


    fetch(API_URL + "/usuarios", {

        method: "DELETE",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            cpf: cpf
        })

    })
    .then(function (resposta) {

        return resposta.json();

    })
    .then(function (dados) {

        mensagem.textContent = dados.mensagem;

        if (dados.sucesso) {

            mensagem.style.color = "green";

            limparCampos();

            const secaoDeletar = document.getElementById("secao-dados-deletar");
            if (secaoDeletar) {
                secaoDeletar.style.display = "none";
            }

        } else {

            mensagem.style.color = "red";

        }

    })
    .catch(function (erro) {

        console.error("Erro ao deletar:", erro);

        mensagem.textContent =
            "Erro ao conectar com o servidor.";

        mensagem.style.color = "red";

    });

}


/* =====================================================
   LIMPAR CAMPOS
===================================================== */

function limparCampos() {

    const cpf =
        document.getElementById("cpf");

    const nome =
        document.getElementById("nome");

    const profissao =
        document.getElementById("profissao");


    if (cpf) {
        cpf.value = "";
    }


    if (nome) {
        nome.value = "";
    }


    if (profissao) {
        profissao.value = "";
    }

}


/* =====================================================
   CARREGAR RESULTADOS E CONFIGURAR MÁSCARAS
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const campoCPF = document.getElementById("cpf");

        if (campoCPF) {
            campoCPF.addEventListener("input", function () {
                aplicarMascaraCPF(this);
            });
        }

        carregarResultados();

    }
);