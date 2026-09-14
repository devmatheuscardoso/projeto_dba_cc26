console.log("SCRIPT CARREGADO");

/* =====================================================
   SISTEMA DE CONTROLE DE EPIS E FUNCIONÁRIOS
   Front-end — HTML + CSS + JavaScript

   Conectado ao backend Python via API REST.
===================================================== */

const API_URL = window.location.origin + "/api";

let cpfVerificadoAtualizar = "";
let cpfVerificadoDeletar = "";

/* =====================================================
   CARREGAR PROFISSÕES E SETORES (SELECTS)
===================================================== */

function carregarProfissoesESetores(selectedProfissaoVal = null, selectedSetorId = null) {
    const campoProfissao = document.getElementById("profissao") || document.getElementById("profissao_id");
    const selectSetor = document.getElementById("setor_id");

    if (campoProfissao) {
        if (campoProfissao.tagName === "SELECT") {
            fetch(API_URL + "/profissoes")
                .then(res => res.json())
                .then(dados => {
                    if (dados.sucesso && dados.profissoes) {
                        campoProfissao.innerHTML = '<option value="">Selecione a profissão...</option>';
                        dados.profissoes.forEach(prof => {
                            const opt = document.createElement("option");
                            opt.value = prof.id;
                            opt.textContent = prof.nome;
                            if (selectedProfissaoVal && (prof.id == selectedProfissaoVal || prof.nome == selectedProfissaoVal)) {
                                opt.selected = true;
                            }
                            campoProfissao.appendChild(opt);
                        });
                    }
                })
                .catch(err => console.error("Erro ao carregar profissões:", err));
        } else if (selectedProfissaoVal) {
            campoProfissao.value = selectedProfissaoVal;
        }
    }

    if (selectSetor) {
        fetch(API_URL + "/setores")
            .then(res => res.json())
            .then(dados => {
                if (dados.sucesso && dados.setores) {
                    selectSetor.innerHTML = '<option value="">Selecione o setor...</option>';
                    dados.setores.forEach(setor => {
                        const opt = document.createElement("option");
                        opt.value = setor.id;
                        opt.textContent = setor.nome;
                        if (selectedSetorId && (setor.id == selectedSetorId || setor.nome == selectedSetorId)) {
                            opt.selected = true;
                        }
                        selectSetor.appendChild(opt);
                    });
                }
            })
            .catch(err => console.error("Erro ao carregar setores:", err));
    }
}

/* =====================================================
   LOGIN
===================================================== */

function fazerLogin() {
    const campoUsuario = document.getElementById("usuario");
    const campoSenha = document.getElementById("senha");
    const mensagem = document.getElementById("mensagem-login");

    if (!campoUsuario || !campoSenha || !mensagem) return;

    const usuario = campoUsuario.value.trim();
    const senha = campoSenha.value.trim();

    if (usuario === "" || senha === "") {
        mensagem.textContent = "Preencha todos os campos.";
        mensagem.style.color = "red";
        return;
    }

    fetch(API_URL + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario: usuario, senha: senha })
    })
    .then(r => r.json())
    .then(dados => {
        mensagem.textContent = dados.mensagem;
        if (dados.sucesso) {
            mensagem.style.color = "green";
            setTimeout(function () {
                window.location.href = "telas/consulta.html";
            }, 500);
        } else {
            mensagem.style.color = "red";
        }
    })
    .catch(erro => {
        console.error("Erro no login:", erro);
        mensagem.textContent = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";
    });
}

function mostrarSenha() {
    const campoSenha = document.getElementById("senha");
    if (!campoSenha) return;
    campoSenha.type = campoSenha.type === "password" ? "text" : "password";
}

/* =====================================================
   MÁSCARA AUTOMÁTICA DE CPF
===================================================== */

