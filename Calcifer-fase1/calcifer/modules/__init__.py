"""
🔥 CALCIFER — Módulos
Carpeta raíz de todos los módulos de Calcifer.

CONTRATO DE UN MÓDULO:
Cada módulo debe tener esta estructura:

modules/
└── nombre_modulo/
    ├── __init__.py      ← registro del módulo
    ├── manifest.py      ← metadata del módulo
    ├── commands.py      ← handlers de comandos
    ├── service.py       ← lógica de negocio
    └── config.py        ← configuración específica

EJEMPLO de manifest.py:
    from core.registry import ModuleManifest

    MANIFEST = ModuleManifest(
        name        = "gateway.stripe",
        version     = "1.0.0",
        author      = "Calcifer Team",
        description = "Pasarela Stripe",
        status      = "active",
        commands    = ["/pagar"],
        permissions = ["Owner", "Seller", "Premium", "Basic"],
    )

EJEMPLO de __init__.py:
    from core.registry import registry
    from modules.stripe.manifest import MANIFEST
    from modules.stripe.commands import handle_pagar

    def setup(manager):
        registry.register(MANIFEST)
        manager.register_handler(MANIFEST.name, "/pagar", handle_pagar)
"""
