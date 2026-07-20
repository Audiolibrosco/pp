-- 🔥 Calcifer Core — Database Schema v1.1.0
-- Incluye: module_executions, credit_transactions, core_config, module_status

-- Tabla de ejecuciones de módulos (Audit Manager)
CREATE TABLE IF NOT EXISTS module_executions (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    telegram_id     BIGINT       NOT NULL,
    username        VARCHAR(100),
    command         VARCHAR(50)  NOT NULL,
    framework       VARCHAR(50),
    module          VARCHAR(100),
    status          VARCHAR(30)  NOT NULL,
    execution_time  INT          DEFAULT 0,
    credits_before  INT          DEFAULT 0,
    credits_after   INT          DEFAULT 0,
    response        VARCHAR(500),
    error_code      VARCHAR(20),
    extra           JSON,
    created_at      DATETIME     DEFAULT NOW(),
    INDEX idx_telegram (telegram_id),
    INDEX idx_status   (status),
    INDEX idx_created  (created_at)
);

-- Tabla de historial de créditos (Credits Manager)
CREATE TABLE IF NOT EXISTS credit_transactions (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    telegram_id     BIGINT       NOT NULL,
    operation       VARCHAR(20)  NOT NULL,  -- DEDUCT | ADD | REVERT | SET_UNLIMITED
    amount          INT          NOT NULL,
    credits_before  INT          NOT NULL,
    credits_after   INT          NOT NULL,
    created_at      DATETIME     DEFAULT NOW(),
    INDEX idx_telegram (telegram_id),
    INDEX idx_created  (created_at)
);

-- Tabla de configuración dinámica del Core
CREATE TABLE IF NOT EXISTS core_config (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    config_key  VARCHAR(200) UNIQUE NOT NULL,
    config_val  TEXT,
    updated_at  DATETIME DEFAULT NOW() ON UPDATE NOW()
);

-- Tabla de estado de módulos (persistencia entre reinicios)
CREATE TABLE IF NOT EXISTS module_status_log (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,
    old_status  VARCHAR(30),
    new_status  VARCHAR(30),
    changed_by  VARCHAR(100),
    created_at  DATETIME DEFAULT NOW()
);
