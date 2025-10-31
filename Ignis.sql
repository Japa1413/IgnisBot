-- 1) Banco do Ignis
CREATE DATABASE IF NOT EXISTS ignis
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2) Usuário de app (ajuste a senha)
CREATE USER IF NOT EXISTS 'ignis_user'@'localhost' IDENTIFIED BY 'SENHA_FORTE_AQUI';

-- 3) Permissões no banco ignis
GRANT ALL PRIVILEGES ON ignis.* TO 'ignis_user'@'localhost';

FLUSH PRIVILEGES;

-- 4) (Opcional) Tabela base do sistema de pontos (se ainda não existir)
USE ignis;
CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT PRIMARY KEY,
  points INT DEFAULT 0,
  `rank` VARCHAR(50) DEFAULT 'Civitas aspirant',
  progress INT DEFAULT 0
);

-- 5) (Opcional) Tabela do rank->companhia usada em cogs/rank.py
CREATE TABLE IF NOT EXISTS role_company_map (
  role_name VARCHAR(100) PRIMARY KEY,
  company INT NOT NULL
);

-- 6) Tabela de consentimento LGPD (conformidade legal)
CREATE TABLE IF NOT EXISTS user_consent (
  user_id BIGINT PRIMARY KEY,
  consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  consent_version VARCHAR(20) DEFAULT '1.0',
  base_legal VARCHAR(50) DEFAULT 'consentimento',
  consent_given BOOLEAN DEFAULT FALSE,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7) Tabela de auditoria de dados pessoais (LGPD Art. 10)
CREATE TABLE IF NOT EXISTS data_audit_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  action_type VARCHAR(50) NOT NULL,
  data_type VARCHAR(100) NOT NULL,
  performed_by BIGINT,
  purpose TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  details JSON,
  INDEX idx_user_id (user_id),
  INDEX idx_timestamp (timestamp),
  INDEX idx_action_type (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;