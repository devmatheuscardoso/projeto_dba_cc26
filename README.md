# Projeto DBA CC26 — Sistema de Controle e Gestão de EPIs

Sistema web completo para controle de estoque, fornecimento e rastreio de Equipamentos de Proteção Individual (EPIs) para colaboradores, desenvolvido em Python puro (sem frameworks), MySQL nativo e interface web (HTML5/CSS3/JavaScript).

---

## 1. Identificação Institucional e Integrantes

* **Instituição:** Universidade Paulista (UNIP)
* **Curso:** Bacharelado em Ciência da Computação
* **Disciplina:** Banco de Dados (NP1)
* **Semestre:** 3º Semestre / 4º Semestre 
* **Ano:** 2026
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
- **Backend**: Python 3.8+ utilizando apenas bibliotecas nativas (`http.server`, `json`, `re`, `urllib`) e suporte a múltiplos drivers (`mysql-connector-python`, `sqlite3`, `pyodbc`).
- **Banco de Dados**: Suporte nativo e configurável para MySQL Server 8.0+, Microsoft SQL Server ou SQLite via variável de ambiente.
- **Frontend**: Interface web desenvolvida em HTML5, CSS3 estilizado e JavaScript puro (ES6+ Vanilla).

### Regras de Negócio e Funcionalidades
- **Normalização e Integridade Referencial**: Mapeamento completo de profissões (`profissoes`) e setores (`setores`), garantindo que cada funcionário pertença a entidades válidas via chaves estrangeiras.
- **Identificação e Busca Híbrida (CPF ou Matrícula)**: Todas as pesquisas, consultas, atualização, inativação/deletar, retiradas e devoluções aceitam o **CPF** (com ou sem formatação `xxx.xxx.xxx-xx`) ou a **Matrícula** (ex: `FUNC-001`).
- **Auto-complete Inteligente de Matrícula**: Nos campos de busca e cadastro, digitar `func` ou `FUNC` completa automaticamente com o hífen e prefixo `FUNC-` facilitando a digitação rápida.
- **Entrada Flexível de Profissão vs. Seleção de Setor**: O setor é selecionado via opções predefinidas (`setores`), enquanto a profissão pode ser digitada livremente pelo usuário na interface e o sistema cadastra/associa automaticamente na tabela `profissoes` gerando uma descrição padronizada da categoria.
- **Rastreabilidade e Formatação de Funcionários**: Cadastro de colaboradores associando matrícula (única), CPF, e-mail, telefone, setor e profissão. Caso a matrícula não seja informada no cadastro, o sistema gera automaticamente no padrão `FUNC-xxx`.
- **Gestão de Estoque de EPIs**: Controle rigoroso de estoque atual e ponto de reposição (`estoque_minimo`), contendo obrigatoriamente código do item, Certificado de Aprovação (CA), tamanho e sinalização visual de estoque baixo (`BAIXO`/`OK`).
- **Movimentação e Devolução de EPIs**: Mapeamento do fluxo de entrega e devolução parcial ou total de equipamentos aos colaboradores, atualizando o saldo do estoque e registrando datas e status.
- **Inativação Lógica (*Soft Delete*)**: O sistema utiliza o atributo `ativo` (`1` para ativo e `0` para inativo) para desativar/inativar funcionários no banco preservando todo o histórico de retiradas e devoluções.
- **Autenticação Administrativa**: O acesso ao painel de gerenciamento exige autenticação prévia de usuário administrador na tabela `admins`.

---

## 3. Estrutura do Projeto

