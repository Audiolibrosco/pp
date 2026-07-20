"""
🔥 Calcifer Core — Version Manager
Autor: Calcifer Team | Versión: 1.1.0
Control de versiones con política de compatibilidad y migración.
"""

VERSION    = "1.1.0"
PHASE      = "B.3"
BUILD_DATE = "2026-07-04"
CODENAME   = "Calcifer Core"
STATUS     = "stable"

VERSION_INFO = {
    "version"   : VERSION,
    "phase"     : PHASE,
    "build_date": BUILD_DATE,
    "codename"  : CODENAME,
    "status"    : STATUS,
}

# ── Política de compatibilidad ────────────────────────────────────────────────
# MAJOR.MINOR.PATCH
# MAJOR → rompe compatibilidad de contratos o API interna
# MINOR → nueva función sin romper compatibilidad
# PATCH → corrección de bug sin cambio de comportamiento

COMPATIBILITY_POLICY = {
    "breaking_change": "MAJOR",
    "new_feature"    : "MINOR",
    "bug_fix"        : "PATCH",
}

# ── Política de migración ─────────────────────────────────────────────────────
MIGRATION_NOTES = {
    "1.0.0 → 1.1.0": [
        "Dispatcher añadido — usar dispatcher.dispatch() en lugar de llamadas directas",
        "Response Builder añadido — usar response_builder.from_contract_out()",
        "Security añadido — todos los inputs pasan por security.sanitize()",
        "Event Bus añadido — suscribirse a eventos con event_bus.subscribe()",
        "Framework Manager añadido — registrar frameworks con framework_manager.register()",
        "Credits: add() ahora solo acepta 250 o 500",
    ]
}

MIN_MODULE_CORE = "1.0.0"  # versión mínima del Core que un módulo puede requerir


def get_version() -> str:
    return VERSION

def get_version_string() -> str:
    return f"Calcifer v{VERSION} (Phase {PHASE}) — {BUILD_DATE}"

def get_version_info() -> dict:
    return VERSION_INFO

def is_compatible(required_version: str) -> bool:
    """Verifica si la versión actual es compatible con la requerida."""
    try:
        current = [int(x) for x in VERSION.split(".")]
        required = [int(x) for x in required_version.split(".")]
        return current >= required
    except Exception:
        return True

def get_migration_notes(from_version: str) -> list:
    """Retorna las notas de migración desde una versión anterior."""
    key = f"{from_version} → {VERSION}"
    return MIGRATION_NOTES.get(key, [])