function aplicarMascaraCPF(input) {
    if (!input) return;
    let valor = input.value.replace(/\D/g, "");
    if (valor.length > 11) valor = valor.slice(0, 11);

    if (valor.length > 9) {
        valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})$/, "$1.$2.$3-$4");
    } else if (valor.length > 6) {
        valor = valor.replace(/^(\d{3})(\d{3})(\d{1,6})$/, "$1.$2.$3");
    } else if (valor.length > 3) {
        valor = valor.replace(/^(\d{3})(\d{1,3})$/, "$1.$2");
    }
    input.value = valor;
}

function validarCPF(cpfStr) {
    if (!cpfStr) return false;
    const digitos = String(cpfStr).replace(/\D/g, "");
    if (digitos.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(digitos)) return false;
    return true;
}

/* =====================================================
   LOGOUT / SAIR E NAVEGAÇÃO
===================================================== */

function fazerLogout() {
    sessionStorage.clear();
    window.location.href = "../index.html";
}

function abrirEdicao() { window.location.href = "editar.html"; }
function abrirAdicionar() { window.location.href = "adicionar.html"; }
function abrirAtualizar() { window.location.href = "atualizar.html"; }
function abrirDeletar() { window.location.href = "deletar.html"; }
function voltarConsulta() { window.location.href = "consulta.html"; }
function abrirRetiradaEPI() { window.location.href = "retirada-epi.html"; }
function abrirDevolucaoEPI() { window.location.href = "devolucao-epi.html"; }
function abrirEstoque() { window.location.href = "estoque.html"; }

/* =====================================================
   CONSULTAR FUNCIONÁRIO
===================================================== */

function consultarUsuario() {
    const campo = document.getElementById("nome-pesquisa");
    if (!campo) return;

    const nomePesquisa = campo.value.trim();
    if (nomePesquisa === "") {
        alert("Digite um nome, CPF ou Matrícula para realizar a consulta.");
        return;
    }

    sessionStorage.setItem("ultimaPesquisa", nomePesquisa);
    window.location.href = "resultados.html";
}

/* =====================================================
   MOSTRAR RESULTADOS
===================================================== */

