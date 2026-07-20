"""
🔥 Calcifer Core — Audit Manager
Autor: Calcifer Team | Versión: 1.0.0
Registra cada operación del sistema con todos sus detalles.
"""
import json
from datetime import datetime
from typing import Optional
import mysql.connector
from core.config_manager import config
from core.logger import logger


class AuditManager:
    """
    Registra cada ejecución de módulo en la base de datos.
    Campos: usuario, telegram_id, comando, framework, módulo,
            inicio, fin, tiempo, créditos, resultado, error.
    """

    def _conn(self):
        try:
            return mysql.connector.connect(**config.get_db_config())
        except mysql.connector.Error as e:
            logger.error(f"Audit DB error: {e}", "AUDIT")
            return None

    def log(
        self,
        telegram_id   : int,
        username      : str,
        command       : str,
        framework     : str,
        module        : str,
        status        : str,
        execution_time: int,
        credits_before: int,
        credits_after : int,
        response      : str  = "",
        error_code    : Optional[str] = None,
        extra         : Optional[dict] = None,
    ) -> bool:
        """Registra una ejecución completa en module_executions."""
        conn = self._conn()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO module_executions
                (telegram_id, username, command, framework, module,
                 status, execution_time, credits_before, credits_after,
                 response, error_code, extra, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                telegram_id, username, command, framework, module,
                status, execution_time, credits_before, credits_after,
                response[:500] if response else "",
                error_code,
                json.dumps(extra or {}, ensure_ascii=False),
                datetime.utcnow(),
            ))
            conn.commit()
            logger.info(
                f"Audit: @{username} | {command} | {module} | {status} | {execution_time}s",
                "AUDIT"
            )
            return True
        except mysql.connector.Error as e:
            logger.error(f"Error guardando audit: {e}", "AUDIT")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_history(self, telegram_id: int, limit: int = 10) -> list:
        """Retorna el historial de ejecuciones de un usuario."""
        conn = self._conn()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT command, framework, module, status,
                       execution_time, credits_before, credits_after,
                       response, error_code, created_at
                FROM module_executions
                WHERE telegram_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (telegram_id, limit))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error(f"Error leyendo historial: {e}", "AUDIT")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_stats(self, telegram_id: int) -> dict:
        """Retorna estadísticas del usuario."""
        conn = self._conn()
        if not conn:
            return {}
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'CHARGED'     THEN 1 ELSE 0 END) as charged,
                    SUM(CASE WHEN status = 'DECLINED'    THEN 1 ELSE 0 END) as declined,
                    SUM(CASE WHEN status = 'PENDING_3DS' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status LIKE 'ERR%'     THEN 1 ELSE 0 END) as errors,
                    AVG(execution_time) as avg_time
                FROM module_executions
                WHERE telegram_id = %s
            """, (telegram_id,))
            return cursor.fetchone() or {}
        except mysql.connector.Error as e:
            logger.error(f"Error leyendo stats: {e}", "AUDIT")
            return {}
        finally:
            cursor.close()
            conn.close()


audit_manager = AuditManager()
