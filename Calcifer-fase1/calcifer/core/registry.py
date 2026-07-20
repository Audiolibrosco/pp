"""
🔥 Calcifer Core — Module Registry
Autor: Calcifer Team | Versión: 1.1.0
Catálogo central con descubrimiento automático, validación de metadata
y compatibilidad de versiones.
"""
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from core.logger import logger
from core.version import VERSION


CORE_VERSION = VERSION


@dataclass
class ModuleManifest:
    name        : str
    version     : str
    author      : str
    description : str
    status      : str
    commands    : List[str]
    permissions : List[str]
    dependencies: List[str] = field(default_factory=list)
    framework   : str = ""
    min_core    : str = "1.0.0"

    def is_active(self) -> bool:
        return self.status == "active"

    def to_dict(self) -> dict:
        return {
            "name": self.name, "version": self.version,
            "author": self.author, "description": self.description,
            "status": self.status, "commands": self.commands,
            "permissions": self.permissions, "dependencies": self.dependencies,
            "framework": self.framework, "min_core": self.min_core,
        }

    @classmethod
    def from_metadata(cls, data: dict) -> "ModuleManifest":
        """Crea un ModuleManifest desde un metadata.json."""
        return cls(
            name        = data.get("name", ""),
            version     = data.get("version", "0.0.0"),
            author      = data.get("author", ""),
            description = data.get("description", ""),
            status      = data.get("status", "inactive"),
            commands    = data.get("commands", []),
            permissions = data.get("permissions", []),
            dependencies= data.get("dependencies", []),
            framework   = data.get("framework", ""),
            min_core    = data.get("min_core", "1.0.0"),
        )