function carregarResultados() {
    const tabela = document.getElementById("tabela-usuarios");
    const textoPesquisa = document.getElementById("texto-pesquisa");
    const total = document.getElementById("total-resultados");

    if (!tabela) return;

    const pesquisa = sessionStorage.getItem("ultimaPesquisa") || "";
    if (textoPesquisa) textoPesquisa.textContent = `"${pesquisa}"`;

    fetch(API_URL + "/funcionarios?nome=" + encodeURIComponent(pesquisa))
    .then(r => r.json())
    .then(dados => {
        if (!dados.sucesso) {
            tabela.innerHTML = `<tr><td colspan="7" style="text-align:center;">Erro ao buscar funcionários.</td></tr>`;
            return;
        }

        const resultados = dados.funcionarios || dados.usuarios || [];
        tabela.innerHTML = "";

        resultados.forEach(function (user) {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td><strong>${user.matricula || '-'}</strong></td>
                <td>${user.nome}</td>
                <td>${user.cpf}</td>
                <td>${user.email || '-'}</td>
                <td>${user.telefone || '-'}</td>
                <td>${user.setor_nome || user.setor || '-'}</td>
                <td>${user.profissao_nome || user.profissao || '-'}</td>
            `;
            tabela.appendChild(linha);
        });

        if (total) total.textContent = resultados.length;

        if (resultados.length === 0) {
            tabela.innerHTML = `<tr><td colspan="7" style="text-align:center;">Nenhum funcionário encontrado.</td></tr>`;
        }
    })
    .catch(erro => {
        console.error("Erro ao carregar resultados:", erro);
        tabela.innerHTML = `<tr><td colspan="7" style="text-align:center;">Erro ao conectar com o servidor.</td></tr>`;
    });
}

/* =====================================================
   BUSCAR FUNCIONÁRIO POR CPF OU MATRÍCULA
===================================================== */

function buscarUsuarioPorCPF() {
    const campoCPF = document.getElementById("cpf");
    const campoMatricula = document.getElementById("matricula");
    const campoNome = document.getElementById("nome");
    const campoEmail = document.getElementById("email");
    const campoTelefone = document.getElementById("telefone");
    const selectSetor = document.getElementById("setor_id");
    const selectProfissao = document.getElementById("profissao_id");
    const mensagem = document.getElementById("mensagem-edicao");
    const secaoDados = document.getElementById("secao-dados-usuario");
    const containerBotao = document.getElementById("container-botao-atualizar");
    const btnSalvar = document.getElementById("btn-salvar-atualizar");
    const btnReativar = document.getElementById("btn-reativar-usuario");

    if (!campoCPF || !mensagem) return;
    const cpf = campoCPF.value.trim();

    if (cpf === "") {
        mensagem.textContent = "Digite o CPF ou Matrícula para buscar.";
        mensagem.style.color = "red";
        cpfVerificadoAtualizar = "";
        cpfVerificadoDeletar = "";
        if (secaoDados) secaoDados.style.display = "none";
        if (containerBotao) containerBotao.style.display = "none";
        return;
    }

    fetch(API_URL + "/funcionarios/buscar-cpf?cpf=" + encodeURIComponent(cpf))
    .then(r => r.json())
    .then(dados => {
        if (dados.sucesso) {
            const u = dados.usuario || dados.funcionario;
            cpfVerificadoAtualizar = u.cpf;
            cpfVerificadoDeletar = u.cpf;

            if (campoMatricula) campoMatricula.value = u.matricula || "";
            if (campoNome) campoNome.value = u.nome || "";
            if (campoEmail) campoEmail.value = u.email || "";
            if (campoTelefone) campoTelefone.value = u.telefone || "";

            carregarProfissoesESetores(u.profissao_id || u.profissao, u.setor_id || u.setor);

            if (secaoDados) secaoDados.style.display = "block";
            if (containerBotao) containerBotao.style.display = "flex";
            if (btnSalvar) btnSalvar.style.display = "inline-block";
            if (btnReativar) btnReativar.style.display = "none";

            mensagem.textContent = "Funcionário encontrado! Altere os dados e clique em 'Salvar Alterações'.";
            mensagem.style.color = "green";

        } else if (dados.inativo) {
            const u = dados.usuario || dados.funcionario;
            cpfVerificadoAtualizar = u ? u.cpf : cpf;

            if (campoMatricula && u) campoMatricula.value = u.matricula || "";
            if (campoNome && u) campoNome.value = u.nome || "";
            if (campoEmail && u) campoEmail.value = u.email || "";
            if (campoTelefone && u) campoTelefone.value = u.telefone || "";

            if (u) carregarProfissoesESetores(u.profissao_id || u.profissao, u.setor_id || u.setor);

            if (secaoDados) secaoDados.style.display = "block";
            if (containerBotao) containerBotao.style.display = "flex";
            if (btnSalvar) btnSalvar.style.display = "none";
            if (btnReativar) btnReativar.style.display = "inline-block";

            mensagem.textContent = dados.mensagem || "Funcionário encontrado, mas inativo. Deseja reativá-lo?";
            mensagem.style.color = "#d35400";

        } else {
            cpfVerificadoAtualizar = "";
            cpfVerificadoDeletar = "";
            if (secaoDados) secaoDados.style.display = "none";
            if (containerBotao) containerBotao.style.display = "none";
            mensagem.textContent = dados.mensagem;
            mensagem.style.color = "red";
        }
    })
    .catch(erro => {
        console.error("Erro ao buscar por CPF/Matrícula:", erro);
        cpfVerificadoAtualizar = "";
        cpfVerificadoDeletar = "";
        if (secaoDados) secaoDados.style.display = "none";
        if (containerBotao) containerBotao.style.display = "none";
        mensagem.textContent = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";
    });
}

/* =====================================================
   VERIFICAR FUNCIONÁRIO PARA DELETAR
===================================================== */

function buscarUsuarioParaDeletar() {
    const campoCPF = document.getElementById("cpf");
    const mensagem = document.getElementById("mensagem-edicao");
    const secaoDeletar = document.getElementById("secao-dados-deletar");
    const containerBotao = document.getElementById("container-botao-deletar");
    const spanMatricula = document.getElementById("deletar-matricula");
    const spanNome = document.getElementById("deletar-nome");
    const spanSetor = document.getElementById("deletar-setor");
    const spanProfissao = document.getElementById("deletar-profissao");

    if (!campoCPF || !mensagem) return;
    const cpf = campoCPF.value.trim();

    if (cpf === "") {
        mensagem.textContent = "Digite o CPF ou Matrícula para verificar.";
        mensagem.style.color = "red";
        cpfVerificadoDeletar = "";
        if (secaoDeletar) secaoDeletar.style.display = "none";
        if (containerBotao) containerBotao.style.display = "none";
        return;
    }

    fetch(API_URL + "/funcionarios/buscar-cpf?cpf=" + encodeURIComponent(cpf))
    .then(r => r.json())
    .then(dados => {
        if (dados.sucesso) {
            const u = dados.usuario || dados.funcionario;
            cpfVerificadoDeletar = u.cpf;

            if (secaoDeletar) secaoDeletar.style.display = "block";
            if (containerBotao) containerBotao.style.display = "flex";

            if (spanMatricula) spanMatricula.textContent = u.matricula || "-";
            if (spanNome) spanNome.textContent = u.nome || "-";
            if (spanSetor) spanSetor.textContent = u.setor_nome || u.setor || "-";
            if (spanProfissao) spanProfissao.textContent = u.profissao_nome || u.profissao || "-";

            mensagem.textContent = "Funcionário encontrado! Clique em 'Confirmar e Inativar Funcionário' para prosseguir.";
            mensagem.style.color = "green";

        } else if (dados.inativo) {
            cpfVerificadoDeletar = "";
            if (secaoDeletar) secaoDeletar.style.display = "none";
            if (containerBotao) containerBotao.style.display = "none";
            mensagem.textContent = "Funcionário já se encontra inativo.";
            mensagem.style.color = "#d35400";

        } else {
            cpfVerificadoDeletar = "";
            if (secaoDeletar) secaoDeletar.style.display = "none";
            if (containerBotao) containerBotao.style.display = "none";
            mensagem.textContent = dados.mensagem;
            mensagem.style.color = "red";
        }
    })
    .catch(erro => {
        console.error("Erro ao buscar para deletar:", erro);
        cpfVerificadoDeletar = "";
        if (secaoDeletar) secaoDeletar.style.display = "none";
        if (containerBotao) containerBotao.style.display = "none";
        mensagem.textContent = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";
    });
}

/* =====================================================
   ADICIONAR FUNCIONÁRIO
===================================================== */

function adicionarUsuario() {
    const campoMatricula = document.getElementById("matricula");
    const campoCPF = document.getElementById("cpf");
    const campoNome = document.getElementById("nome");
    const campoEmail = document.getElementById("email");
    const campoTelefone = document.getElementById("telefone");
    const selectSetor = document.getElementById("setor_id");
    const campoProfissao = document.getElementById("profissao") || document.getElementById("profissao_id");
    const mensagem = document.getElementById("mensagem-edicao");
    const btnRedirecionar = document.getElementById("container-redirecionar-atualizar");

    if (!campoCPF || !campoNome || !mensagem) return;

    const matricula = campoMatricula ? campoMatricula.value.trim() : "";
    const cpf = campoCPF.value.trim();
    const nome = campoNome.value.trim();
    const email = campoEmail ? campoEmail.value.trim() : "";
    const telefone = campoTelefone ? campoTelefone.value.trim() : "";
    const setor_id = selectSetor ? selectSetor.value : "";
    const profissao = campoProfissao ? campoProfissao.value.trim() : "";

    if (cpf === "" || nome === "" || !setor_id || !profissao) {
        mensagem.textContent = "Preencha todos os campos obrigatórios (CPF, Nome, Setor e Profissão).";
        mensagem.style.color = "red";
        return;
    }

    if (!validarCPF(cpf)) {
        mensagem.textContent = "CPF inválido. Verifique os números digitados.";
        mensagem.style.color = "red";
        return;
    }

    fetch(API_URL + "/funcionarios", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            matricula: matricula,
            cpf: cpf,
            nome: nome,
            email: email,
            telefone: telefone,
            setor_id: setor_id,
            profissao: profissao,
            profissao_id: profissao
        })
    })
    .then(r => r.json())
    .then(dados => {
        mensagem.textContent = dados.mensagem;
        if (dados.sucesso) {
            mensagem.style.color = "green";
            if (btnRedirecionar) btnRedirecionar.style.display = "none";
            limparCampos();
        } else if (dados.inativo) {
            mensagem.style.color = "#d35400";
            if (btnRedirecionar) btnRedirecionar.style.display = "flex";
            if (confirm("Funcionário encontrado, mas inativo. Deseja ir para a página de atualização para reativá-lo?")) {
                irParaAtualizar(cpf);
            }
        } else {
            mensagem.style.color = "red";
            if (btnRedirecionar) btnRedirecionar.style.display = "none";
        }
    })
    .catch(erro => {
        console.error("Erro ao adicionar:", erro);
        mensagem.textContent = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";
    });
}

/* =====================================================
   REATIVAR / ATUALIZAR FUNCIONÁRIO
===================================================== */

function reativarUsuario() {
    atualizarUsuario();
}

function irParaAtualizar(cpfParam) {
    const cpf = cpfParam || (document.getElementById("cpf") ? document.getElementById("cpf").value.trim() : "");
    window.location.href = "atualizar.html?cpf=" + encodeURIComponent(cpf);
}

function atualizarUsuario() {
    const campoMatricula = document.getElementById("matricula");
    const campoCPF = document.getElementById("cpf");
    const campoNome = document.getElementById("nome");
    const campoEmail = document.getElementById("email");
    const campoTelefone = document.getElementById("telefone");
    const selectSetor = document.getElementById("setor_id");
    const campoProfissao = document.getElementById("profissao") || document.getElementById("profissao_id");
    const mensagem = document.getElementById("mensagem-edicao");

    if (!campoCPF || !campoNome || !mensagem) return;

    const matricula = campoMatricula ? campoMatricula.value.trim() : "";
    const cpf = campoCPF.value.trim();
    const nome = campoNome.value.trim();
    const email = campoEmail ? campoEmail.value.trim() : "";
    const telefone = campoTelefone ? campoTelefone.value.trim() : "";
    const setor_id = selectSetor ? selectSetor.value : "";
    const profissao = campoProfissao ? campoProfissao.value.trim() : "";

    if (cpf === "" || nome === "") {
        mensagem.textContent = "Preencha ao menos o CPF/Matrícula e o Nome.";
        mensagem.style.color = "red";
        return;
    }

    if (cpfVerificadoAtualizar && cpf !== cpfVerificadoAtualizar) {
        mensagem.textContent = "Clique em 'Buscar' para verificar o funcionário antes de salvar.";
        mensagem.style.color = "red";
        return;
    }

    fetch(API_URL + "/funcionarios", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            matricula: matricula,
            cpf: cpf,
            nome: nome,
            email: email,
            telefone: telefone,
            setor_id: setor_id,
            profissao: profissao,
            profissao_id: profissao
        })
    })
    .then(r => r.json())
    .then(dados => {
        if (dados.sucesso) {
            mensagem.textContent = dados.mensagem || "Cadastro atualizado com sucesso!";
            mensagem.style.color = "green";
            limparCampos();
        } else {
            mensagem.textContent = dados.mensagem;
            mensagem.style.color = "red";
        }
    })
    .catch(erro => {
        console.error("Erro ao atualizar:", erro);
        mensagem.textContent = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";
    });
}

/* =====================================================
   DELETAR FUNCIONÁRIO (INATIVAÇÃO LÓGICA)
===================================================== */

function deletarUsuario() {
    const campoCPF = document.getElementById("cpf");
    const mensagem = document.getElementById("mensagem-edicao");

    if (!campoCPF || !mensagem) return;
    const cpf = campoCPF.value.trim();

    if (cpf === "" && !cpfVerificadoDeletar) {
        mensagem.textContent = "Digite o CPF ou Matrícula do funcionário a inativar.";
        mensagem.style.color = "red";
        return;
    }

    const valorParaEnviar = cpfVerificadoDeletar || cpf;

    const confirmar = confirm(`Tem certeza que deseja inativar o funcionário (${valorParaEnviar})?`);
    if (!confirmar) return;

    fetch(API_URL + "/funcionarios", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf: valorParaEnviar, matricula: valorParaEnviar })
    })
    .then(r => r.json())
    .then(dados => {
        if (dados.sucesso) {
            mensagem.textContent = dados.mensagem || "Funcionário inativado com sucesso!";
            mensagem.style.color = "green";
            limparCampos();
        } else {
            mensagem.textContent = dados.mensagem;
            mensagem.style.color = "red";
        }
    })
    .catch(erro => {
        console.error("Erro ao deletar:", erro);
        mensagem.textContent = "Erro ao conectar com o servidor.";
        mensagem.style.color = "red";
    });
}

/* =====================================================
   LIMPAR CAMPOS
===================================================== */

function limparCampos() {
    cpfVerificadoAtualizar = "";
    cpfVerificadoDeletar = "";

    const ids = ["cpf", "matricula", "nome", "email", "telefone"];
    ids.forEach(id => {
        const elem = document.getElementById(id);
        if (elem) elem.value = "";
    });

    const secaoDados = document.getElementById("secao-dados-usuario");
    const containerBotaoAtualizar = document.getElementById("container-botao-atualizar");
    const btnSalvar = document.getElementById("btn-salvar-atualizar");
    const btnReativar = document.getElementById("btn-reativar-usuario");
    const btnRedirecionar = document.getElementById("container-redirecionar-atualizar");
    const secaoDeletar = document.getElementById("secao-dados-deletar");
    const containerBotaoDeletar = document.getElementById("container-botao-deletar");

    if (secaoDados) secaoDados.style.display = "none";
    if (containerBotaoAtualizar) containerBotaoAtualizar.style.display = "none";
    if (btnSalvar) btnSalvar.style.display = "inline-block";
    if (btnReativar) btnReativar.style.display = "none";
    if (btnRedirecionar) btnRedirecionar.style.display = "none";
    if (secaoDeletar) secaoDeletar.style.display = "none";
    if (containerBotaoDeletar) containerBotaoDeletar.style.display = "none";
}

/* =====================================================
   RETIRADA DE EPI
===================================================== */

function carregarEpisRetirada() {
    const tabela = document.getElementById("tabela-retirada-corpo");
    if (!tabela) return;

    fetch(API_URL + "/epis")
    .then(r => r.json())
    .then(dados => {
        if (!dados.sucesso) {
            tabela.innerHTML = `<tr><td colspan="3">Erro: ${dados.mensagem}</td></tr>`;
            return;
        }

        tabela.innerHTML = "";
        dados.epis.forEach(epi => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${epi.codigo} - ${epi.nome} (${epi.tamanho})</td>
                <td>
                    <span class="estoque-quantidade" style="${epi.quantidade <= epi.estoque_minimo ? 'color: red;' : ''}">${epi.quantidade}</span>
                </td>
                <td>
                    <input type="number" class="quantidade-retirada" data-epi="${epi.id}" min="0" max="${epi.quantidade}" placeholder="0" value="0">
                </td>
            `;
            tabela.appendChild(linha);
        });
    })
    .catch(err => {
        tabela.innerHTML = `<tr><td colspan="3">Erro de conexão</td></tr>`;
    });
}

