-- ================================================
-- CALCIFER BOT — Schema MySQL
-- Ejecutar en phpMyAdmin de Hostinger
-- ================================================

CREATE DATABASE IF NOT EXISTS calcifer_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE calcifer_db;

-- ── USUARIOS TELEGRAM ────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  telegram_id       VARCHAR(50) NOT NULL UNIQUE,
  username          VARCHAR(100),
  nombre            VARCHAR(200),
  membresia         ENUM('Owner','Admin','Premium','Basic','Trial') DEFAULT 'Trial',
  activo            BOOLEAN DEFAULT TRUE,
  fecha_activacion  DATE,
  fecha_vencimiento DATE,
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insertar Owner por defecto
INSERT INTO usuarios (telegram_id, username, nombre, membresia, activo, fecha_activacion)
VALUES ('7469285894', 'MacClaren13', 'Mac', 'Owner', TRUE, '2026-06-25')
ON DUPLICATE KEY UPDATE membresia='Owner';

-- ── TRANSACCIONES ────────────────────────────────
CREATE TABLE IF NOT EXISTS transacciones (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  reference       VARCHAR(100) NOT NULL UNIQUE,
  pasarela        ENUM('stripe','paypal','shopify','square','amazon','adyen','moneris','payflow','zuora') NOT NULL,
  estado          ENUM('AUTH','CHARGED','DECLINED','PENDING','CANCELLED','EXPIRED') NOT NULL,
  response_code   VARCHAR(100),
  monto           DECIMAL(10,2) NOT NULL,
  moneda          VARCHAR(10) DEFAULT 'USD',
  mensaje         TEXT,
  telegram_user   VARCHAR(100),
  transaction_id  VARCHAR(200),
  auth_code       VARCHAR(100),
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── VALIDACIONES ─────────────────────────────────
CREATE TABLE IF NOT EXISTS validaciones (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  transaccion_id  INT,
  cvv_status      ENUM('MATCH','NO_MATCH','NOT_PROVIDED','UNKNOWN') DEFAULT 'UNKNOWN',
  avs_status      ENUM('MATCH','NO_MATCH','PARTIAL','NOT_PROVIDED','UNKNOWN') DEFAULT 'UNKNOWN',
  secure_3d       ENUM('SUCCESS','FAILED','PENDING','NOT_REQUIRED','UNKNOWN') DEFAULT 'UNKNOWN',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (transaccion_id) REFERENCES transacciones(id)
);

-- ── WEBHOOKS RECIBIDOS ───────────────────────────
CREATE TABLE IF NOT EXISTS webhooks (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  pasarela        VARCHAR(50) NOT NULL,
  payload         JSON,
  procesado       BOOLEAN DEFAULT FALSE,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── PRUEBAS SELENIUM ─────────────────────────────
CREATE TABLE IF NOT EXISTS pruebas_selenium (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  pasarela        VARCHAR(50) NOT NULL,
  resultado       ENUM('EXITOSO','FALLIDO','ERROR') NOT NULL,
  screenshot      TEXT,
  detalle         TEXT,
  proxy_usado     VARCHAR(200),
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices
-- ── MANTENIMIENTO DE PASARELAS ──────────────────────────────
CREATE TABLE IF NOT EXISTS mantenimiento (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  pasarela    VARCHAR(100) NOT NULL UNIQUE,
  activo      BOOLEAN DEFAULT TRUE,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transacciones_estado    ON transacciones(estado);
CREATE INDEX idx_transacciones_pasarela  ON transacciones(pasarela);
CREATE INDEX idx_transacciones_reference ON transacciones(reference);
CREATE INDEX idx_webhooks_pasarela       ON webhooks(pasarela);
CREATE INDEX idx_usuarios_telegram_id    ON usuarios(telegram_id);
