"""
🔥 Calcifer Core — v1.1.0 (Phase B.3)
Autor: Calcifer Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLUJO OFICIAL DEL CORE — única ruta de ejecución válida
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Telegram
    ↓
Dispatcher.dispatch()      ← punto único de entrada
    ↓
Security.sanitize_all()    ← sanitización centralizada
    ↓
PermissionManager          ← valida rol del usuario
    ↓
CreditsManager             ← valida y descuenta créditos
    ↓
Registry                   ← verifica que el módulo existe
    ↓
FrameworkManager           ← verifica que el framework está activo
    ↓
ModuleManager              ← gestiona ciclo de vida del módulo
    ↓
módulo.run(ContractIn)     ← lógica específica del módulo
    ↓
ContractOut                ← resultado estructurado
    ↓
ResponseBuilder            ← construye el mensaje para Telegram
    ↓
AuditManager               ← registra la ejecución completa
    ↓
Logger                     ← registra eventos del sistema
    ↓
EventBus                   ← publica eventos internos
    ↓
Telegram (respuesta)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGLAS OBLIGATORIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Todo comando entra por Dispatcher — sin excepciones
✅ Todo módulo recibe ContractIn y devuelve ContractOut
✅ Ningún módulo valida permisos por su cuenta
✅ Ningún módulo descuenta créditos directamente
✅ Ningún módulo construye mensajes de Telegram
✅ Toda ejecución queda registrada en AuditManager
✅ Todo error sigue: Exception → Logger → Audit → ResponseBuilder

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CICLO DE VIDA DE UN MÓDULO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Inicio → Validación → Permisos → Créditos →
Inicialización → Ejecución → Resultado →
Auditoría → Respuesta → Finalización

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPONENTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  dispatcher.py         → Punto único de entrada
  security.py           → Validación y sanitización
  permission_manager.py → Roles y permisos
  credits.py            → Gestión de créditos
  registry.py           → Catálogo de módulos
  framework_manager.py  → Gestión de frameworks
  module_manager.py     → Ciclo de vida de módulos
  contracts.py          → ContractIn y ContractOut
  response_builder.py   → Construcción de respuestas
  audit_manager.py      → Registro de ejecuciones
  logger.py             → Sistema de logs
  event_bus.py          → Eventos internos
  core_status.py        → Estado del sistema
  exceptions.py         → Jerarquía de errores
  config_manager.py     → Configuración centralizada
  version.py            → Versionado y compatibilidad
"""
from core.version import VERSION
__version__ = VERSION
