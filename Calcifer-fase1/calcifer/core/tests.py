"""
🔥 Calcifer Core — Tests Completos
Autor: Calcifer Team | Versión: 1.1.0
Cobertura: unitaria + integración + flujo completo
Ejecutar: cd /root/calcifer && python3 core/tests.py
"""
import sys
sys.path.insert(0, "/root/calcifer")

passed = 0
failed = 0

def assert_eq(a, b):
    assert a == b, "Expected " + repr(b) + ", got " + repr(a)

def assert_true(v):
    assert v, "Expected True, got " + repr(v)

def assert_false(v):
    assert not v, "Expected False, got " + repr(v)

def assert_raises(fn, exc):
    try:
        fn()
        raise AssertionError("Expected " + exc.__name__ + " to be raised")
    except exc:
        pass

def test(name, fn):
    global passed, failed
    try:
        fn()
        print("  ✅ " + name)
        passed += 1
    except Exception as e:
        print("  ❌ " + name + " → " + str(e))
        failed += 1

print("\n🔥 CALCIFER CORE — TESTS COMPLETOS\n")

# ── FASE 11 — Exceptions ──────────────────────────────────────────────────────
print("📋 Exceptions")
from core.exceptions import (
    InvalidFormatError, InsufficientCreditsError, PermissionDeniedError,
    BrowserError, DatabaseError, ModuleNotFoundError, FrameworkNotFoundError,
    error_to_status, get_error_message, log_exception_to_audit, ERROR_CODES
)
test("ERR001 code",            lambda: assert_eq(InvalidFormatError().code, "ERR001"))
test("ERR003 code",            lambda: assert_eq(InsufficientCreditsError().code, "ERR003"))
test("ERR007 BrowserError",   lambda: assert_eq(BrowserError().code, "ERR007"))
test("ERR011 DatabaseError",   lambda: assert_eq(DatabaseError().code, "ERR011"))
test("ERR014 ModuleNotFound",  lambda: assert_eq(ModuleNotFoundError().code, "ERR014"))
test("ERR017 FrameworkNotF",   lambda: assert_eq(FrameworkNotFoundError().code, "ERR017"))
test("error_to_status",        lambda: assert_eq(error_to_status(InvalidFormatError()), "ERR001"))
test("get_error_message",      lambda: assert_eq(get_error_message("ERR001"), "Formato inválido"))
test("ERROR_CODES dict",       lambda: assert_true(len(ERROR_CODES) >= 15))
test("to_dict method",         lambda: assert_true("code" in InvalidFormatError().to_dict()))
test("log_exception no crash", lambda: log_exception_to_audit(InvalidFormatError()))

# ── FASE 5 — Contracts ────────────────────────────────────────────────────────
print("\n📋 Contracts")
from core.contracts import (
    ContractIn, ContractOut, ContractCardInfo, ContractLogData,
    validate_contract_in, validate_contract_out, CONTRACT_VERSION
)
cin = ContractIn.build(1, 123, "test", "Basic", 10, 40, "/sc", "4242|01|2028|111",
                       "stripe", "stripe", "1.0.0", "Start")
test("ContractIn build",           lambda: assert_eq(cin.command.trigger, "/sc"))
test("ContractIn params_list",     lambda: assert_eq(len(cin.command.params_list), 4))
test("ContractIn to_dict",         lambda: assert_true("user" in cin.to_dict()))
test("validate_contract_in OK",    lambda: assert_true(validate_contract_in(cin.to_dict())))
test("CONTRACT_VERSION exists",    lambda: assert_true(len(CONTRACT_VERSION) > 0))

cout_ok  = ContractOut.success("Start","stripe","Charged",64,ContractCardInfo("Visa","Debit","Classic"))
cout_dec = ContractOut.declined("Start","stripe","Declined",30,ContractCardInfo())
cout_3ds = ContractOut.pending_3ds("Start","stripe",20)
cout_err = ContractOut.error("Start","stripe","ERR001","Formato inválido")

