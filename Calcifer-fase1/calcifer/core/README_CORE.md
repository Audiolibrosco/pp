# 🔥 Calcifer Core v1.1.0 — Phase B.3

Núcleo central del sistema Calcifer. Base compartida para todos los módulos.

## Archivos del Core

| Archivo | Fase | Responsabilidad |
|---|---|---|
| `version.py` | F20 | Versión, compatibilidad y migración |
| `exceptions.py` | F11 | Jerarquía completa de errores (ERR001-ERR020) |
| `logger.py` | F9 | Logs por módulo, framework, rotación y JSON |
| `config_manager.py` | F6 | Config global, por framework y módulo. Recarga dinámica |
| `permission_manager.py` | F7 | Permisos por comando, módulo y framework |
| `registry.py` | F2 | Catálogo, descubrimiento automático y validación de metadata |
| `module_manager.py` | F3 | Ciclo de vida, enable/disable/restart/error |
| `contracts.py` | F5 | ContractIn, ContractOut, validación automática |
| `credits.py` | F8 | Créditos: consulta, descuento, recarga (250/500), historial |
| `audit_manager.py` | F10 | Registro completo de cada operación |
| `response_builder.py` | F12 | Mensajes uniformes para Telegram |
| `framework_manager.py` | F13 | Gestión de frameworks (Stripe, PayPal, etc.) |
| `event_bus.py` | F14 | Eventos internos entre componentes |
| `core_status.py` | F15 | Estado del sistema en tiempo real |
| `security.py` | F16 | Validación, sanitización y protección |
| `dispatcher.py` | F4 | Punto único de entrada para todos los comandos |

## Flujo de un comando

```
Telegram → dispatcher.dispatch()
    → security (sanitizar)
    → permissions (validar rol)
    → framework_manager (verificar framework)
    → registry (verificar módulo)
    → credits (validar saldo)
    → ContractIn (construir)
    → módulo.run(contract_in)
    → ContractOut (recibir)
    → credits.deduct (si aplica)
    → audit_manager.log
    → response_builder.from_contract_out
    → Telegram (respuesta)
```

## Recarga de créditos individuales
Los créditos se pueden agregar individualmente (fuera de membresía)
solo en cantidades de **250 o 500** — los mismos valores de las membresías.

## Tests
```bash
cd /root/calcifer && python3 core/tests.py
```

## Versión
1.1.0 — Phase B.3
