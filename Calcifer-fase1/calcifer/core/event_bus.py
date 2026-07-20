"""
🔥 Calcifer Core — Event Bus
Autor: Calcifer Team | Versión: 1.0.0
Bus de eventos internos para comunicación entre componentes.
"""
from typing import Callable, Dict, List, Any
from core.logger import logger


# Eventos oficiales del sistema
EVENT_MODULE_LOADED    = "module_loaded"
EVENT_MODULE_STARTED   = "module_started"
EVENT_MODULE_FINISHED  = "module_finished"
EVENT_MODULE_ERROR     = "module_error"
EVENT_CREDITS_CONSUMED = "credits_consumed"
EVENT_USER_BLOCKED     = "user_blocked"
EVENT_MAINTENANCE_ON   = "maintenance_on"
EVENT_MAINTENANCE_OFF  = "maintenance_off"
EVENT_FRAMEWORK_ACTIVE   = "framework_active"
EVENT_FRAMEWORK_DISABLED = "framework_disabled"
EVENT_USER_AUTHENTICATED = "user_authenticated"
EVENT_MODULE_LOADED      = "module_loaded"


class EventBus:
    """Bus de eventos para comunicación interna entre componentes de Calcifer."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, handler: Callable):
        """Suscribe un handler a un evento."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        logger.debug(f"Suscrito a evento: {event}", "EVENT_BUS")

    def unsubscribe(self, event: str, handler: Callable):
        """Cancela la suscripción de un handler."""
        if event in self._handlers and handler in self._handlers[event]:
            self._handlers[event].remove(handler)

    def emit(self, event: str, data: Any = None):
        """Emite un evento a todos sus suscriptores."""
        handlers = self._handlers.get(event, [])
        logger.debug(f"Evento emitido: {event} → {len(handlers)} handlers", "EVENT_BUS")
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error en handler de {event}: {e}", "EVENT_BUS")

    def emit_module_started(self, module: str, framework: str, user: str):
        self.emit(EVENT_MODULE_STARTED, {
            "module": module, "framework": framework, "user": user
        })

    def emit_module_finished(self, module: str, framework: str, status: str, time: int):
        self.emit(EVENT_MODULE_FINISHED, {
            "module": module, "framework": framework, "status": status, "time": time
        })

    def emit_module_error(self, module: str, error_code: str):
        self.emit(EVENT_MODULE_ERROR, {"module": module, "error_code": error_code})

    def emit_framework_disabled(self, framework: str):
        self.emit(EVENT_FRAMEWORK_DISABLED, {"framework": framework})

    def emit_user_authenticated(self, telegram_id: int, username: str, role: str):
        self.emit(EVENT_USER_AUTHENTICATED, {
            "telegram_id": telegram_id, "username": username, "role": role
        })

    def emit_module_loaded(self, module: str, framework: str):
        self.emit(EVENT_MODULE_LOADED, {"module": module, "framework": framework})

    def emit_credits_consumed(self, telegram_id: int, amount: int, remaining: int):
        self.emit(EVENT_CREDITS_CONSUMED, {
            "telegram_id": telegram_id, "amount": amount, "remaining": remaining
        })


event_bus = EventBus()