```text
projeto_dba_cc26/
├── ConsultaFuncionarios/          # Arquivos de Frontend (HTML/CSS/JS)
│   ├── css/                       # Estilos CSS da aplicação
│   ├── imagem/                    # Recursos de imagem e logotipos
│   ├── js/                        # Scripts JavaScript (máscaras, chamadas API)
│   ├── telas/                     # Páginas HTML dos fluxos
│   └── index.html                 # Tela de Login Administrativo
├── backend/                       # Servidor Python e Configurações (MVC)
│   ├── controllers/               # Controladores da API (Lógica de Negócio)
│   │   ├── auth_controller.py
│   │   ├── epi_controller.py
│   │   ├── funcionario_controller.py
│   │   └── movimentacao_controller.py
│   ├── config.py                  # Fábrica de conexões multi-DB (MySQL, SQL Server, SQLite)
│   ├── database.py                # Wrapper para execução de consultas no DB
│   ├── utils.py                   # Funções auxiliares (CPF, MIME types)
│   ├── init_db.sql                # Script DDL e cargas iniciais do banco
│   └── servidor.py                # Ponto de entrada: Servidor HTTP e Roteador de Requests
├── docs/                          # Documentações e Prints de Evidência
│   └── prints/                    # Prints de tela para o README
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

CREATE DATABASE IF NOT EXISTS controle_usuarios
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE controle_usuarios;

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
| `GET` | `/api/profissoes` | Lista as profissões ativas cadastradas | - |
| `GET` | `/api/setores` | Lista os setores ativos cadastrados | - |
| `GET` | `/api/funcionarios` | Lista os funcionários ou filtra por nome/CPF/Matrícula | `?nome=...` |
| `GET` | `/api/funcionarios/buscar-cpf` | Busca dados do funcionário por CPF ou Matrícula | `?cpf=...` |
| `POST` | `/api/funcionarios` | Insere novo funcionário | `{ "matricula": "...", "nome": "...", "cpf": "...", "email": "...", "telefone": "...", "profissao_id": 1, "setor_id": 1 }` |
| `PUT` | `/api/funcionarios` | Atualiza dados do funcionário | `{ "matricula": "...", "nome": "...", "cpf": "...", "email": "...", "telefone": "...", "profissao_id": 1, "setor_id": 1 }` |
| `DELETE` | `/api/funcionarios` | Inativação lógica (*soft delete*) do funcionário | `{ "cpf": "..." }` |
| `GET` | `/api/epis` | Lista equipamentos de proteção cadastrados e em estoque | - |
| `POST` | `/api/retiradas` | Registra movimentação de entrega de EPI vinculada ao funcionário e subtrai do estoque | `{ "cpf": "...", "itens": [{ "epi_id": 1, "quantidade": 1 }] }` |
| `GET` | `/api/retiradas` | Lista os itens pendentes de devolução para um funcionário | `?cpf=...` |
| `POST` | `/api/devolucoes` | Registra a devolução do item e repõe ao estoque | `{ "item_retirada_id": 1, "quantidade": 1 }` |

---

## 6. Guia de Instalação e Execução

### Pré-requisitos
- **Python 3.8+** instalado.
- **Banco de Dados**: MySQL Server, Microsoft SQL Server, ou SQLite (embutido).

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/devmatheuscardoso/projeto_dba_cc26.git
cd projeto_dba_cc26
```

### Passo 2: Instalar Dependências Python
Instale a biblioteca de conexão correspondente ao seu banco de dados escolhido:
```bash
pip install mysql-connector-python  # Para MySQL
pip install pyodbc                  # Para SQL Server
# Não é necessário instalar nada extra para SQLite.
```

### Passo 3: Configuração das Credenciais do Banco de Dados

O sistema oferece **duas formas** para você configurar a conexão com o banco de dados. Escolha a que preferir:

---

#### Método 1: Criando o arquivo `.env` (Recomendado)
Na pasta `backend/`, crie um arquivo chamado `.env` e defina as variáveis de ambiente conforme o banco de dados desejado:

##### Opção A: MySQL (Padrão / Recomendado)
```env
DB_DRIVER=mysql

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=SuaSenhaAqui
MYSQL_DATABASE=controle_funcionarios
```

##### Opção B: SQLite (Zero-Config / Sem necessidade de instalar servidor)
```env
DB_DRIVER=sqlite
SQLITE_FILE=controle_funcionarios.db
```

##### Opção C: Microsoft SQL Server (MSSQL)
```env
DB_DRIVER=mssql

MSSQL_SERVER=localhost
MSSQL_PORT=1433
MSSQL_USER=sa
MSSQL_PASSWORD=SuaSenhaAqui
MSSQL_DATABASE=controle_funcionarios
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
```

---

#### Método 2: Editando diretamente no arquivo `backend/config.py`
Se não quiser criar o arquivo `.env`, você pode alterar os valores padrão diretamente no arquivo `backend/config.py`. Para isso, modifique o texto **depois da vírgula** no segundo parâmetro da função `os.getenv("CHAVE", "valor_padrao")`:

- **Para MySQL (`backend/config.py`):**
  ```python
  host = os.getenv("MYSQL_HOST", "localhost")          # Altere "localhost" se o host for diferente
  port = int(os.getenv("MYSQL_PORT", "3306"))          # Altere "3306" para a porta do seu MySQL
  user = os.getenv("MYSQL_USER", "root")               # Altere "root" para seu usuário do banco
  password = os.getenv("MYSQL_PASSWORD", "SuaSenha")   # <-- Altere "" para sua senha entre aspas
  database = os.getenv("MYSQL_DATABASE", "controle_funcionarios") # Nome do banco de dados
  ```

- **Para outros bancos em `backend/config.py`:**
  - **SQL Server (MSSQL):** Altere os valores após a vírgula em `MSSQL_SERVER`, `MSSQL_USER`, `MSSQL_PASSWORD`, etc.
  - **SQLite:** Caso queira mudar o caminho do arquivo `.db`, altere o segundo argumento em `os.getenv("SQLITE_FILE", "caminho_do_banco.db")`.

---