function realizarRetirada() {
    const cpf = document.getElementById("cpf-retirada").value.trim();
    const mensagem = document.getElementById("mensagem-retirada");
    if (!mensagem) return;

    if (cpf === "") {
        mensagem.textContent = "Digite o CPF ou Matrícula do funcionário.";
        mensagem.style.color = "red";
        return;
    }

    const campos = document.querySelectorAll(".quantidade-retirada");
    let itens = [];

    campos.forEach(campo => {
        const quantidade = Number(campo.value);
        if (quantidade > 0) {
            itens.push({
                epi_id: campo.getAttribute("data-epi"),
                quantidade: quantidade
            });
        }
    });

    if (itens.length === 0) {
        mensagem.textContent = "Informe a quantidade de pelo menos um EPI para retirar.";
        mensagem.style.color = "red";
        return;
    }

    fetch(API_URL + "/retiradas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpf: cpf, matricula: cpf, itens: itens })
    })
    .then(r => r.json())
    .then(dados => {
        mensagem.textContent = dados.mensagem;
        if (dados.sucesso) {
            mensagem.style.color = "green";
            carregarEpisRetirada();
            document.getElementById("cpf-retirada").value = "";
        } else {
            mensagem.style.color = "red";
        }
    })
    .catch(err => {
        mensagem.textContent = "Erro de conexão.";
        mensagem.style.color = "red";
    });
}

