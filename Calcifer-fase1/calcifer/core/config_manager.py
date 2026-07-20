"""
🔥 Calcifer Core — Config Manager
Autor: Calcifer Team | Versión: 1.1.0
Configuración global, por framework y por módulo.
Soporta recarga dinámica sin reinicio.
"""
import os
import json
from dotenv import load_dotenv
from typing import Any, Optional

load_dotenv()


class ConfigManager:
    """Configuración centralizada con soporte por framework y módulo."""

    # ── Telegram ──────────────────────────────────────────────────────────────
    TELEGRAM_TOKEN : str = os.environ.get("TELEGRAM_TOKEN", "")
    PORT           : int = int(os.environ.get("PORT", 5001))
    BASE_URL       : str = os.environ.get("BASE_URL", "")

    # ── Base de datos ─────────────────────────────────────────────────────────
    DB_HOST : str = os.environ.get("DB_HOST", "localhost")
    DB_NAME : str = os.environ.get("DB_NAME", "calcifer_db")
    DB_USER : str = os.environ.get("DB_USER", "calcifer_user")
    DB_PASS : str = os.environ.get("DB_PASS", "")
    DB_PORT : int = int(os.environ.get("DB_PORT", 3306))

    # ── Pasarelas ─────────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY     : str = os.environ.get("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET : str = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    PAYPAL_CLIENT_ID      : str = os.environ.get("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET  : str = os.environ.get("PAYPAL_CLIENT_SECRET", "")
    SQUARE_ACCESS_TOKEN   : str = os.environ.get("SQUARE_ACCESS_TOKEN", "")
    AMAZON_PUBLIC_KEY     : str = os.environ.get("AMAZON_PUBLIC_KEY", "")
    ADYEN_API_KEY         : str = os.environ.get("ADYEN_API_KEY", "")
    MONERIS_STORE_ID      : str = os.environ.get("MONERIS_STORE_ID", "")
    MONERIS_API_TOKEN     : str = os.environ.get("MONERIS_API_TOKEN", "")
    ZUORA_CLIENT_ID       : str = os.environ.get("ZUORA_CLIENT_ID", "")
    ZUORA_CLIENT_SECRET   : str = os.environ.get("ZUORA_CLIENT_SECRET", "")

    # ── 911Proxy ──────────────────────────────────────────────────────────────
    PROXY_USER : str = os.environ.get("PROXY_USER", "")
    PROXY_PASS : str = os.environ.get("PROXY_PASS", "")
    PROXY_HOST : str = os.environ.get("PROXY_HOST", "")
    PROXY_PORT : str = os.environ.get("PROXY_PORT", "")

    # ── Configuración dinámica (por framework/módulo) ─────────────────────────
    _dynamic: dict = {}

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración dinámica."""
        return cls._dynamic.get(key, default)

    @classmethod
    def set(cls, key: str, value: Any):
        """Establece un valor de configuración dinámica sin reinicio."""
        cls._dynamic[key] = value

    @classmethod
    def get_framework_config(cls, framework: str) -> dict:
        """Retorna la configuración específica de un framework."""
        prefix = f"framework.{framework}."
        return {
            k[len(prefix):]: v
            for k, v in cls._dynamic.items()
            if k.startswith(prefix)
        }

    @classmethod
    def get_module_config(cls, framework: str, module: str) -> dict:
        """Retorna la configuración específica de un módulo."""
        prefix = f"module.{framework}.{module}."
        return {
            k[len(prefix):]: v
            for k, v in cls._dynamic.items()
            if k.startswith(prefix)
        }

    @classmethod
    def load_from_file(cls, path: str) -> bool:
        """Recarga configuración dinámica desde un archivo JSON."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cls._dynamic.update(data)
            return True
        except Exception as e:
            print(f"[CONFIG] Error cargando {path}: {e}")
            return False

    @classmethod
    def reload_env(cls):
        """Recarga las variables de entorno sin reinicio."""
        load_dotenv(override=True)
        cls.TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
        cls.DB_PASS        = os.environ.get("DB_PASS", "")

    @classmethod
    def validate(cls) -> bool:
        required = ["TELEGRAM_TOKEN", "DB_HOST", "DB_NAME", "DB_USER", "DB_PASS"]
        missing  = [k for k in required if not getattr(cls, k)]
        if missing:
            print(f"[CONFIG ERROR] Variables faltantes: {missing}")
            return False
        return True

    @classmethod
    def get_db_config(cls) -> dict:
        return {
            "host"    : cls.DB_HOST,
            "database": cls.DB_NAME,
            "user"    : cls.DB_USER,
            "password": cls.DB_PASS,
            "port"    : cls.DB_PORT,
        }


config = ConfigManager()
