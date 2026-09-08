# Projeto DBA CC26 — Sistema de Controle e Gestão de EPIs

Sistema web completo para controle de estoque, fornecimento e rastreio de Equipamentos de Proteção Individual (EPIs) para colaboradores, desenvolvido em Python puro (sem frameworks), MySQL nativo e interface web (HTML5/CSS3/JavaScript).

---

## 1. Identificação Institucional e Integrantes

* **Instituição:** Universidade Paulista (UNIP)
* **Curso:** Bacharelado em Ciência da Computação
* **Disciplina:** Banco de Dados (NP1)
* **Semestre/Ano:** 3º Semestre / 2º Semestre de 2026
* **Integrantes do Grupo:**
  * Flávio Augusto Rodrigues de Oliveira - R950239
  * Henry Vinícius Barros Salgado - H789IG0
  * Joao Batista Suzana Filho - R956IH4
  * Lucas Marçal de Oliveira - R879941
  * Matheus Henrique Aparecido Cardoso - H77IFE3

---

## 2. Descrição do Projeto

### Apresentação do Tema
O **Sistema de Controle de EPIs** é uma aplicação corporativa e industrial destinada a gerenciar o cadastro de funcionários, o inventário de Equipamentos de Proteção Individual e o registro detalhado de retiradas e devoluções, visando conformidade com as normas de segurança do trabalho.

### Arquitetura e Tecnologias
- **Backend**: Python 3.8+ utilizando apenas bibliotecas nativas (`http.server`, `json`, `re`, `urllib`) e o driver oficial `mysql-connector-python`.
- **Banco de Dados**: MySQL Server 8.0+ com engine InnoDB e charset `utf8mb4`.
- **Frontend**: Interface web desenvolvida em HTML5, CSS3 estilizado e JavaScript puro (ES6+ Vanilla).

### Regras de Negócio e Funcionalidades
- **Normalização e Integridade Referencial**: Mapeamento completo de profissões (`profissoes`) e setores (`setores`), garantindo que cada funcionário pertença a entidades válidas via chaves estrangeiras.
- **Rastreabilidade de Funcionários**: Cadastro de colaboradores associando matrícula (única), CPF, e-mail, telefone, setor e profissão.
- **Gestão de Estoque de EPIs**: Controle rigoroso de estoque atual e ponto de reposição (`estoque_minimo`), contendo código do item, Certificado de Aprovação (CA) e tamanho.
- **Movimentação de Retiradas**: Mapeamento do fluxo de entrega de equipamentos vinculando o funcionário (`retiradas`) aos itens solicitados (`itens_retirada`), controlando datas e quantidades.
- **Controle de Status de Devolução**: Monitoramento dos itens com status `RETIRADO`, `DEVOLVIDO` ou `ATRASADO`.
- **Inativação Lógica (*Soft Delete*)**: O sistema utiliza o atributo `ativo` (`1` para ativo e `0` para inativo) em todas as tabelas principais para preservar o histórico operacional.
- **Autenticação Administrativa**: O acesso ao painel de gerenciamento exige autenticação prévia de usuário administrador na tabela `admins`.

---

## 3. Estrutura do Projeto

```text
projeto_dba_cc26/
├── ConsultaUsuarios/              # Arquivos de Frontend (HTML/CSS/JS)
│   ├── css/                       # Estilos CSS da aplicação
│   ├── imagem/                    # Recursos de imagem e logotipos
│   ├── js/                        # Scripts JavaScript (máscaras, chamadas API)
│   ├── telas/                     # Páginas HTML dos fluxos
│   └── index.html                 # Tela de Login Administrativo
├── backend/                       # Servidor Python e Configurações
│   ├── config.py                  # Credenciais do banco e porta do servidor
│   ├── init_db.sql                # Script DDL e cargas iniciais do banco
│   └── servidor.py                # Servidor HTTP nativo e API REST
├── docs/                          # Documentações e Prints de Evidência
│   └── prints/                    # Prints de tela para o README
│       ├── 01_select_funcionarios.png
│       ├── 02_select_epis.png
│       ├── 03_select_retiradas.png
│       └── 04_interface_web.png
├── .gitignore                     # Arquivos ignorados pelo Git
└── README.md                      # Documentação do projeto
```