/* =====================================================
   DEVOLUÇÃO DE EPI
===================================================== */

function buscarItensParaDevolucao() {
    const cpfInput = document.getElementById("cpf-devolucao");
    const select = document.getElementById("epi-devolucao");
    const mensagem = document.getElementById("mensagem-devolucao");
    const inputQtd = document.getElementById("quantidade-devolucao");

    if (!cpfInput || !select || !mensagem) return;
    const cpf = cpfInput.value.trim();

    if (cpf === "") {
        mensagem.textContent = "Digite o CPF ou Matrícula do funcionário.";
        mensagem.style.color = "red";
        return;
    }

    select.innerHTML = '<option value="">Carregando...</option>';
    if (inputQtd) inputQtd.value = "";

    fetch(API_URL + "/retiradas?cpf=" + encodeURIComponent(cpf))
    .then(r => r.json())
    .then(dados => {
        if (!dados.sucesso) {
            mensagem.textContent = dados.mensagem;
            mensagem.style.color = "red";
            select.innerHTML = '<option value="">Erro ao carregar itens</option>';
            return;
        }

        if (!dados.itens || dados.itens.length === 0) {
            mensagem.textContent = "Nenhum EPI pendente de devolução para este funcionário.";
            mensagem.style.color = "orange";
            select.innerHTML = '<option value="">Nenhum item pendente</option>';
            return;
        }

        mensagem.textContent = "Itens encontrados. Selecione o EPI para devolver.";
        mensagem.style.color = "green";
        select.innerHTML = '<option value="">Selecione o EPI...</option>';
        
        dados.itens.forEach(item => {
            const dataRetirada = item.data_retirada ? new Date(item.data_retirada).toLocaleDateString("pt-BR") : "-";
            select.innerHTML += `<option value="${item.item_retirada_id}" data-max="${item.quantidade}">
                ${item.nome} (Qtd: ${item.quantidade}) - Retirado em: ${dataRetirada}
            </option>`;
        });

        select.onchange = function() {
            const opt = this.options[this.selectedIndex];
            const max = opt ? opt.getAttribute('data-max') : null;
            if (max) {
                if (inputQtd) {
                    inputQtd.max = max;
                    inputQtd.value = max;
                }
            } else {
                if (inputQtd) inputQtd.value = "";
            }
        };

        if (dados.itens.length === 1) {
            select.selectedIndex = 1;
            select.onchange();
        }
    })
    .catch(err => {
        console.error("Erro ao buscar retiradas:", err);
        mensagem.textContent = "Erro de conexão com o servidor.";
        mensagem.style.color = "red";
        select.innerHTML = '<option value="">Erro ao carregar itens</option>';
    });
}

