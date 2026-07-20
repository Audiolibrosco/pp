"""
🔥 Calcifer Core — Permission Manager
Autor: Calcifer Team | Versión: 1.1.0
Permisos por módulo, comando y framework.
"""
from enum import Enum
from typing import List, Dict


class Role(Enum):
    OWNER   = "Owner"
    SELLER  = "Seller"
    PREMIUM = "Premium"
    BASIC   = "Basic"
    FREE    = "Free"
    TRIAL   = "Trial"


ROLE_HIERARCHY: Dict[Role, int] = {
    Role.OWNER  : 100,
    Role.SELLER : 80,
    Role.PREMIUM: 60,
    Role.BASIC  : 40,
    Role.FREE   : 20,
    Role.TRIAL  : 10,
}

# Permisos por comando
COMMAND_PERMISSIONS: Dict[str, List[Role]] = {
    "/start"        : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE, Role.TRIAL],
    "/register"     : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE, Role.TRIAL],
    "/perfil"       : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE],
    "/ayuda"        : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE],
    "/estado"       : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE],
    "/pasarelas"    : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE],
    "/verificar"    : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE],
    "/historial"    : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE],
    "/addmembresia" : [Role.OWNER, Role.SELLER],
    "/deluser"      : [Role.OWNER, Role.SELLER],
    "/blockuser"    : [Role.OWNER, Role.SELLER],
    "/unblockuser"  : [Role.OWNER, Role.SELLER],
}

# Permisos por framework
FRAMEWORK_PERMISSIONS: Dict[str, List[Role]] = {
    "stripe" : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC],
    "paypal" : [Role.OWNER, Role.SELLER, Role.PREMIUM],
    "shopify": [Role.OWNER, Role.SELLER, Role.PREMIUM],
    "adyen"  : [Role.OWNER, Role.SELLER, Role.PREMIUM],
    "square" : [Role.OWNER, Role.SELLER, Role.PREMIUM],
    "moneris": [Role.OWNER, Role.SELLER, Role.PREMIUM],
}

# Permisos por módulo
MODULE_PERMISSIONS: Dict[str, List[Role]] = {
    "start"  : [Role.OWNER, Role.SELLER, Role.PREMIUM, Role.BASIC, Role.FREE],
}

ADMIN_ROLES            = [Role.OWNER, Role.SELLER]
UNLIMITED_CREDIT_ROLES = [Role.OWNER, Role.SELLER]


class PermissionManager:

    @staticmethod
    def has_permission(role_str: str, command: str) -> bool:
        try:
            role    = Role(role_str)
            allowed = COMMAND_PERMISSIONS.get(command, [])
            return role in allowed
        except ValueError:
            return False

    @staticmethod
    def has_framework_permission(role_str: str, framework: str) -> bool:
        try:
            role    = Role(role_str)
            allowed = FRAMEWORK_PERMISSIONS.get(framework, [])
            return role in allowed
        except ValueError:
            return False

    @staticmethod
    def has_module_permission(role_str: str, module: str) -> bool:
        try:
            role    = Role(role_str)
            allowed = MODULE_PERMISSIONS.get(module, [])
            return role in allowed
        except ValueError:
            return False

    @staticmethod
    def is_admin(role_str: str) -> bool:
        try:
            return Role(role_str) in ADMIN_ROLES
        except ValueError:
            return False

    @staticmethod
    def has_unlimited_credits(role_str: str) -> bool:
        try:
            return Role(role_str) in UNLIMITED_CREDIT_ROLES
        except ValueError:
            return False

    @staticmethod
    def get_role_level(role_str: str) -> int:
        try:
            return ROLE_HIERARCHY.get(Role(role_str), 0)
        except ValueError:
            return 0

    @staticmethod
    def get_allowed_commands(role_str: str) -> List[str]:
        try:
            role = Role(role_str)
            return [cmd for cmd, roles in COMMAND_PERMISSIONS.items() if role in roles]
        except ValueError:
            return []

    @staticmethod
    def register_command(command: str, roles: List[str]):
        """Registra un nuevo comando con sus permisos en tiempo de ejecución."""
        COMMAND_PERMISSIONS[command] = [
            Role(r) for r in roles if r in Role._value2member_map_
        ]


permissions = PermissionManager()
