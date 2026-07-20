"""
🔥 Calcifer Core — Core Status
Autor: Calcifer Team | Versión: 1.0.0
Estado completo del sistema en tiempo real.
"""
import os
import time
from datetime import datetime

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from core.version import VERSION, PHASE


START_TIME = time.time()


class CoreStatus:

    def get(self) -> dict:
        from core.registry          import registry
        from core.framework_manager import framework_manager

        uptime_sec = int(time.time() - START_TIME)
        uptime_str = self._format_uptime(uptime_sec)

        mem_mb = 0.0
        if HAS_PSUTIL:
            try:
                proc   = psutil.Process(os.getpid())
                mem_mb = round(proc.memory_info().rss / 1024 / 1024, 2)
            except Exception:
                pass

        active_modules    = [m.name for m in registry.get_active()]
        active_frameworks = [f.name for f in framework_manager.get_active()]

        return {
            "version"           : VERSION,
            "phase"             : PHASE,
            "status"            : "running",
            "uptime"            : uptime_str,
            "uptime_seconds"    : uptime_sec,
            "memory_mb"         : mem_mb,
            "active_modules"    : active_modules,
            "active_frameworks" : active_frameworks,
            "total_modules"     : len(registry.get_all()),
            "total_frameworks"  : len(framework_manager.get_all()),
            "timestamp"         : datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "errors"            : self._count_error_modules(),
            "frameworks_maintenance": self._count_maintenance_frameworks(),
        }

    def _count_maintenance_frameworks(self) -> int:
        """Cuenta frameworks en estado inactive/mantenimiento."""
        try:
            from core.framework_manager import framework_manager
            return sum(1 for f in framework_manager.get_all().values() if not f.is_active())
        except Exception:
            return 0

    def _count_error_modules(self) -> int:
        """Cuenta módulos en estado de error."""
        try:
            from core.registry import registry
            return sum(1 for m in registry.get_all().values() if m.status == "error")
        except Exception:
            return 0

    def _format_uptime(self, seconds: int) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return str(h) + "h " + str(m) + "m " + str(s) + "s"

    def format_message(self) -> str:
        s          = self.get()
        modules    = ", ".join(s["active_modules"])    or "ninguno"
        frameworks = ", ".join(s["active_frameworks"]) or "ninguno"
        msg = (
            "🔥 Calcifer Core Status\n\n"
            "Version    : " + s["version"] + " (Phase " + s["phase"] + ")\n"
            "Estado     : ✅ running\n"
            "Uptime     : " + s["uptime"] + "\n"
            "Memoria    : " + str(s["memory_mb"]) + " MB\n\n"
            "Modulos activos    : " + modules + "\n"
            "Frameworks activos : " + frameworks + "\n"
            "Total modulos      : " + str(s["total_modules"]) + "\n"
        )
        return msg


core_status = CoreStatus()