function realizarDevolucao() {
    const selectEPI = document.getElementById("epi-devolucao");
    const inputQtd = document.getElementById("quantidade-devolucao");
    const mensagem = document.getElementById("mensagem-devolucao");

    if (!selectEPI || !inputQtd || !mensagem) return;

    const itemRetiradaId = selectEPI.value;
    const quantidade = Number(inputQtd.value);

    if (!itemRetiradaId) {
        mensagem.textContent = "Selecione o EPI para devolução (busque o funcionário primeiro).";
        mensagem.style.color = "red";
        return;
    }

    const optSelecionada = selectEPI.options[selectEPI.selectedIndex];
    const maxPermitido = optSelecionada ? Number(optSelecionada.getAttribute('data-max')) : 0;

    if (isNaN(quantidade) || quantidade <= 0) {
        mensagem.textContent = "Digite uma quantidade válida (maior que 0).";
        mensagem.style.color = "red";
        return;
    }

    if (maxPermitido > 0 && quantidade > maxPermitido) {
        mensagem.textContent = `A quantidade não pode exceder o total retirado (${maxPermitido}).`;
        mensagem.style.color = "red";
        return;
    }

    fetch(API_URL + "/devolucoes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_retirada_id: itemRetiradaId, quantidade: quantidade })
    })
    .then(r => r.json())
    .then(dados => {
        mensagem.textContent = dados.mensagem;
        if (dados.sucesso) {
            mensagem.style.color = "green";
            inputQtd.value = "";
            buscarItensParaDevolucao();
        } else {
            mensagem.style.color = "red";
        }
    })
    .catch(err => {
        console.error("Erro ao realizar devolução:", err);
        mensagem.textContent = "Erro de conexão com o servidor.";
        mensagem.style.color = "red";
    });
}

