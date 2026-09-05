/* =====================================================
   SCRIPT DE INICIALIZAÇÃO DO BANCO DE DADOS
   
   Execute este script no MySQL para criar o banco,
   as tabelas e os dados iniciais.
===================================================== */


CREATE DATABASE IF NOT EXISTS controle_usuarios
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE controle_usuarios;


/* =====================================================
   TABELA DE USUÁRIOS
===================================================== */

CREATE TABLE IF NOT EXISTS usuarios (

    cpf         VARCHAR(20)  NOT NULL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    profissao   VARCHAR(100) NOT NULL,
    ativo       TINYINT(1)   NOT NULL DEFAULT 1

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/* =====================================================
   TABELA DE ADMINISTRADORES (LOGIN)
===================================================== */

CREATE TABLE IF NOT EXISTS admins (

    id       INT          AUTO_INCREMENT PRIMARY KEY,
    usuario  VARCHAR(50)  NOT NULL UNIQUE,
    senha    VARCHAR(255) NOT NULL,
    ativo    TINYINT(1)   NOT NULL DEFAULT 1

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/* =====================================================
   DADOS INICIAIS — USUÁRIOS
===================================================== */

INSERT IGNORE INTO usuarios (cpf, nome, profissao, ativo) VALUES
    ('123.456.789-01', 'João da Silva',           'Analista de Sistemas', 1),
    ('234.567.890-12', 'João Pedro Santos',        'Desenvolvedor', 1),
    ('345.678.901-23', 'João Carlos Oliveira',     'Suporte Técnico', 1),
    ('456.789.012-34', 'João Vitor Almeida',       'Designer Gráfico', 1),
    ('567.890.123-45', 'João Marcelo Souza',       'Assistente Administrativo', 1);


/* =====================================================
   DADOS INICIAIS — ADMIN
===================================================== */

INSERT IGNORE INTO admins (usuario, senha, ativo) VALUES
    ('admin', '1234', 1);