test("CHARGED status",         lambda: assert_eq(cout_ok.status, "CHARGED"))
test("DECLINED status",        lambda: assert_eq(cout_dec.status, "DECLINED"))
test("PENDING_3DS status",     lambda: assert_eq(cout_3ds.status, "PENDING_3DS"))
test("ERR status",             lambda: assert_eq(cout_err.status, "ERR001"))
test("CHARGED deducts",        lambda: assert_true(cout_ok.should_deduct_credits()))
test("DECLINED deducts",       lambda: assert_true(cout_dec.should_deduct_credits()))
test("PENDING deducts",        lambda: assert_true(cout_3ds.should_deduct_credits()))
test("ERR no deducts",         lambda: assert_false(cout_err.should_deduct_credits()))
test("is_success",             lambda: assert_true(cout_ok.is_success()))
test("is_declined",            lambda: assert_true(cout_dec.is_declined()))
test("is_pending",             lambda: assert_true(cout_3ds.is_pending()))
test("is_error",               lambda: assert_true(cout_err.is_error()))
test("validate_contract_out",  lambda: assert_true(validate_contract_out(cout_ok.to_dict())))

# ── FASE 7 — Permissions ──────────────────────────────────────────────────────
print("\n📋 Permissions")
from core.permission_manager import permissions
test("Owner /sc",              lambda: assert_true(permissions.has_permission("Owner", "/sc")))
test("Seller /sc",             lambda: assert_true(permissions.has_permission("Seller", "/sc")))
test("Premium /sc",            lambda: assert_true(permissions.has_permission("Premium", "/sc")))
test("Basic /sc",              lambda: assert_true(permissions.has_permission("Basic", "/sc")))
test("Free /sc denied",        lambda: assert_false(permissions.has_permission("Free", "/sc")))
test("Free /sc denied",      lambda: assert_false(permissions.has_permission("Free", "/sc")))
test("Owner /addmembresia",    lambda: assert_true(permissions.has_permission("Owner", "/addmembresia")))
test("Basic /addmembresia NO", lambda: assert_false(permissions.has_permission("Basic", "/addmembresia")))
test("Owner is_admin",         lambda: assert_true(permissions.is_admin("Owner")))
test("Seller is_admin",        lambda: assert_true(permissions.is_admin("Seller")))
test("Basic not admin",        lambda: assert_false(permissions.is_admin("Basic")))
test("Owner level 100",        lambda: assert_eq(permissions.get_role_level("Owner"), 100))
test("Basic level 40",         lambda: assert_eq(permissions.get_role_level("Basic"), 40))
test("Free level 20",          lambda: assert_eq(permissions.get_role_level("Free"), 20))
test("Stripe perm Basic",      lambda: assert_true(permissions.has_framework_permission("Basic","stripe")))
test("Stripe perm Free NO",    lambda: assert_false(permissions.has_framework_permission("Free","stripe")))
test("Module perm start Basic",lambda: assert_true(permissions.has_module_permission("Basic","stripe")))
test("Invalid role → False",   lambda: assert_false(permissions.has_permission("Admin","/sc")))

# ── FASE 16 — Security ────────────────────────────────────────────────────────
print("\n📋 Security")
from core.security import security
from core.exceptions import InvalidFormatError as IFE, InvalidParameterError as IPE
test("validate card OK",       lambda: assert_eq(
    security.validate_card_format("4242424242424242|01|2028|111"),
    ("4242424242424242", "01", "2028", "111")))
test("invalid format raises",  lambda: assert_raises(lambda: security.validate_card_format("invalid"), IFE))
test("empty format raises",    lambda: assert_raises(lambda: security.validate_card_format(""), IFE))
test("mask_ccn",               lambda: assert_eq(security.mask_ccn("4242424242424242"), "424242xxxxxxxxxx"))
test("mask short ccn",         lambda: assert_eq(security.mask_ccn("123"), "****"))
test("sanitize text",          lambda: assert_eq(security.sanitize_text("hello\x00world"), "helloworld"))
test("sanitize max length",    lambda: assert_eq(len(security.sanitize_text("a"*600, 200)), 200))
test("valid credit 250",       lambda: assert_eq(security.validate_credits_amount(250), 250))
test("valid credit 500",       lambda: assert_eq(security.validate_credits_amount(500), 500))
test("invalid credit 100",     lambda: assert_raises(lambda: security.validate_credits_amount(100), Exception))
test("valid telegram_id",      lambda: assert_eq(security.validate_telegram_id(7469285894), 7469285894))
test("invalid telegram_id",    lambda: assert_raises(lambda: security.validate_telegram_id(-1), Exception))
test("validate_not_null OK",   lambda: assert_eq(security.validate_not_null("hello","field"), "hello"))
test("validate_not_null None", lambda: assert_raises(lambda: security.validate_not_null(None,"field"), IPE))
test("validate_not_null empty",lambda: assert_raises(lambda: security.validate_not_null("  ","field"), IPE))
test("validate_max_length OK", lambda: assert_eq(security.validate_max_length("hello","f",10), "hello"))
test("validate_max_length ERR",lambda: assert_raises(lambda: security.validate_max_length("hello","f",3), IPE))
test("validate_type OK",       lambda: assert_eq(security.validate_type(42, int,"f"), 42))
test("validate_type ERR",      lambda: assert_raises(lambda: security.validate_type("x", int,"f"), IPE))
test("validate_command OK",    lambda: assert_eq(security.validate_command("/sc"), "/sc"))
test("validate_command ERR",   lambda: assert_raises(lambda: security.validate_command("kt"), IPE))
test("sanitize_all returns 4", lambda: assert_eq(len(security.sanitize_all(123,"user","/sc","params")), 4))

