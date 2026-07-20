"""
🔥 Calcifer Core — Logger
Autor: Calcifer Team | Versión: 1.1.0
Logger unificado con soporte por módulo, framework, rotación,
logs estructurados JSON y limpieza automática.
"""
import os
import json
import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import Optional


LOG_DIR      = "/root/calcifer/logs"
MAX_BYTES    = 10 * 1024 * 1024   # 10 MB por archivo
BACKUP_COUNT = 5                   # máximo 5 archivos históricos
LOG_LEVEL    = logging.INFO
MAX_AGE_DAYS = 30                  # eliminar logs con más de 30 días


class CalciferLogger:
    """Logger centralizado con rotación, JSON y soporte por módulo/framework."""

    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        self._loggers = {}
        self._setup_root()

    def _setup_root(self):
        logging.basicConfig(
            format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
            level=LOG_LEVEL,
        )
        self._root = logging.getLogger("Calcifer")

    def _get_file_logger(self, filename: str) -> logging.Logger:
        """Obtiene o crea un logger con rotación para un archivo."""
        if filename in self._loggers:
            return self._loggers[filename]
        path    = os.path.join(LOG_DIR, filename)
        handler = logging.handlers.RotatingFileHandler(
            path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        lg = logging.getLogger(f"calcifer.file.{filename}")
        lg.addHandler(handler)
        lg.setLevel(LOG_LEVEL)
        lg.propagate = False
        self._loggers[filename] = lg
        return lg

    def _ts(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _write(self, filename: str, level: str, module: str, message: str, extra: dict = None):
        """Escribe línea plana y JSON estructurado."""
        ts      = self._ts()
        plain   = f"[{ts}] {level} | {module} | {message}"
        lg      = self._get_file_logger(filename)
        lg.info(plain)
        # JSON estructurado en archivo aparte
        record = {"ts": ts, "level": level, "module": module, "message": message}
        if extra:
            record.update(extra)
        json_lg = self._get_file_logger(filename.replace(".log", ".json.log"))
        json_lg.info(json.dumps(record, ensure_ascii=False))

    # ── Métodos principales ───────────────────────────────────────────────────

    def info(self, message: str, module: str = "CORE"):
        self._root.info(f"[{module}] {message}")
        self._write("bot.log", "INFO", module, message)

    def warning(self, message: str, module: str = "CORE"):
        self._root.warning(f"[{module}] {message}")
        self._write("bot.log", "WARNING", module, message)

    def error(self, message: str, module: str = "CORE"):
        self._root.error(f"[{module}] {message}")
        self._write("errores.log", "ERROR", module, message)

    def debug(self, message: str, module: str = "CORE"):
        if self._root.isEnabledFor(logging.DEBUG):
            self._root.debug(f"[{module}] {message}")

    # ── Métodos especializados ────────────────────────────────────────────────

    def command(self, user_id: str, username: str, command: str, result: str = "SUCCESS"):
        msg = f"USER:{user_id} (@{username}) | CMD:{command} | RESULT:{result}"
        self._root.info(msg)
        self._write("comandos.log", "INFO", "CMD", msg,
                    {"user_id": user_id, "username": username, "command": command, "result": result})

    def access(self, user_id: str, username: str, action: str):
        msg = f"USER:{user_id} (@{username}) | ACTION:{action}"
        self._write("accesos.log", "INFO", "ACCESS", msg,
                    {"user_id": user_id, "username": username, "action": action})

    def audit(self, admin_id: str, admin_username: str, action: str, target: str):
        msg = f"ADMIN:{admin_id} (@{admin_username}) | ACTION:{action} | TARGET:{target}"
        self._root.info(f"[AUDIT] {msg}")
        self._write("auditoria.log", "AUDIT", "AUDIT", msg,
                    {"admin_id": admin_id, "admin": admin_username, "action": action, "target": target})

    def module(self, module_name: str, framework: str, event: str, detail: str = ""):
        """Log específico por módulo y framework."""
        filename = f"module_{framework}_{module_name}.log"
        msg = f"EVENT:{event} | {detail}"
        self._write(filename, "INFO", f"{framework}.{module_name}", msg,
                    {"framework": framework, "module": module_name, "event": event, "detail": detail})

    def framework(self, framework_name: str, event: str, detail: str = ""):
        """Log específico por framework."""
        filename = f"framework_{framework_name}.log"
        self._write(filename, "INFO", f"FRAMEWORK.{framework_name}", event,
                    {"framework": framework_name, "event": event, "detail": detail})

    def critical(self, message: str, module: str = "CORE"):
        """Log de nivel CRITICAL — errores que detienen el sistema."""
        self._root.critical(f"[{module}] {message}")
        self._write("errores.log", "CRITICAL", module, message)
        self._write("critical.log", "CRITICAL", module, message)

    def set_level(self, level: str):
        """Cambia el nivel de log en caliente."""
        levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO,
                  "WARNING": logging.WARNING, "ERROR": logging.ERROR}
        self._root.setLevel(levels.get(level.upper(), logging.INFO))
        self.info(f"Nivel de log cambiado a: {level}", "LOGGER")

    def cleanup_old_logs(self, max_age_days: int = MAX_AGE_DAYS):
        """Elimina logs con más de max_age_days días."""
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        removed = 0
        for fname in os.listdir(LOG_DIR):
            fpath = os.path.join(LOG_DIR, fname)
            if os.path.isfile(fpath):
                mtime = datetime.utcfromtimestamp(os.path.getmtime(fpath))
                if mtime < cutoff:
                    os.remove(fpath)
                    removed += 1
        self.info(f"Limpieza de logs: {removed} archivos eliminados", "LOGGER")
        return removed


logger = CalciferLogger()