### Passo 4: Como Executar o Script de Inicialização (`init_db.sql`)

Antes de iniciar a aplicação, é necessário criar o banco de dados e as tabelas com a carga inicial de dados executando o arquivo `backend/init_db.sql`. Escolha a forma de execução adequada ao seu ambiente:

#### Opção 1: Via Linha de Comando / Terminal (MySQL CLI)
Abra o terminal ou prompt de comando na raiz do projeto e execute:

- **Linux / macOS / Git Bash:**
  ```bash
  mysql -u root -p < backend/init_db.sql
  ```
- **Windows (PowerShell):**
  ```powershell
  Get-Content backend\init_db.sql | mysql -u root -p
  ```
- **Windows (CMD):**
  ```cmd
  mysql -u root -p < backend\init_db.sql
  ```
*(O sistema solicitará a sua senha do MySQL e criará automaticamente a base de dados `controle_funcionarios` com todas as tabelas e dados pré-cadastrados).*

#### Opção 2: Via MySQL Workbench / DBeaver / phpMyAdmin
1. Abra o **MySQL Workbench** (ou **DBeaver** / **phpMyAdmin**).
2. Conecte-se ao seu servidor MySQL local ou remoto.
3. No menu superior, vá em **File -> Open SQL Script...** (ou pressione `Ctrl + O`) e selecione o arquivo `backend/init_db.sql`.
4. Clique no ícone de **raio** (Execute SQL script / `Ctrl + Shift + Enter`) para rodar todas as instruções.
5. Verifique no painel lateral de Schemas se o banco `controle_funcionarios` foi criado com sucesso.

#### Opção 3: Se estiver utilizando SQLite
Se optou por utilizar SQLite (`DB_DRIVER=sqlite`), você pode criar a estrutura no arquivo executando no terminal:
```bash
sqlite3 backend/controle_funcionarios.db < backend/init_db.sql
```
*(Ou utilize uma ferramenta gráfica como **DB Browser for SQLite** para importar o arquivo `init_db.sql`).*

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
  
## 7. Evidências Visuais (Interface Redesenhada)
As telas abaixo demonstram o sistema final com a interface moderna (HTML5 + CSS3 puro com animações, fonte Inter e layout em cards).

#### 1. Tela de Login
![Login](docs/screenshot_01_login.png)
*Formulário de autenticação com animação de entrada suave (slide-up fade) e botão com pulso brilhante.*

#### 2. Painel de Controle (Dashboard)
![Painel de Controle](docs/screenshot_02_dashboard.png)
*Menu principal organizado em grid com ações coloridas por gradiente, cada uma com efeito hover e busca rápida.*

#### 3. Cadastro de Funcionário
![Cadastro de Funcionário](docs/screenshot_03_cadastro.png)
*Formulário de adição de colaboradores com campo livre para profissão, seleção de setor e validação visual.*

#### 4. Atualização e Reativação de Cadastro
![Atualização de Funcionário](docs/screenshot_07_atualizar.png)
*Busca por CPF/Matrícula para alteração de dados do colaborador ou reativação de registros inativos.*

#### 5. Estoque de EPIs
![Estoque](docs/screenshot_04_estoque.png)
*Tabela de inventário em tempo real exibindo quantidade, estoque mínimo e status de cada EPI.*

#### 6. Retirada de EPI
![Retirada de EPI](docs/screenshot_05_retirada.png)
*Registro de entrega de EPIs por CPF, com seleção dinâmica dos itens disponíveis em estoque.*

#### 7. Devolução de EPI
![Devolução de EPI](docs/screenshot_06_devolucao.png)
*Histórico de retiradas pendentes buscado pelo CPF, com controle de status (RETIRADO → DEVOLVIDO).*

---

### 7.2 Evidências de Consultas no Banco de Dados (DBA - SQL)

Abaixo estão os comprovantes de execução das consultas SQL no Banco de Dados MySQL para verificação da integridade das tabelas e relacionamentos:

#### 1. Consulta à Tabela de Funcionários (`SELECT * FROM funcionarios`)
![Select Funcionários](docs/prints/01_select_funcionarios.png)
*Execução de consulta relacional trazendo a listagem de colaboradores cadastrados.*

#### 2. Consulta à Tabela de EPIs (`SELECT * FROM epis`)
![Select EPIs](docs/prints/02_select_epis.png)
*Consulta ao inventário e controle de estoque de Equipamentos de Proteção Individual.*

#### 3. Registros de Retiradas (`SELECT * FROM retiradas`)
![Select Retiradas](docs/prints/03_select_retiradas.png)
*Listagem de movimentações de entrega de EPIs vinculadas aos colaboradores.*

#### 4. Controle e Atualização de Devoluções de EPIs
![Select Devoluções](docs/prints/03b_select_devolucao.png)
*Verificação dos itens com controle de status de devolução e reposição ao estoque.*