# ── FASE 12 — Response Builder ────────────────────────────────────────────────
print("\n📋 Response Builder")
from core.response_builder import response_builder
test("error_format has /sc",   lambda: assert_true("/sc" in response_builder.error_format()))
test("error_credits has 0",    lambda: assert_true("0" in response_builder.error_credits(0)))
test("error_maintenance",      lambda: assert_true("mantenimiento" in response_builder.error_maintenance("Start")))
test("error_timeout",          lambda: assert_true("Timeout" in response_builder.error_timeout("Start")))
test("error_permission",       lambda: assert_true("permisos" in response_builder.error_permission("Basic").lower()))
test("error_internal",         lambda: assert_true("ERR005" in response_builder.error_internal("Start","ERR005")))
test("error_blocked empty",    lambda: assert_eq(response_builder.error_blocked(), ""))
test("processing msg",         lambda: assert_true("Start" in response_builder.processing("Start")))
test("charged has CHARGED",    lambda: assert_true("#CHARGED" in response_builder.charged(
    "Start","Debit","Classic","Visa","BBVA","Colombia","🇨🇴",64,10,"MacClaren13")))
test("declined has DECLINED",  lambda: assert_true("#DECLINED" in response_builder.declined(
    "Declined","Start","Debit","Classic","Visa","BBVA","Colombia","🇨🇴",30,9,"MacClaren13")))
test("from_contract_out CHRG", lambda: assert_true("#CHARGED" in response_builder.from_contract_out(
    cout_ok.to_dict(), 9, "MacClaren13")))
test("from_contract_out ERR",  lambda: assert_true("/sc" in response_builder.from_contract_out(
    cout_err.to_dict(), 10, "MacClaren13")))

# ── FASE 13 — Framework Manager ───────────────────────────────────────────────
print("\n📋 Framework Manager")
from core.framework_manager import framework_manager, FrameworkManifest
test("stripe registered",      lambda: assert_true("stripe" in framework_manager))
test("stripe active",          lambda: assert_true(framework_manager.get("stripe").is_active()))
test("paypal inactive",        lambda: assert_false(framework_manager.get("paypal").is_active()))
test("get None for unknown",   lambda: assert_true(framework_manager.get("unknown") is None))
test("validate stripe OK",     lambda: assert_eq(framework_manager.validate("stripe"), (True, "ok")))
test("validate unknown",       lambda: assert_eq(framework_manager.validate("noexiste")[0], False))
test("validate inactive",      lambda: assert_eq(framework_manager.validate("paypal")[0], False))
test("remove test fw",         lambda: (
    framework_manager.register(FrameworkManifest("test_fw","1.0","test","inactive",[])),
    assert_true(framework_manager.remove("test_fw"))
))
test("removed not in fw",      lambda: assert_true(framework_manager.get("test_fw") is None))
test("activate/deactivate",    lambda: (
    framework_manager.register(FrameworkManifest("temp_fw","1.0","temp","inactive",[])),
    framework_manager.activate("temp_fw"),
    assert_true(framework_manager.get("temp_fw").is_active()),
    framework_manager.deactivate("temp_fw"),
    assert_false(framework_manager.get("temp_fw").is_active()),
    framework_manager.remove("temp_fw")
))

# ── FASE 20 — Version ─────────────────────────────────────────────────────────
print("\n📋 Version")
from core.version import VERSION, is_compatible, get_migration_notes, get_version_string
test("is_compatible 1.0.0",    lambda: assert_true(is_compatible("1.0.0")))
test("is_compatible 1.1.0",    lambda: assert_true(is_compatible("1.1.0")))
test("NOT compatible 9.0.0",   lambda: assert_false(is_compatible("9.0.0")))
test("version_string has v",   lambda: assert_true("v" in get_version_string()))
test("migration notes list",   lambda: assert_true(isinstance(get_migration_notes("1.0.0"), list)))

