"""
🔥 Calcifer Core — Module Manager
Autor: Calcifer Team | Versión: 1.1.0
Ejecución, ciclo de vida, habilitación/deshabilitación y monitoreo de módulos.
"""
from enum import Enum
from typing import Optional, Callable, Any, Dict
from core.registry import registry, ModuleManifest
from core.logger import logger
from core.exceptions import ModuleNotFoundError, ModuleNotActiveError


class ModuleState(Enum):
    ACTIVE      = "active"
    INACTIVE    = "inactive"
    MAINTENANCE = "maintenance"
    ERROR       = "error"


class ModuleManager:
    """Gestor de ciclo de vida y ejecución de módulos."""

    def __init__(self):
        self._handlers  : Dict[str, Dict[str, Callable]] = {}
        self._error_count: Dict[str, int] = {}

    # ── Registro de handlers ──────────────────────────────────────────────────

    def register_handler(self, module_name: str, command: str, handler: Callable):
        if module_name not in self._handlers:
            self._handlers[module_name] = {}
        self._handlers[module_name][command] = handler
        logger.info(f"Handler: {module_name} → {command}", "MODULE_MANAGER")

    def get_handler(self, command: str) -> Optional[Callable]:
        module = registry.get_by_command(command)
        if not module:
            raise ModuleNotFoundError(f"Sin módulo para: {command}")
        if not module.is_active():
            raise ModuleNotActiveError(f"'{module.name}' está en {module.status}")
        return self._handlers.get(module.name, {}).get(command)

    # ── Ejecución ─────────────────────────────────────────────────────────────

    async def execute(self, command: str, *args, **kwargs) -> Any:
        try:
            handler = self.get_handler(command)
            if not handler:
                logger.warning(f"Sin handler para: {command}", "MODULE_MANAGER")
                return None
            return await handler(*args, **kwargs)
        except (ModuleNotFoundError, ModuleNotActiveError) as e:
            logger.warning(str(e), "MODULE_MANAGER")
            raise
        except Exception as e:
            logger.error(f"Error ejecutando '{command}': {e}", "MODULE_MANAGER")
            raise

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def enable(self, module_name: str) -> bool:
        """Habilita un módulo (active)."""
        result = registry.set_status(module_name, ModuleState.ACTIVE.value)
        if result:
            self._error_count.pop(module_name, None)
            logger.audit("SYSTEM", "system", "MODULE_ENABLED", module_name)
        return result

    def disable(self, module_name: str) -> bool:
        """Deshabilita un módulo (inactive)."""
        result = registry.set_status(module_name, ModuleState.INACTIVE.value)
        if result:
            logger.audit("SYSTEM", "system", "MODULE_DISABLED", module_name)
        return result

    def set_maintenance(self, module_name: str) -> bool:
        """Pone un módulo en mantenimiento."""
        result = registry.set_status(module_name, ModuleState.MAINTENANCE.value)
        if result:
            logger.audit("SYSTEM", "system", "MAINTENANCE_ON", module_name)
        return result

    def set_active(self, module_name: str) -> bool:
        """Reactiva un módulo desde mantenimiento."""
        return self.enable(module_name)

    def set_error(self, module_name: str) -> bool:
        """Marca un módulo con estado de error."""
        self._error_count[module_name] = self._error_count.get(module_name, 0) + 1
        result = registry.set_status(module_name, ModuleState.ERROR.value)
        if result:
            logger.error(f"Módulo en estado ERROR: {module_name}", "MODULE_MANAGER")
        return result

    def restart(self, module_name: str) -> bool:
        """Reinicia un módulo (disable → enable)."""
        self.disable(module_name)
        result = self.enable(module_name)
        if result:
            logger.info(f"Módulo reiniciado: {module_name}", "MODULE_MANAGER")
        return result

    # ── Estado y monitoreo ────────────────────────────────────────────────────

    def get_state(self, module_name: str) -> Optional[ModuleState]:
        module = registry.get(module_name)
        if not module:
            return None
        try:
            return ModuleState(module.status)
        except ValueError:
            return ModuleState.ERROR

    def get_status(self) -> str:
        return registry.list_modules()

    def get_error_count(self, module_name: str) -> int:
        return self._error_count.get(module_name, 0)

    def release(self, module_name: str):
        """Libera los recursos de un módulo (handlers)."""
        if module_name in self._handlers:
            del self._handlers[module_name]
            logger.info("Recursos liberados: " + module_name, "MODULE_MANAGER")

    def set_timeout(self, module_name: str, timeout_seconds: int):
        """Registra el timeout configurado para un módulo."""
        if not hasattr(self, "_timeouts"):
            self._timeouts = {}
        self._timeouts[module_name] = timeout_seconds
        logger.info("Timeout: " + module_name + " = " + str(timeout_seconds) + "s", "MODULE_MANAGER")

    def get_timeout(self, module_name: str, default: int = 120) -> int:
        """Obtiene el timeout de un módulo."""
        if not hasattr(self, "_timeouts"):
            return default
        return self._timeouts.get(module_name, default)

    def get_summary(self) -> dict:
        modules = registry.get_all()
        return {
            "total"      : len(modules),
            "active"     : sum(1 for m in modules.values() if m.status == "active"),
            "inactive"   : sum(1 for m in modules.values() if m.status == "inactive"),
            "maintenance": sum(1 for m in modules.values() if m.status == "maintenance"),
            "error"      : sum(1 for m in modules.values() if m.status == "error"),
        }


module_manager = ModuleManager()