---

## 4. Modelagem de Dados

### Diagrama Entidade-Relacionamento (DER)

``` mermaid
erDiagram
    PROFISSOES ||--o{ FUNCIONARIOS : possui
    SETORES ||--o{ FUNCIONARIOS : alocado
    FUNCIONARIOS ||--o{ RETIRADAS : realiza
    RETIRADAS ||--|{ ITENS_RETIRADA : contem
    EPIS ||--o{ ITENS_RETIRADA : composto

    PROFISSOES {
        INT id PK
        VARCHAR nome UK
        VARCHAR descricao
        TINYINT ativo
    }

    SETORES {
        INT id PK
        VARCHAR nome UK
        VARCHAR descricao
        TINYINT ativo
    }

    FUNCIONARIOS {
        INT id PK
        VARCHAR matricula UK
        VARCHAR nome
        VARCHAR cpf UK
        VARCHAR email UK
        VARCHAR telefone
        INT profissao_id FK
        INT setor_id FK
        TINYINT ativo
    }

    EPIS {
        INT id PK
        VARCHAR codigo UK
        VARCHAR nome
        VARCHAR ca
        VARCHAR tamanho
        INT quantidade
        INT estoque_minimo
        TINYINT ativo
    }

    RETIRADAS {
        INT id PK
        INT funcionario_id FK
        DATETIME data_retirada
        VARCHAR observacao
    }

    ITENS_RETIRADA {
        INT id PK
        INT retirada_id FK
        INT epi_id FK
        INT quantidade
        DATETIME data_devolucao
        ENUM status
        VARCHAR observacao
    }

    ADMINS {
        INT id PK
        VARCHAR usuario UK
        VARCHAR senha
        TINYINT ativo
    }
```

### Script DDL e DML Completo