# ── FASE 14 — Event Bus ───────────────────────────────────────────────────────
print("\n📋 Event Bus")
from core.event_bus import event_bus, EVENT_MODULE_STARTED, EVENT_MODULE_FINISHED, EVENT_CREDITS_CONSUMED
results = []
event_bus.subscribe(EVENT_MODULE_STARTED,  lambda d: results.append(("started", d)))
event_bus.subscribe(EVENT_MODULE_FINISHED, lambda d: results.append(("finished", d)))
event_bus.subscribe(EVENT_CREDITS_CONSUMED,lambda d: results.append(("credits", d)))
event_bus.emit_module_started("stripe","stripe","MacClaren13")
event_bus.emit_module_finished("stripe","stripe","CHARGED",64)
event_bus.emit_credits_consumed(7469285894, 1, 271)
test("module_started received",  lambda: assert_eq(results[0][0], "started"))
test("module_finished received", lambda: assert_eq(results[1][0], "finished"))
test("credits_consumed received",lambda: assert_eq(results[2][0], "credits"))
test("started data correct",     lambda: assert_eq(results[0][1]["module"], "stripe"))
test("finished status correct",  lambda: assert_eq(results[1][1]["status"], "CHARGED"))
test("credits data correct",     lambda: assert_eq(results[2][1]["amount"], 1))

# ── FASE 2 — Registry ─────────────────────────────────────────────────────────
print("\n📋 Registry")
from core.registry import registry, ModuleManifest
test("core.bot registered",     lambda: assert_true("core.bot" in registry))
test("discover /tmp no crash",  lambda: assert_true(isinstance(registry.discover("/tmp/no_existe"), int)))
test("get_by_command /sc",      lambda: assert_true(registry.get_by_command("/sc") is not None))
test("detect_invalid_modules",  lambda: assert_true(isinstance(registry.detect_invalid_modules(), list)))
test("detect fw modules",       lambda: assert_true(isinstance(registry.detect_framework_modules("stripe"), list)))
test("validate_and_register OK",lambda: assert_true(registry.validate_and_register(
    ModuleManifest("test.mod","1.0.0","Author","desc","inactive",[],[]))[0]))
# Limpiar módulo de test
registry._modules.pop("test.mod", None)

# ── FASE 3 — Module Manager ───────────────────────────────────────────────────
print("\n📋 Module Manager")
from core.module_manager import module_manager, ModuleState
summary = module_manager.get_summary()
test("summary has total",       lambda: assert_true("total" in summary))
test("summary total > 0",       lambda: assert_true(summary["total"] > 0))
test("summary has active",      lambda: assert_true("active" in summary))
test("get_timeout default",     lambda: assert_eq(module_manager.get_timeout("unknown"), 120))
test("set_timeout custom",      lambda: (
    module_manager.set_timeout("stripe", 90),
    assert_eq(module_manager.get_timeout("stripe"), 90)
))
test("enable/disable cycle",    lambda: (
    module_manager.disable("gateway.stripe.start"),
    assert_eq(module_manager.get_state("gateway.stripe.start"), ModuleState.INACTIVE),
    module_manager.enable("gateway.stripe.start"),
    assert_eq(module_manager.get_state("gateway.stripe.start"), ModuleState.ACTIVE)
))
test("set_error state",         lambda: (
    module_manager.set_error("gateway.stripe"),
    assert_eq(module_manager.get_state("gateway.stripe"), ModuleState.ERROR),
    module_manager.enable("gateway.stripe")
))

# ── INTEGRACIÓN — Flujo completo simulado ─────────────────────────────────────
print("\n📋 Integración — Flujo completo")

def simulate_flow(membership, command, raw_params):
    """Simula el flujo completo del Dispatcher sin BD ni Browser."""
    try:
        # 1. Security
        tid, uname, cmd, params = security.sanitize_all(
            7469285894, "MacClaren13", command, raw_params
        )
        # 2. Permissions
        has_perm = permissions.has_permission(membership, cmd)
        if not has_perm:
            return "ERR004"
        # 3. Framework
        fw_map = {"/sc": "stripe"}
        fw_name = fw_map.get(cmd, "")
        fw_valid, fw_reason = framework_manager.validate(fw_name)
        if not fw_valid:
            return "ERR_FW"
        # 4. Registry
        mod = registry.get_by_command(cmd)
        if not mod:
            return "ERR014"
        # 5. ContractIn
        cin = ContractIn.build(1, tid, uname, membership, 10, 40,
                               cmd, params, "stripe","stripe","1.0.0","Start")
        # 6. Validate contract
        security.validate_contract_structure(cin)
        # 7. Simular ContractOut
        cout = ContractOut.error("Start","stripe","ERR005","Simulado")
        # 8. ResponseBuilder
        resp = response_builder.from_contract_out(cout.to_dict(), 10, uname)
        return "OK_" + cout.status
    except Exception as e:
        return "EXCEPTION_" + str(e)[:30]