class ModuleRegistry:
    """Registro central de módulos con descubrimiento y validación automática."""

    REQUIRED_METADATA_FIELDS = [
        "name", "version", "author", "description",
        "status", "commands", "permissions"
    ]

    def __init__(self):
        self._modules: Dict[str, ModuleManifest] = {}

    def register(self, manifest: ModuleManifest) -> bool:
        if manifest.name in self._modules:
            logger.info(f"Registry: módulo '{manifest.name}' actualizado", "REGISTRY")
        self._modules[manifest.name] = manifest
        logger.info(f"Registry: ✅ '{manifest.name}' v{manifest.version} — {manifest.status}", "REGISTRY")
        return True

    def discover(self, modules_path: str = "/root/calcifer/modules") -> int:
        """
        Descubrimiento automático de módulos.
        Busca metadata.json en modules/{framework}/{module}/metadata.json
        """
        discovered = 0
        if not os.path.exists(modules_path):
            logger.warning(f"Ruta de módulos no existe: {modules_path}", "REGISTRY")
            return 0

        for framework in os.listdir(modules_path):
            fw_path = os.path.join(modules_path, framework)
            if not os.path.isdir(fw_path):
                continue
            for module in os.listdir(fw_path):
                mod_path  = os.path.join(fw_path, module)
                meta_path = os.path.join(mod_path, "metadata.json")
                if os.path.isfile(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if self._validate_metadata(data):
                            manifest = ModuleManifest.from_metadata(data)
                            self.register(manifest)
                            discovered += 1
                        else:
                            logger.warning(f"metadata.json inválido: {meta_path}", "REGISTRY")
                    except Exception as e:
                        logger.error(f"Error leyendo {meta_path}: {e}", "REGISTRY")

        logger.info(f"Descubrimiento: {discovered} módulos encontrados", "REGISTRY")
        return discovered

    def _validate_metadata(self, data: dict) -> bool:
        """Valida que el metadata.json tenga todos los campos requeridos."""
        missing = [f for f in self.REQUIRED_METADATA_FIELDS if f not in data]
        if missing:
            logger.warning(f"Metadata incompleto, faltan: {missing}", "REGISTRY")
            return False
        return True

    def check_compatibility(self, manifest: ModuleManifest) -> bool:
        """Verifica que el módulo sea compatible con la versión del Core."""
        try:
            core_parts   = [int(x) for x in CORE_VERSION.split(".")]
            min_parts    = [int(x) for x in manifest.min_core.split(".")]
            if core_parts >= min_parts:
                return True
            logger.warning(
                f"Módulo '{manifest.name}' requiere Core >= {manifest.min_core}, "
                f"actual: {CORE_VERSION}", "REGISTRY"
            )
            return False
        except Exception:
            return True


    def validate_and_register(self, manifest: "ModuleManifest") -> tuple:
        """
        Valida completamente un módulo antes de registrarlo.
        Retorna (success: bool, reason: str)
        """
        # Verificar campos requeridos
        if not manifest.name:
            return False, "name vacío"
        if not manifest.version:
            return False, "version vacía"
        if not manifest.author:
            return False, "author vacío"

        # Verificar compatibilidad de versión
        if not self.check_compatibility(manifest):
            manifest.status = "inactive"
            logger.warning(
                "Módulo '" + manifest.name + "' deshabilitado: Core incompatible",
                "REGISTRY"
            )
            self.register(manifest)
            return False, "version_incompatible"

        self.register(manifest)
        return True, "ok"

    def detect_invalid_modules(self) -> list:
        """Detecta y deshabilita automáticamente módulos inválidos."""
        invalid = []
        for name, manifest in self._modules.items():
            reasons = []

            # Metadata incompleta
            if not manifest.author:
                reasons.append("author faltante")
            if not manifest.version or manifest.version == "":
                reasons.append("version faltante")

            # Versión incompatible
            if not self.check_compatibility(manifest):
                reasons.append("version_incompatible")

            if reasons:
                manifest.status = "inactive"
                logger.warning(
                    "Módulo inválido deshabilitado: " + name + " — " + ", ".join(reasons),
                    "REGISTRY"
                )
                invalid.append({"name": name, "reasons": reasons})

        return invalid

    def detect_framework_modules(self, framework: str) -> list:
        """Retorna módulos de un framework específico."""
        return [m for m in self._modules.values() if m.framework == framework]

    def get(self, name: str) -> Optional[ModuleManifest]:
        return self._modules.get(name)

    def get_all(self) -> Dict[str, ModuleManifest]:
        return self._modules.copy()

    def get_active(self) -> List[ModuleManifest]:
        return [m for m in self._modules.values() if m.is_active()]

    def get_by_command(self, command: str) -> Optional[ModuleManifest]:
        for m in self._modules.values():
            if command in m.commands:
                return m
        return None

    def get_by_framework(self, framework: str) -> List[ModuleManifest]:
        return [m for m in self._modules.values() if m.framework == framework]

    def set_status(self, name: str, status: str) -> bool:
        if name not in self._modules:
            return False
        self._modules[name].status = status
        logger.info(f"Registry: '{name}' → {status}", "REGISTRY")
        return True

    def list_modules(self) -> str:
        if not self._modules:
            return "No hay módulos registrados."
        lines = ["📦 *Módulos en Calcifer:*\n"]
        for name, m in self._modules.items():
            emoji = "🟢" if m.is_active() else "🔴" if m.status == "maintenance" else "⚫"
            lines.append(f"{emoji} `{name}` v{m.version} — {m.description}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._modules)

    def __contains__(self, name: str) -> bool:
        return name in self._modules


registry = ModuleRegistry()

# ── Módulos registrados ───────────────────────────────────────────────────────
registry.register(ModuleManifest(
    name="core.bot", version="1.0.0", author="Calcifer Team",
    description="Bot principal de Telegram", status="active",
    commands=["/start","/register","/perfil","/addmembresia","/deluser",
              "/blockuser","/unblockuser","/verificar","/historial",
              "/pasarelas","/estado","/ayuda",],
    permissions=["Owner","Seller","Premium","Basic","Free"],
))
registry.register(ModuleManifest(
    name="core.database", version="1.0.0", author="Calcifer Team",
    description="Conexión y operaciones MySQL", status="active",
    commands=[], permissions=["Owner","Seller","Premium","Basic","Free"],
))