```sql
/* =====================================================
   SCRIPT DDL/DML — BANCO DE DADOS CONTROLE DE EPIS
   Disciplina: Banco de Dados (NP1) - UNIP CC26
===================================================== */

CREATE DATABASE IF NOT EXISTS controle_epis
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE controle_epis;

/* =====================================================
   1. TABELA DE PROFISSÕES
===================================================== */
CREATE TABLE IF NOT EXISTS profissoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(255),
    ativo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   2. TABELA DE SETORES
===================================================== */
CREATE TABLE IF NOT EXISTS setores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao VARCHAR(255),
    ativo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   3. TABELA DE FUNCIONÁRIOS
===================================================== */
CREATE TABLE IF NOT EXISTS funcionarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricula VARCHAR(30) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    profissao_id INT NOT NULL,
    setor_id INT NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,

    INDEX idx_funcionario_nome (nome),

    CONSTRAINT fk_funcionarios_profissao
        FOREIGN KEY (profissao_id)
        REFERENCES profissoes(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_funcionario_setor
        FOREIGN KEY (setor_id)
        REFERENCES setores(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   4. TABELA DE EPIs
===================================================== */
CREATE TABLE IF NOT EXISTS epis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    ca VARCHAR(50) NOT NULL,
    tamanho VARCHAR(20),
    quantidade INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 0,
    ativo TINYINT(1) NOT NULL DEFAULT 1,

    INDEX idx_epi_nome (nome)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   5. TABELA DE RETIRADAS
===================================================== */
CREATE TABLE IF NOT EXISTS retiradas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    funcionario_id INT NOT NULL,
    data_retirada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observacao VARCHAR(255),

    CONSTRAINT fk_retirada_funcionario
        FOREIGN KEY (funcionario_id)
        REFERENCES funcionarios(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   6. TABELA DE ITENS DA RETIRADA
===================================================== */
CREATE TABLE IF NOT EXISTS itens_retirada (
    id INT AUTO_INCREMENT PRIMARY KEY,
    retirada_id INT NOT NULL,
    epi_id INT NOT NULL,
    quantidade INT NOT NULL DEFAULT 1,
    data_devolucao DATETIME,
    status ENUM('RETIRADO', 'DEVOLVIDO', 'ATRASADO') NOT NULL DEFAULT 'RETIRADO',
    observacao VARCHAR(255),

    INDEX idx_item_status (status),

    CONSTRAINT fk_item_retirada
        FOREIGN KEY (retirada_id)
        REFERENCES retiradas(id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_item_epi
        FOREIGN KEY (epi_id)
        REFERENCES epis(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   7. TABELA DE ADMINISTRADORES
===================================================== */
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =====================================================
   CARGA INICIAL DE DADOS (DML)
===================================================== */

INSERT INTO profissoes (nome, descricao) VALUES
    ('Operador de Produção', 'Responsável por atividades relacionadas à produção'),
    ('Técnico de Segurança', 'Responsável pelas atividades de segurança do trabalho'),
    ('Almoxarife', 'Responsável pelo controle e armazenamento de materiais'),
    ('Supervisor de Produção', 'Responsável pela supervisão das atividades de produção'),
    ('Técnico de Manutenção', 'Responsável pela manutenção de máquinas e equipamentos');

INSERT INTO setores (nome, descricao) VALUES
    ('Produção', 'Setor responsável pela produção'),
    ('Almoxarifado', 'Setor responsável pelo armazenamento e controle de estoque'),
    ('Manutenção', 'Setor responsável pela manutenção de equipamentos'),
    ('Qualidade', 'Setor responsável pelo controle de qualidade'),
    ('Segurança do Trabalho', 'Setor responsável pela segurança dos funcionários');

INSERT INTO funcionarios
    (matricula, nome, cpf, email, telefone, profissao_id, setor_id)
VALUES
    (
        'FUNC-001',
        'João da Silva',
        '123.456.789-01',
        'joao.silva@email.com',
        '(11) 99999-0001',
        (SELECT id FROM profissoes
         WHERE nome = 'Operador de Produção'),
        (SELECT id FROM setores
         WHERE nome = 'Produção')
    ),
    (
        'FUNC-002',
        'Pedro Santos',
        '234.567.890-12',
        'pedro.santos@email.com',
        '(11) 99999-0002',
        (SELECT id FROM profissoes
         WHERE nome = 'Técnico de Segurança'),
        (SELECT id FROM setores
         WHERE nome = 'Segurança do Trabalho')
    ),
    (
        'FUNC-003',
        'Carlos Oliveira',
        '345.678.901-23',
        'carlos.oliveira@email.com',
        '(11) 99999-0003',
        (SELECT id FROM profissoes
         WHERE nome = 'Almoxarife'),
        (SELECT id FROM setores
         WHERE nome = 'Almoxarifado')
    ),
    (
        'FUNC-004',
        'Marcos Almeida',
        '456.789.012-34',
        'marcos.almeida@email.com',
        '(11) 99999-0004',
        (SELECT id FROM profissoes
         WHERE nome = 'Supervisor de Produção'),
        (SELECT id FROM setores
         WHERE nome = 'Produção')
    ),
    (
        'FUNC-005',
        'Lucas Souza',
        '567.890.123-45',
        'lucas.souza@email.com',
        '(11) 99999-0005',
        (SELECT id FROM profissoes
         WHERE nome = 'Técnico de Manutenção'),
        (SELECT id FROM setores
         WHERE nome = 'Manutenção')
    );

INSERT INTO epis
    (codigo, nome, descricao, ca, tamanho, quantidade, estoque_minimo)
VALUES
    ('EPI-001', 'Capacete de Segurança',
     'Capacete para proteção da cabeça', '12345', 'Único', 20, 5),

    ('EPI-002', 'Óculos de Proteção',
     'Óculos para proteção dos olhos', '23456', 'Único', 30, 10),

    ('EPI-003', 'Luva de Proteção',
     'Luva para proteção das mãos', '34567', 'M', 50, 10),

    ('EPI-004', 'Botina de Segurança',
     'Botina para proteção dos pés', '45678', '40', 15, 5),

    ('EPI-005', 'Protetor Auricular',
     'Proteção contra ruídos', '56789', 'Único', 25, 5),

    ('EPI-006', 'Máscara Respiratória',
     'Proteção respiratória contra partículas', '67890', 'Único', 40, 10);

INSERT INTO admins (usuario, senha) VALUES
    ('admin', '1234');
```