/* =====================================================
   ESTOQUE DE EPI
===================================================== */

function carregarEstoque() {
    const tabela = document.getElementById("tabela-estoque-corpo");
    if (!tabela) return;

    fetch(API_URL + "/epis")
    .then(r => r.json())
    .then(dados => {
        if (!dados.sucesso) {
            tabela.innerHTML = `<tr><td colspan="7">Erro: ${dados.mensagem}</td></tr>`;
            return;
        }

        tabela.innerHTML = "";
        dados.epis.forEach(epi => {
            const emBaixa = epi.quantidade <= epi.estoque_minimo;
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${epi.codigo}</td>
                <td>${epi.nome}</td>
                <td>${epi.ca}</td>
                <td>${epi.tamanho}</td>
                <td style="font-weight: bold; ${emBaixa ? 'color: red;' : ''}">${epi.quantidade}</td>
                <td>${epi.estoque_minimo}</td>
                <td>
                    <span style="${emBaixa ? 'color: red; font-weight: bold;' : 'color: green; font-weight: bold;'}">
                        ${emBaixa ? 'BAIXO' : 'OK'}
                    </span>
                </td>
            `;
            tabela.appendChild(linha);
        });
    })
    .catch(err => {
        tabela.innerHTML = `<tr><td colspan="7">Erro de conexão</td></tr>`;
    });
}

/* =====================================================
   INICIALIZAÇÃO DA PÁGINA
===================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const campoCPF = document.getElementById("cpf");
    if (campoCPF) {
        campoCPF.addEventListener("input", function () {
            aplicarMascaraCPF(this);
        });
    }

    carregarProfissoesESetores();

    const urlParams = new URLSearchParams(window.location.search);
    const cpfParam = urlParams.get("cpf");

    if (cpfParam && campoCPF) {
        campoCPF.value = cpfParam;
        aplicarMascaraCPF(campoCPF);
        if (typeof buscarUsuarioPorCPF === "function" && document.getElementById("secao-dados-usuario")) {
            buscarUsuarioPorCPF();
        }
    }

    carregarResultados();
    if (document.getElementById("tabela-estoque-corpo")) carregarEstoque();
    if (document.getElementById("tabela-retirada-corpo")) carregarEpisRetirada();
});

window.formatarCPF = aplicarMascaraCPF;
window.sairSistema = fazerLogout;

const consultarFuncionario = consultarUsuario;
const adicionarFuncionario = adicionarUsuario;
const atualizarFuncionario = atualizarUsuario;
const deletarFuncionario = deletarUsuario;
const buscarFuncionarioPorCPF = buscarUsuarioPorCPF;
const buscarFuncionarioParaDeletar = buscarUsuarioParaDeletar;
const reativarFuncionario = reativarUsuario;

