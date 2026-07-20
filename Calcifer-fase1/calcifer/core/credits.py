"""
🔥 Calcifer Core — Credits Manager
Autor: Calcifer Team | Versión: 1.1.0
Gestión completa de créditos: consulta, validación, descuento,
recarga individual (250 o 500), reversión e historial.
"""
import mysql.connector
from datetime import datetime
from typing import Optional
from core.config_manager import config
from core.logger import logger
from core.exceptions import InsufficientCreditsError, DatabaseError, UserNotFoundError, InvalidParameterError


UNLIMITED       = -1
DEFAULT_COST    = 1
VALID_AMOUNTS   = {250, 500}   # Montos permitidos para recarga individual
BILLABLE        = {"CHARGED", "DECLINED", "PENDING_3DS"}


class CreditsManager:

    def _conn(self):
        try:
            return mysql.connector.connect(**config.get_db_config())
        except mysql.connector.Error as e:
            logger.error(f"Credits DB error: {e}", "CREDITS")
            raise DatabaseError(str(e))

    # ── CONSULTA ──────────────────────────────────────────────────────────────

    def get(self, telegram_id: int) -> int:
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT credits FROM users WHERE telegram_id = %s", (telegram_id,))
            row = cursor.fetchone()
            if not row:
                raise UserNotFoundError(f"Usuario {telegram_id} no encontrado")
            return row[0]
        except UserNotFoundError:
            raise
        except mysql.connector.Error as e:
            raise DatabaseError(str(e))
        finally:
            cursor.close(); conn.close()

    # ── VALIDACIÓN ────────────────────────────────────────────────────────────

    def validate(self, telegram_id: int, cost: int = DEFAULT_COST) -> bool:
        credits = self.get(telegram_id)
        if credits == UNLIMITED:
            return True
        if credits < cost:
            raise InsufficientCreditsError(
                f"Créditos insuficientes. Tienes {credits}, necesitas {cost}."
            )
        return True

    def has_credits(self, telegram_id: int, cost: int = DEFAULT_COST) -> bool:
        try:
            self.validate(telegram_id, cost)
            return True
        except (InsufficientCreditsError, UserNotFoundError):
            return False

    # ── DESCUENTO ─────────────────────────────────────────────────────────────

    def deduct(self, telegram_id: int, cost: int = DEFAULT_COST) -> int:
        credits = self.get(telegram_id)
        if credits == UNLIMITED:
            return UNLIMITED
        conn = self._conn()
        try:
            cursor = conn.cursor()
            new = max(0, credits - cost)
            cursor.execute("UPDATE users SET credits=%s WHERE telegram_id=%s", (new, telegram_id))
            conn.commit()
            self._log_transaction(telegram_id, "DEDUCT", cost, credits, new)
            logger.info(f"Descuento: id={telegram_id} {credits}→{new}", "CREDITS")
            return new
        except mysql.connector.Error as e:
            conn.rollback(); raise DatabaseError(str(e))
        finally:
            cursor.close(); conn.close()

    def deduct_if_billable(self, telegram_id: int, status: str, cost: int = DEFAULT_COST) -> Optional[int]:
        if status not in BILLABLE:
            return None
        return self.deduct(telegram_id, cost)

    # ── REVERTIR CRÉDITOS ─────────────────────────────────────────────────────

    def revert(self, telegram_id: int, amount: int = DEFAULT_COST) -> int:
        """Devuelve créditos al usuario (ej. tras error del sistema)."""
        credits = self.get(telegram_id)
        if credits == UNLIMITED:
            return UNLIMITED
        conn = self._conn()
        try:
            cursor = conn.cursor()
            new = credits + amount
            cursor.execute("UPDATE users SET credits=%s WHERE telegram_id=%s", (new, telegram_id))
            conn.commit()
            self._log_transaction(telegram_id, "REVERT", amount, credits, new)
            logger.info(f"Reversión: id={telegram_id} {credits}→{new}", "CREDITS")
            return new
        except mysql.connector.Error as e:
            conn.rollback(); raise DatabaseError(str(e))
        finally:
            cursor.close(); conn.close()

    # ── RECARGA INDIVIDUAL ────────────────────────────────────────────────────

    def add(self, telegram_id: int, amount: int) -> int:
        """
        Agrega créditos individualmente (por fuera de membresía).
        Solo permite montos de 250 o 500.
        """
        if amount not in VALID_AMOUNTS:
            raise InvalidParameterError(
                f"Monto inválido: {amount}. Solo se permiten: 250 o 500."
            )
        credits = self.get(telegram_id)
        if credits == UNLIMITED:
            return UNLIMITED
        conn = self._conn()
        try:
            cursor = conn.cursor()
            new = credits + amount
            cursor.execute("UPDATE users SET credits=%s WHERE telegram_id=%s", (new, telegram_id))
            conn.commit()
            self._log_transaction(telegram_id, "ADD", amount, credits, new)
            logger.info(f"Recarga: id={telegram_id} +{amount} → {new}", "CREDITS")
            return new
        except mysql.connector.Error as e:
            conn.rollback(); raise DatabaseError(str(e))
        finally:
            cursor.close(); conn.close()

    def set_unlimited(self, telegram_id: int) -> bool:
        conn = self._conn()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET credits=%s WHERE telegram_id=%s", (UNLIMITED, telegram_id))
            conn.commit()
            logger.info(f"Créditos ilimitados: id={telegram_id}", "CREDITS")
            return True
        except mysql.connector.Error as e:
            conn.rollback(); raise DatabaseError(str(e))
        finally:
            cursor.close(); conn.close()

    def is_unlimited(self, telegram_id: int) -> bool:
        return self.get(telegram_id) == UNLIMITED

    # ── HISTORIAL ─────────────────────────────────────────────────────────────

    def _log_transaction(self, telegram_id: int, operation: str,
                         amount: int, before: int, after: int):
        """Guarda cada movimiento de créditos en credit_transactions."""
        try:
            conn = self._conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO credit_transactions
                (telegram_id, operation, amount, credits_before, credits_after, created_at)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (telegram_id, operation, amount, before, after, datetime.utcnow()))
            conn.commit()
        except Exception as e:
            logger.warning(f"No se pudo guardar transacción de créditos: {e}", "CREDITS")
        finally:
            try: cursor.close(); conn.close()
            except: pass

    def get_history(self, telegram_id: int, limit: int = 10) -> list:
        """Retorna historial de movimientos de créditos."""
        try:
            conn = self._conn()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT operation, amount, credits_before, credits_after, created_at
                FROM credit_transactions
                WHERE telegram_id=%s
                ORDER BY created_at DESC LIMIT %s
            """, (telegram_id, limit))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error leyendo historial créditos: {e}", "CREDITS")
            return []
        finally:
            try: cursor.close(); conn.close()
            except: pass

    def validate_transaction(self, telegram_id: int, operation: str,
                              amount: int, expected_before: int) -> bool:
        """Valida que una transacción sea consistente."""
        actual = self.get(telegram_id)
        if actual != expected_before and actual != UNLIMITED:
            logger.warning(
                f"Inconsistencia: id={telegram_id} esperado={expected_before} actual={actual}",
                "CREDITS"
            )
            return False
        return True


credits_manager = CreditsManager()
