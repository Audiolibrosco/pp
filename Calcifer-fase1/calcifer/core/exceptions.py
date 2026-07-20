"""
🔥 Calcifer Core — Exceptions
Autor: Calcifer Team | Versión: 1.1.0
Jerarquía completa de excepciones con códigos de error unificados.
"""


# ── Códigos de error unificados ───────────────────────────────────────────────
ERROR_CODES = {
    # Usuario
    "ERR001": "Formato inválido",
    "ERR002": "Tarjeta vencida",
    "ERR003": "Créditos insuficientes",
    "ERR004": "Sin permisos",
    "ERR013": "Usuario bloqueado",
    "ERR016": "Usuario no registrado",
    "ERR006": "Timeout",
    "ERR007": "Browser no inició",
    "ERR008": "Página no cargó",
    "ERR009": "BIN lookup falló",
    # Sistema / Core
    "ERR005": "Error interno",
    "ERR010": "Módulo en mantenimiento",
    "ERR011": "Base de datos no disponible",
    "ERR012": "Configuración inválida",
    "ERR014": "Módulo no encontrado",
    "ERR015": "Versión incompatible",
    "ERR017": "Framework no encontrado",
    "ERR018": "Contrato inválido",
    "ERR019": "Parámetro inválido",
    "ERR020": "Framework inactivo",
}


class CalciferError(Exception):
    """Error base de Calcifer. Todo error hereda de aquí."""
    code: str = "ERR005"

    def __init__(self, message: str = "", code: str = None):
        self.message = message or ERROR_CODES.get(self.code, "Error desconocido")
        if code:
            self.code = code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "code"   : self.code,
            "message": self.message,
            "type"   : self.__class__.__name__,
        }


# ── Errores de usuario ────────────────────────────────────────────────────────
class InvalidFormatError(CalciferError):
    code = "ERR001"

class ExpiredCardError(CalciferError):
    code = "ERR002"

class InsufficientCreditsError(CalciferError):
    code = "ERR003"

class PermissionDeniedError(CalciferError):
    code = "ERR004"

class UserBlockedError(CalciferError):
    code = "ERR013"

class UserNotFoundError(CalciferError):
    code = "ERR016"

class UserNotRegisteredError(CalciferError):
    code = "ERR016"


# ── Errores de automatización ─────────────────────────────────────────────────
class TimeoutError(CalciferError):
    code = "ERR006"

class BrowserError(CalciferError):
    code = "ERR007"

class PageNotLoadedError(CalciferError):
    code = "ERR008"

class BinLookupError(CalciferError):
    code = "ERR009"


# ── Errores de sistema ────────────────────────────────────────────────────────
class InternalError(CalciferError):
    code = "ERR005"

class ModuleMaintenanceError(CalciferError):
    code = "ERR010"

class DatabaseError(CalciferError):
    code = "ERR011"

class ConfigError(CalciferError):
    code = "ERR012"

class ModuleNotFoundError(CalciferError):
    code = "ERR014"

class ModuleNotActiveError(CalciferError):
    code = "ERR010"

class VersionIncompatibleError(CalciferError):
    code = "ERR015"

class FrameworkNotFoundError(CalciferError):
    code = "ERR017"

class InvalidContractError(CalciferError):
    code = "ERR018"

class InvalidParameterError(CalciferError):
    code = "ERR019"

class FrameworkInactiveError(CalciferError):
    code = "ERR020"

# ── Alias de compatibilidad ───────────────────────────────────────────────────
GatewayError = InternalError


def log_exception_to_audit(error: "CalciferError", telegram_id: int = 0,
                               username: str = "", command: str = "",
                               framework: str = "", module: str = "") -> None:
    """Registra automáticamente una excepción en el AuditManager."""
    try:
        from core.audit_manager import audit_manager
        audit_manager.log(
            telegram_id    = telegram_id,
            username       = username,
            command        = command,
            framework      = framework,
            module         = module,
            status         = getattr(error, "code", "ERR005"),
            execution_time = 0,
            credits_before = 0,
            credits_after  = 0,
            response       = str(error),
            error_code     = getattr(error, "code", "ERR005"),
        )
    except Exception:
        pass  # No propagar errores del sistema de audit


def error_to_status(error: "CalciferError") -> str:
    """Convierte una excepción a su código de status para contract_out."""
    return getattr(error, "code", "ERR005")


def get_error_message(code: str) -> str:
    """Retorna el mensaje oficial de un código de error."""
    return ERROR_CODES.get(code, "Error desconocido")