test("Owner /sc full flow",     lambda: assert_true(simulate_flow("Owner","/sc","4242|01|2028|111").startswith("OK_")))
test("Basic /sc full flow",     lambda: assert_true(simulate_flow("Basic","/sc","4242|01|2028|111").startswith("OK_")))
test("Free /sc → ERR004",       lambda: assert_eq(simulate_flow("Free","/sc","4242|01|2028|111"), "ERR004"))
test("invalid cmd → exception", lambda: assert_true(simulate_flow("Owner","notacmd","x").startswith("EXCEPTION")))


# ── FASE 15 — Validación Final del Core ──────────────────────────────────────
print("\n📋 Validación Final — Core 100% consolidado")
from core.logger import logger
from core import __version__

test("version en __init__",        lambda: assert_true(len(__version__) > 0))
test("flujo documentado",          lambda: assert_true("Dispatcher" in open("/root/calcifer/core/__init__.py").read()))
test("finally en dispatcher",      lambda: assert_true("finally" in open("/root/calcifer/core/dispatcher.py").read()))
test("critical en logger",         lambda: assert_true(hasattr(logger, "critical")))

from core.event_bus import (
    EVENT_FRAMEWORK_DISABLED, EVENT_USER_AUTHENTICATED, EVENT_MODULE_LOADED
)
test("framework_disabled event",   lambda: assert_true(len(EVENT_FRAMEWORK_DISABLED) > 0))
test("user_authenticated event",   lambda: assert_true(len(EVENT_USER_AUTHENTICATED) > 0))
test("module_loaded event",        lambda: assert_true(len(EVENT_MODULE_LOADED) > 0))

fw_results = []
event_bus.subscribe(EVENT_USER_AUTHENTICATED, lambda d: fw_results.append(d))
event_bus.subscribe(EVENT_FRAMEWORK_DISABLED, lambda d: fw_results.append(d))
event_bus.emit_user_authenticated(7469285894, "MacClaren13", "Owner")
event_bus.emit_framework_disabled("paypal")
test("user_auth event fired",      lambda: assert_eq(fw_results[0]["username"], "MacClaren13"))
test("fw_disabled event fired",    lambda: assert_eq(fw_results[1]["framework"], "paypal"))

from core.core_status import core_status
status = core_status.get()
test("status has maintenance fw",  lambda: assert_true("frameworks_maintenance" in status))
test("maintenance count >= 0",     lambda: assert_true(status["frameworks_maintenance"] >= 0))
test("status has errors",          lambda: assert_true("errors" in status))

# Verificar cadena de error completa F8
test("error chain: Exception→code", lambda: assert_eq(error_to_status(InvalidFormatError()), "ERR001"))
test("error chain: code→response",  lambda: assert_true("/sc" in response_builder._error_response("ERR001","Start",0)
    if hasattr(response_builder, "_error_response") else
    "/sc" in response_builder.error_format()))

# Verificar flujo completo final
test("flujo completo Owner",       lambda: assert_true(simulate_flow("Owner","/sc","4242|01|2028|111").startswith("OK_")))
test("flujo completo Premium",     lambda: assert_true(simulate_flow("Premium","/sc","4242|01|2028|111").startswith("OK_")))
test("flujo deniega Free",         lambda: assert_eq(simulate_flow("Free","/sc","4242|01|2028|111"), "ERR004"))
test("logger critical no crash",   lambda: logger.critical("test critical", "TEST"))

# ── RESULTADO FINAL ───────────────────────────────────────────────────────────
print("\n" + "━"*55)
print("✅ Pasaron: " + str(passed) + "   ❌ Fallaron: " + str(failed))
if failed == 0:
    print("🔥 TODOS LOS TESTS PASARON — Core 100% consolidado")
else:
    print("⚠️  Algunos tests fallaron — revisar arriba")
