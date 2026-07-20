"""
🔥 Calcifer Core — Contracts
Autor: Calcifer Team
Versión: 1.0.0
Propósito: Lenguaje oficial entre el Core y todos los módulos.

Reglas:
  - contract_in  → siempre lo construye el Core, nunca el módulo
  - contract_out → siempre lo construye el módulo, nunca el Core
  - El módulo NUNCA lanza excepciones al Core
  - El módulo SIEMPRE devuelve un contract_out, incluso en error
  - Todos los campos siempre presentes (None si no aplica)
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


# ─────────────────────────────────────────────────────────────────────────────
# CONTRACT IN — lo que el Core entrega a cualquier módulo
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ContractUser:
    """Datos del usuario que ejecuta el comando."""
    user_id     : int       # ID interno en calcifer_db
    telegram_id : int       # ID de Telegram
    username    : str       # @username sin arroba
    membership  : str       # Owner | Seller | Premium | Basic | Free
    credits     : int       # -1 = ilimitado (Owner / Seller)
    role_level  : int       # 100=Owner, 80=Seller, 60=Premium, 40=Basic, 20=Free


@dataclass
class ContractCommand:
    """Datos del comando recibido."""
    trigger     : str       # "/sc"
    raw_params  : str       # "4242424242424242|01|2028|111"
    params_list : List[str] # ["4242424242424242", "01", "2028", "111"]


@dataclass
class ContractModule:
    """Datos del módulo que se va a ejecutar."""
    name        : str       # "start"
    framework   : str       # "stripe"
    version     : str       # "1.0.0"
    visible_name: str       # "Start"


@dataclass
class ContractEnv:
    """Datos del entorno de ejecución."""
    timestamp   : str       # "2026-07-04T18:42:00"
    server      : str       # "bold-webhook-server"
    debug       : bool      # False en producción


@dataclass
class ContractIn:
    """
    Contrato de entrada oficial de Calcifer.
    El Core lo construye antes de invocar cualquier módulo.
    """
    user    : ContractUser
    command : ContractCommand
    module  : ContractModule
    env     : ContractEnv

    @classmethod
    def build(
        cls,
        user_id      : int,
        telegram_id  : int,
        username     : str,
        membership   : str,
        credits      : int,
        role_level   : int,
        trigger      : str,
        raw_params   : str,
        module_name  : str,
        framework    : str,
        version      : str,
        visible_name : str,
        server       : str  = "bold-webhook-server",
        debug        : bool = False,
    ) -> "ContractIn":
        """Constructor oficial del ContractIn."""
        return cls(
            user=ContractUser(
                user_id     = user_id,
                telegram_id = telegram_id,
                username    = username,
                membership  = membership,
                credits     = credits,
                role_level  = role_level,
            ),
            command=ContractCommand(
                trigger     = trigger,
                raw_params  = raw_params,
                params_list = raw_params.split("|") if raw_params else [],
            ),
            module=ContractModule(
                name         = module_name,
                framework    = framework,
                version      = version,
                visible_name = visible_name,
            ),
            env=ContractEnv(
                timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                server    = server,
                debug     = debug,
            ),
        )

    def to_dict(self) -> dict:
        """Serializa el ContractIn a diccionario."""
        return {
            "user": {
                "user_id"    : self.user.user_id,
                "telegram_id": self.user.telegram_id,
                "username"   : self.user.username,
                "membership" : self.user.membership,
                "credits"    : self.user.credits,
                "role_level" : self.user.role_level,
            },
            "command": {
                "trigger"    : self.command.trigger,
                "raw_params" : self.command.raw_params,
                "params_list": self.command.params_list,
            },
            "module": {
                "name"        : self.module.name,
                "framework"   : self.module.framework,
                "version"     : self.module.version,
                "visible_name": self.module.visible_name,
            },
            "env": {
                "timestamp": self.env.timestamp,
                "server"   : self.env.server,
                "debug"    : self.env.debug,
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# CONTRACT OUT — lo que cualquier módulo devuelve al Core
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ContractCardInfo:
    """Información de la tarjeta procesada."""
    brand : Optional[str] = None    # "Visa" | "Mastercard" | "Amex"
    type  : Optional[str] = None    # "Debit" | "Credit" | "Prepaid"
    level : Optional[str] = None    # "Classic" | "Gold" | "Platinum"


@dataclass
class ContractLogData:
    """Datos internos para el sistema de logs."""
    events   : List[str] = field(default_factory=list)
    retries  : int       = 0
    headless : bool      = True


@dataclass
class ContractOut:
    """
    Contrato de salida oficial de Calcifer.
    El módulo lo construye y lo entrega al Core.

    REGLA: Siempre se devuelve, incluso en error.
           El módulo NUNCA lanza excepciones al Core.
    """
    status          : str                   # CHARGED | DECLINED | PENDING_3DS | ERR001...
    response        : str                   # Texto crudo de la plataforma
    gateway         : str                   # "Start"
    module          : str                   # "start"
    execution_time  : int                   # Segundos que tardó
    card            : ContractCardInfo      # brand, type, level
    bank            : Optional[str] = None  # "BBVA Colombia"
    country         : Optional[str] = None  # "Colombia"
    country_flag    : Optional[str] = None  # "🇨🇴"
    message         : Optional[str] = None  # Mensaje formateado para Telegram
    error_code      : Optional[str] = None  # None o "ERR005"
    log_data        : ContractLogData = field(default_factory=ContractLogData)

    # ── Helpers de estado ─────────────────────────────────────────────────────

    def is_success(self) -> bool:
        return self.status == "CHARGED"

    def is_declined(self) -> bool:
        return self.status == "DECLINED"

    def is_pending(self) -> bool:
        return self.status == "PENDING_3DS"

    def is_error(self) -> bool:
        return self.status.startswith("ERR")

    def should_deduct_credits(self) -> bool:
        """
        True si se deben descontar créditos.
        Solo en resultados reales: CHARGED, DECLINED, PENDING_3DS.
        Nunca en errores internos (ERR*).
        """
        return self.status in {"CHARGED", "DECLINED", "PENDING_3DS"}

    # ── Constructores de conveniencia ─────────────────────────────────────────

    @classmethod
    def success(cls, gateway, module, response, execution_time, card,
                bank=None, country=None, country_flag=None, log_data=None) -> "ContractOut":
        """Tarjeta aprobada."""
        return cls(
            status="CHARGED", response=response, gateway=gateway, module=module,
            execution_time=execution_time, card=card, bank=bank,
            country=country, country_flag=country_flag,
            log_data=log_data or ContractLogData(),
        )

    @classmethod
    def declined(cls, gateway, module, response, execution_time, card,
                 bank=None, country=None, country_flag=None, log_data=None) -> "ContractOut":
        """Tarjeta rechazada."""
        return cls(
            status="DECLINED", response=response, gateway=gateway, module=module,
            execution_time=execution_time, card=card, bank=bank,
            country=country, country_flag=country_flag,
            log_data=log_data or ContractLogData(),
        )

    @classmethod
    def pending_3ds(cls, gateway, module, execution_time, log_data=None) -> "ContractOut":
        """3D Secure pendiente."""
        return cls(
            status="PENDING_3DS", response="3D Secure Required",
            gateway=gateway, module=module, execution_time=execution_time,
            card=ContractCardInfo(), log_data=log_data or ContractLogData(),
        )

    @classmethod
    def error(cls, gateway, module, error_code, response, execution_time=0, log_data=None) -> "ContractOut":
        """Error interno — nunca descuenta créditos."""
        return cls(
            status=error_code, response=response, gateway=gateway, module=module,
            execution_time=execution_time, card=ContractCardInfo(),
            error_code=error_code, log_data=log_data or ContractLogData(),
        )

    def to_dict(self) -> dict:
        """Serializa el ContractOut a diccionario."""
        return {
            "status"        : self.status,
            "response"      : self.response,
            "gateway"       : self.gateway,
            "module"        : self.module,
            "execution_time": self.execution_time,
            "card": {
                "brand": self.card.brand,
                "type" : self.card.type,
                "level": self.card.level,
            },
            "bank"          : self.bank,
            "country"       : self.country,
            "country_flag"  : self.country_flag,
            "message"       : self.message,
            "error_code"    : self.error_code,
            "log_data": {
                "events"  : self.log_data.events,
                "retries" : self.log_data.retries,
                "headless": self.log_data.headless,
            },
        }


# ── Validación automática de contratos ────────────────────────────────────────

CONTRACT_VERSION = "1.0.0"

REQUIRED_CONTRACT_IN_FIELDS = [
    ("user", "user_id"), ("user", "telegram_id"), ("user", "username"),
    ("user", "membership"), ("user", "credits"),
    ("command", "trigger"), ("module", "name"), ("module", "framework"),
]

REQUIRED_CONTRACT_OUT_FIELDS = [
    "status", "response", "gateway", "module", "execution_time"
]


def validate_contract_in(data: dict) -> bool:
    """Valida que un contract_in tenga todos los campos requeridos."""
    for section, field in REQUIRED_CONTRACT_IN_FIELDS:
        if section not in data or field not in data[section]:
            return False
    return True


def validate_contract_out(data: dict) -> bool:
    """Valida que un contract_out tenga todos los campos requeridos."""
    return all(f in data for f in REQUIRED_CONTRACT_OUT_FIELDS)
