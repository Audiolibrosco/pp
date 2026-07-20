"""
🔥 Calcifer Core — Dispatcher
Autor: Calcifer Team | Versión: 1.0.0
Punto único de entrada para todos los comandos de Calcifer.

Flujo completo:
  Telegram → Dispatcher → Validar → Permisos → Créditos →
  ContractIn → Módulo → ContractOut → Audit → Créditos → Respuesta → Telegram
"""
import time
from typing import Optional
from core.contracts        import ContractIn, ContractOut
from core.credits          import credits_manager
from core.permission_manager import permissions
from core.registry         import registry
from core.framework_manager import framework_manager
from core.response_builder import response_builder
from core.audit_manager    import audit_manager
from core.logger           import logger
from core.security         import security
from core.event_bus        import event_bus
from core.exceptions       import (
    CalciferError, InvalidFormatError, InsufficientCreditsError,
    PermissionDeniedError, UserBlockedError, ModuleNotFoundError,
    ModuleNotActiveError, FrameworkInactiveError, error_to_status
)
from core.version import VERSION


# Mapa de comando → (framework, module_name, visible_name, min_role)
COMMAND_MAP = {
}


class Dispatcher:
    """
    Punto único de entrada para todos los comandos de Calcifer.
    El bot solo necesita llamar dispatch() con los datos del mensaje.
    """

    async def dispatch(
        self,
        telegram_id : int,
        username    : str,
        membership  : str,
        user_id     : int,
        command     : str,
        raw_params  : str,
    ) -> str:
        """
        Procesa un comando completo y retorna el mensaje para Telegram.

        Siempre retorna un string — nunca lanza excepciones al bot.
        """
        start_time     = time.time()
        credits_before = 0
        credits_after  = 0
        status         = "ERR005"
        error_code     = None
        framework_name = ""
        module_name    = ""
        visible_name   = ""

        try:
            # ── 1. Sanitizar entradas (punto único) ──────────────────────────
            telegram_id, username, command, raw_params = security.sanitize_all(
                telegram_id, username, command, raw_params
            )

            # ── 2. Verificar si está bloqueado ────────────────────────────────
            if membership == "Blocked":
                raise UserBlockedError()

            # ── 3. Identificar el módulo para este comando ────────────────────
            if command not in COMMAND_MAP:
                raise ModuleNotFoundError(f"Comando desconocido: {command}")

            framework_name, module_name, visible_name, min_role = COMMAND_MAP[command]

            # ── 4. Validar permisos ───────────────────────────────────────────
            if not permissions.has_permission(membership, command):
                raise PermissionDeniedError(
                    f"Rol {membership} no puede usar {command}"
                )

            # ── 5. Verificar framework activo ─────────────────────────────────
            fw = framework_manager.get(framework_name)
            if not fw or not fw.is_active():
                raise FrameworkInactiveError(f"Framework {framework_name} inactivo")

            # ── 6. Verificar módulo activo ────────────────────────────────────
            module_manifest = registry.get(f"gateway.{framework_name}.{module_name}")
            if not module_manifest:
                raise ModuleNotFoundError(f"Módulo {module_name} no encontrado")
            if not module_manifest.is_active():
                raise ModuleNotActiveError(f"{visible_name} en mantenimiento")

            # ── 7. Consultar créditos ─────────────────────────────────────────
            credits_before = credits_manager.get(telegram_id)
            credits_manager.validate(telegram_id)

            # ── 8. Construir ContractIn ───────────────────────────────────────
            role_level = permissions.get_role_level(membership)
            contract_in = ContractIn.build(
                user_id      = user_id,
                telegram_id  = telegram_id,
                username     = username,
                membership   = membership,
                credits      = credits_before,
                role_level   = role_level,
                trigger      = command,
                raw_params   = raw_params,
                module_name  = module_name,
                framework    = framework_name,
                version      = VERSION,
                visible_name = visible_name,
            )

            # ── 9. Emitir evento de inicio ────────────────────────────────────
            event_bus.emit_module_started(module_name, framework_name, username)
            logger.module(module_name, framework_name, "STARTED", f"user=@{username}")

            # ── 10. Ejecutar el módulo ────────────────────────────────────────
            contract_out = await self._run_module(framework_name, module_name, contract_in)
            status       = contract_out.status

            # ── 11. Descontar créditos si corresponde ─────────────────────────
            if contract_out.should_deduct_credits():
                credits_after = credits_manager.deduct(telegram_id)
                event_bus.emit_credits_consumed(telegram_id, 1, credits_after)
            else:
                credits_after = credits_before

            # ── 12. Emitir evento de fin ──────────────────────────────────────
            execution_time = int(time.time() - start_time)
            event_bus.emit_module_finished(module_name, framework_name, status, execution_time)
            logger.module(module_name, framework_name, "FINISHED",
                          f"status={status} time={execution_time}s")

            # ── 13. Registrar en audit ────────────────────────────────────────
            audit_manager.log(
                telegram_id    = telegram_id,
                username       = username,
                command        = command,
                framework      = framework_name,
                module         = module_name,
                status         = status,
                execution_time = execution_time,
                credits_before = credits_before if credits_before != -1 else -1,
                credits_after  = credits_after  if credits_after  != -1 else -1,
                response       = contract_out.response,
                error_code     = contract_out.error_code,
            )

            # ── 14. Construir respuesta ───────────────────────────────────────
            return response_builder.from_contract_out(
                contract_out.to_dict(), credits_after, username
            )

        except UserBlockedError:
            return ""   # Sin respuesta para usuarios bloqueados

        except CalciferError as e:
            status     = error_to_status(e)
            error_code = status
            execution_time = int(time.time() - start_time)
            event_bus.emit_module_error(module_name or command, status)
            logger.error(f"CalciferError: {e.message} ({status})", "DISPATCHER")

            # Audit del error
            if module_name:
                audit_manager.log(
                    telegram_id=telegram_id, username=username,
                    command=command, framework=framework_name, module=module_name,
                    status=status, execution_time=execution_time,
                    credits_before=credits_before, credits_after=credits_before,
                    response=e.message, error_code=status,
                )

            return self._error_response(status, visible_name or command, credits_before)

        except Exception as e:
            logger.error(f"Error inesperado en Dispatcher: {e}", "DISPATCHER")
            return response_builder.error_internal(visible_name or command, "ERR005")

        finally:
            # ── Liberación de recursos ────────────────────────────────────────
            # Garantiza que el logger siempre registre el fin de la ejecución
            # independientemente de si hubo éxito o error
            try:
                elapsed = int(time.time() - start_time)
                logger.info(
                    f"Ejecución finalizada: cmd={command} status={status} "
                    f"time={elapsed}s user=@{username}",
                    "DISPATCHER"
                )
            except Exception:
                pass

    async def _run_module(self, framework: str, module: str, contract_in: ContractIn) -> ContractOut:
        """Carga y ejecuta el módulo dinámicamente."""
        try:
            import importlib
            mod = importlib.import_module(f"modules.{framework}.{module}.{module}")
            return await mod.run(contract_in)
        except ImportError as e:
            logger.error(f"No se pudo cargar módulo {framework}.{module}: {e}", "DISPATCHER")
            from core.contracts import ContractOut
            return ContractOut.error(
                gateway    = module,
                module     = module,
                error_code = "ERR014",
                response   = f"Módulo {module} no encontrado",
            )
        except Exception as e:
            logger.error(f"Error ejecutando módulo {module}: {e}", "DISPATCHER")
            from core.contracts import ContractOut
            return ContractOut.error(
                gateway    = module,
                module     = module,
                error_code = "ERR005",
                response   = str(e),
            )

    def _error_response(self, status: str, name: str, credits: int) -> str:
        """Genera la respuesta de error correcta según el código."""
        if status == "ERR001":
            return response_builder.error_format()
        elif status == "ERR003":
            return response_builder.error_credits(credits)
        elif status == "ERR004":
            return response_builder.error_permission("")
        elif status == "ERR006":
            return response_builder.error_timeout(name)
        elif status == "ERR010":
            return response_builder.error_maintenance(name)
        else:
            return response_builder.error_internal(name, status)


dispatcher = Dispatcher()
