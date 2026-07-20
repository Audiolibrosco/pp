"""
Calcifer — Conexión MySQL (Hostinger)
"""
import os
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host     = os.environ.get("DB_HOST"),
            database = os.environ.get("DB_NAME"),
            user     = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASS"),
            port     = int(os.environ.get("DB_PORT", 3306)),
            charset  = "utf8mb4",
        )
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None


def get_usuario(telegram_id: str) -> dict:
    conn = get_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE telegram_id = %s", (str(telegram_id),))
        return cursor.fetchone() or {}
    except Error as e:
        print(f"[DB ERROR get_usuario] {e}")
        return {}
    finally:
        conn.close()


def get_usuario_by_username(username: str) -> dict:
    conn = get_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        return cursor.fetchone() or {}
    except Error as e:
        print(f"[DB ERROR get_usuario_by_username] {e}")
        return {}
    finally:
        conn.close()


def registrar_usuario(telegram_id: str, username: str, nombre: str) -> bool:
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios
            (telegram_id, username, nombre, membresia, creditos, fecha_activacion, fecha_vencimiento)
            VALUES (%s, %s, %s, 'Free', 0, CURDATE(), '9999-12-31')
            ON DUPLICATE KEY UPDATE username=VALUES(username), nombre=VALUES(nombre)
        """
        cursor.execute(sql, (str(telegram_id), username, nombre))
        conn.commit()
        return True
    except Error as e:
        print(f"[DB ERROR registrar_usuario] {e}")
        return False
    finally:
        conn.close()


def asignar_membresia(username: str, membresia: str, dias: int) -> bool:
    """Asigna membresía a un usuario por su username."""
    conn = get_connection()
    if not conn:
        return False
    try:
        # Calcular créditos según membresía y días
        creditos = 0
        if membresia == "Premium":
            creditos = 250 if dias == 15 else 500

        fecha_vencimiento = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")

        cursor = conn.cursor()
        sql = """
            UPDATE usuarios
            SET membresia=%s, creditos=%s, fecha_activacion=CURDATE(),
                fecha_vencimiento=%s, activo=TRUE
            WHERE username=%s
        """
        cursor.execute(sql, (membresia, creditos, fecha_vencimiento, username))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"[DB ERROR asignar_membresia] {e}")
        return False
    finally:
        conn.close()


def guardar_transaccion(data: dict) -> bool:
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO transacciones
            (reference, pasarela, estado, response_code, monto,
             moneda, mensaje, telegram_user, transaction_id, auth_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            estado=VALUES(estado), response_code=VALUES(response_code),
            mensaje=VALUES(mensaje), updated_at=NOW()
        """
        cursor.execute(sql, (
            data.get("reference"), data.get("pasarela"), data.get("estado"),
            data.get("response_code"), data.get("monto", 0), data.get("moneda", "USD"),
            data.get("mensaje"), data.get("telegram_user"),
            data.get("transaction_id"), data.get("auth_code"),
        ))
        conn.commit()
        return True
    except Error as e:
        print(f"[DB ERROR guardar_transaccion] {e}")
        return False
    finally:
        conn.close()


def obtener_transaccion(reference: str) -> dict:
    conn = get_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transacciones WHERE reference = %s", (reference,))
        return cursor.fetchone() or {}
    except Error as e:
        print(f"[DB ERROR obtener_transaccion] {e}")
        return {}
    finally:
        conn.close()


def historial_transacciones(limite: int = 10) -> list:
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM transacciones ORDER BY created_at DESC LIMIT %s", (limite,)
        )
        return cursor.fetchall()
    except Error as e:
        print(f"[DB ERROR historial] {e}")
        return []
    finally:
        conn.close()


def guardar_webhook(pasarela: str, payload: dict) -> bool:
    import json
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO webhooks (pasarela, payload) VALUES (%s, %s)",
            (pasarela, json.dumps(payload))
        )
        conn.commit()
        return True
    except Error as e:
        print(f"[DB ERROR guardar_webhook] {e}")
        return False
    finally:
        conn.close()