---

## 5. Documentação da API REST

| Método | Endpoint | Descrição | Corpo / Parâmetros |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/login` | Autenticação do administrador | `{ "usuario": "...", "senha": "..." }` |
| `GET` | `/api/funcionarios` | Lista funcionários ou filtra por nome/CPF/matrícula | `?busca=...` |
| `POST` | `/api/funcionarios` | Insere novo funcionário | `{ "matricula": "...", "nome": "...", "cpf": "...", "email": "...", "telefone": "...", "profissao_id": 1, "setor_id": 1 }` |
| `PUT` | `/api/funcionarios` | Atualiza dados do funcionário | `{ "id": 1, "nome": "...", "email": "...", "telefone": "..." }` |
| `DELETE` | `/api/funcionarios` | Inativação lógica (*soft delete*) do funcionário | `{ "id": 1 }` |
| `GET` | `/api/epis` | Lista equipamentos de proteção cadastrados | `?nome=...` |
| `POST` | `/api/epis` | Cadastra novo EPI | `{ "codigo": "...", "nome": "...", "ca": "...", "quantidade": 10 }` |
| `POST` | `/api/retiradas` | Registra movimentação de entrega de EPI | `{ "funcionario_id": 1, "epis": [{ "epi_id": 1, "quantidade": 1 }] }` |

---

## 6. Guia de Instalação e Execução

### Pré-requisitos
- **Python 3.8+** instalado.
- **MySQL Server 8.0+** em execução local na porta `3306`.

### Passo 1: Clonar o Repositório
```bash
git clone [https://github.com/devmatheuscardoso/projeto_dba_cc26.git](https://github.com/devmatheuscardoso/projeto_dba_cc26.git)
cd projeto_dba_cc26
```

### Passo 2: Instalar Dependências Python
Instale a biblioteca de conexão do MySQL:
```bash
pip install mysql-connector-python
```

### Passo 3: Configurar Credenciais do MySQL
Abra o arquivo `backend/config.py` e configure as credenciais do seu ambiente MySQL:
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "SuaSenhaDoMySQL",  # <-- Altere para a sua senha
    "database": "controle_epis",
    "charset":  "utf8mb4",
}

PORTA_SERVIDOR = 8080
```

### Passo 4: Inicializar o Banco de Dados
Certifique-se de salvar o script SQL fornecido na Seção 4 no arquivo `backend/init_db.sql`. Em seguida, execute-o para criar a base e os dados de teste:
```bash
mysql -u root -p < backend/init_db.sql
```
*(Também é possível executar o conteúdo de `backend/init_db.sql` via MySQL Workbench, DBeaver ou phpMyAdmin).*

### Passo 5: Executar o Servidor Python
Inicie o servidor HTTP nativo:
```bash
python backend/servidor.py
```

### Passo 6: Acessar a Interface Web
Abra o navegador de sua preferência e acesse:
```text
http://localhost:8080
```

- **Usuário Admin Padrão**: `admin`
- **Senha**: `1234`
  
## 7. Evidências Visuais e Testes de Persistência
#### 1. Inserção de Funcionários e Consulta de Integridade
![Consulta Funcionarios](docs/prints/01_select_funcionarios.png)
*Demonstração da tabela `funcionarios` com os relacionamentos de `setor_id` e `profissao_id` integrados.*
#### 2. Controle de Estoque de EPIs
![Consulta EPIs](docs/prints/02_select_epis.png)
*Visualização do saldo atual de equipamentos e ponto de reposição (`estoque_minimo`).*
#### 3. Registro de Retirada e Devolução
![Movimentação Retirada](docs/prints/03_select_retiradas.png)
![Controle de Devolução](docs/prints/03b_select_devolucao.png)
*Histórico de movimentações na tabela `itens_retirada` com controle de status (`RETIRADO` / `DEVOLVIDO`).*
#### 4. Execução da Interface Web
![Interface do Sistema](docs/prints/04_interface_web.png)
*Painel de controle do sistema rodando na porta 8080.*
