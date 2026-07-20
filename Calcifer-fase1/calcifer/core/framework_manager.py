"""
🔥 Calcifer Core — Framework Manager
Autor: Calcifer Team | Versión: 1.0.0
Administra todos los frameworks de Calcifer.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from core.logger import logger


@dataclass
class FrameworkManifest:
    name        : str
    version     : str
    description : str
    status      : str
    modules     : List[str] = field(default_factory=list)
    min_core    : str = "1.0.0"

    def is_active(self) -> bool:
        return self.status == "active"

    def to_dict(self) -> dict:
        return {
            "name"       : self.name,
            "version"    : self.version,
            "description": self.description,
            "status"     : self.status,
            "modules"    : self.modules,
            "min_core"   : self.min_core,
        }


class FrameworkManager:

    def __init__(self):
        self._frameworks: Dict[str, FrameworkManifest] = {}

    def register(self, manifest: FrameworkManifest) -> bool:
        self._frameworks[manifest.name] = manifest
        logger.info("Framework registrado: " + manifest.name + " v" + manifest.version, "FRAMEWORK")
        return True

    def get(self, name: str) -> Optional[FrameworkManifest]:
        return self._frameworks.get(name)

    def get_all(self) -> Dict[str, FrameworkManifest]:
        return self._frameworks.copy()

    def get_active(self) -> List[FrameworkManifest]:
        return [f for f in self._frameworks.values() if f.is_active()]

    def activate(self, name: str) -> bool:
        if name not in self._frameworks:
            return False
        self._frameworks[name].status = "active"
        logger.info("Framework activado: " + name, "FRAMEWORK")
        return True

    def deactivate(self, name: str) -> bool:
        if name not in self._frameworks:
            return False
        self._frameworks[name].status = "inactive"
        logger.info("Framework desactivado: " + name, "FRAMEWORK")
        return True

    def get_modules(self, name: str) -> List[str]:
        fw = self._frameworks.get(name)
        return fw.modules if fw else []

    def add_module(self, framework_name: str, module_name: str) -> bool:
        fw = self._frameworks.get(framework_name)
        if not fw:
            return False
        if module_name not in fw.modules:
            fw.modules.append(module_name)
        return True

    def list_frameworks(self) -> str:
        if not self._frameworks:
            return "No hay frameworks registrados."
        lines = ["Frameworks en Calcifer:"]
        for name, fw in self._frameworks.items():
            emoji = "🟢" if fw.is_active() else "⚫"
            lines.append(emoji + " " + name + " v" + fw.version + " - " + fw.description)
            if fw.modules:
                lines.append("   Modulos: " + ", ".join(fw.modules))
        return "\n".join(lines)

    def remove(self, name: str) -> bool:
        """Elimina un framework del sistema."""
        if name not in self._frameworks:
            return False
        del self._frameworks[name]
        logger.info("Framework eliminado: " + name, "FRAMEWORK")
        return True


    def validate(self, name: str) -> tuple:
        """
        Valida un framework antes de ejecutar un módulo.
        Retorna (valid: bool, reason: str)
        """
        fw = self._frameworks.get(name)

        if not fw:
            return False, "framework_not_found"

        if not fw.is_active():
            return False, "framework_inactive"

        if not fw.modules:
            logger.warning("Framework sin módulos: " + name, "FRAMEWORK")
            # No bloquea — puede tener módulos registrados por nombre externo

        return True, "ok"

    def is_compatible(self, name: str, core_version: str) -> bool:
        """Verifica si el framework es compatible con la versión del Core."""
        fw = self._frameworks.get(name)
        if not fw:
            return False
        try:
            core_parts    = [int(x) for x in core_version.split(".")]
            min_parts     = [int(x) for x in fw.min_core.split(".")]
            return core_parts >= min_parts
        except Exception:
            return True

    def get_active_with_modules(self) -> list:
        """Retorna frameworks activos que tienen módulos."""
        return [f for f in self._frameworks.values()
                if f.is_active() and f.modules]

    def __contains__(self, name: str) -> bool:
        return name in self._frameworks


framework_manager = FrameworkManager()

framework_manager.register(FrameworkManifest(
    name="stripe", version="1.0.0",
    description="Pasarela Stripe — suscripciones y tarjetas",
    status="active", modules=["start"],
))
framework_manager.register(FrameworkManifest(
    name="paypal", version="0.0.0",
    description="Pasarela PayPal — pagos internacionales",
    status="inactive",
))
framework_manager.register(FrameworkManifest(
    name="shopify", version="0.0.0",
    description="Pasarela Shopify Payments",
    status="inactive",
))
framework_manager.register(FrameworkManifest(
    name="adyen", version="0.0.0",
    description="Pasarela Adyen — enterprise global",
    status="inactive",
))
framework_manager.register(FrameworkManifest(
    name="square", version="0.0.0",
    description="Pasarela Square — POS y e-commerce",
    status="inactive",
))
framework_manager.register(FrameworkManifest(
    name="moneris", version="0.0.0",
    description="Pasarela Moneris — Canada",
    status="inactive",
))