def bloquear_usuario(identificador: str) -> bool:
    """Bloquea un usuario por username o telegram_id."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        if identificador.isdigit():
            cursor.execute("UPDATE usuarios SET activo=FALSE WHERE telegram_id = %s", (identificador,))
        else:
            cursor.execute("UPDATE usuarios SET activo=FALSE WHERE username = %s", (identificador,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"[DB ERROR bloquear_usuario] {e}")
        return False
    finally:
        conn.close()


def desbloquear_usuario(identificador: str) -> bool:
    """Desbloquea un usuario y resetea su membresía a Free."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        if identificador.isdigit():
            cursor.execute(
                "UPDATE usuarios SET activo=TRUE, membresia='Free', creditos=0 WHERE telegram_id = %s",
                (identificador,)
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET activo=TRUE, membresia='Free', creditos=0 WHERE username = %s",
                (identificador,)
            )
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"[DB ERROR desbloquear_usuario] {e}")
        return False
    finally:
        conn.close()


def eliminar_usuario(identificador: str) -> bool:
    """Elimina un usuario por username o telegram_id."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        if identificador.isdigit():
            cursor.execute("DELETE FROM usuarios WHERE telegram_id = %s", (identificador,))
        else:
            cursor.execute("DELETE FROM usuarios WHERE username = %s", (identificador,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"[DB ERROR eliminar_usuario] {e}")
        return False
    finally:
        conn.close()


def poner_mantenimiento(pasarela: str) -> bool:
    """Pone una pasarela en mantenimiento."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mantenimiento (pasarela, activo, created_at)
            VALUES (%s, TRUE, NOW())
            ON DUPLICATE KEY UPDATE activo=TRUE, created_at=NOW()
        """, (pasarela,))
        conn.commit()
        return True
    except Error as e:
        print(f"[DB ERROR poner_mantenimiento] {e}")
        return False
    finally:
        conn.close()


def quitar_mantenimiento(pasarela: str) -> bool:
    """Reactiva una pasarela del mantenimiento."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE mantenimiento SET activo=FALSE WHERE pasarela = %s", (pasarela,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"[DB ERROR quitar_mantenimiento] {e}")
        return False
    finally:
        conn.close()


def get_mantenimiento() -> list:
    """Obtiene todas las pasarelas en mantenimiento."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mantenimiento WHERE activo=TRUE ORDER BY created_at DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"[DB ERROR get_mantenimiento] {e}")
        return []
    finally:
        conn.close()


def get_bin_cache(bin_number: str) -> dict:
    """Obtiene BIN del caché local."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bin_cache WHERE bin_number = %s", (bin_number[:6],))
        row = cursor.fetchone()
        conn.close()
        if row:
            alpha2 = row.get("country_code") or ""
            flag = "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in alpha2.upper()) if alpha2 else None
            return {
                "brand"       : row.get("brand"),
                "type"        : row.get("type"),
                "level"       : row.get("level"),
                "bank"        : row.get("bank"),
                "country"     : row.get("country"),
                "country_flag": flag,
            }
        return {}
    except Exception:
        return {}

def set_bin_cache(bin_number: str, data: dict):
    """Guarda BIN en el caché local."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bin_cache (bin_number, brand, type, level, bank, country, country_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                brand=VALUES(brand), type=VALUES(type), level=VALUES(level),
                bank=VALUES(bank), country=VALUES(country), country_code=VALUES(country_code)
        """, (
            bin_number[:6],
            data.get("brand"),
            data.get("type"),
            data.get("level"),
            data.get("bank"),
            data.get("country"),
            data.get("country_code"),
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass

def asignar_membresia_por_id(telegram_id: str, membresia: str, dias: int) -> bool:
    """Asigna membresía a un usuario por telegram_id."""
    try:
        from datetime import datetime, timedelta
        conn = get_connection()
        cursor = conn.cursor()
        fecha_vencimiento = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
        creditos = 250 if (membresia == "Premium" and dias == 15) else 500 if membresia == "Premium" else -1 if membresia in ("Owner","Seller") else 0
        cursor.execute("""
            UPDATE usuarios SET membresia=%s, fecha_vencimiento=%s, creditos=%s
            WHERE telegram_id=%s
        """, (membresia, fecha_vencimiento, creditos, telegram_id))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception:
        return False
