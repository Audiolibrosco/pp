"""
🔥 Calcifer Core — Response Builder
Autor: Calcifer Team | Versión: 1.0.0
Genera respuestas uniformes para todos los módulos.
"""
from typing import Optional


class ResponseBuilder:
    """Construye mensajes de Telegram estandarizados para todos los módulos."""

    # ── Respuestas de resultado ───────────────────────────────────────────────

    @staticmethod
    def charged(gateway, card_type, card_level, card_brand,
                bank, country, flag, execution_time, credits, username) -> str:
        info = " • ".join(filter(None, [card_type, card_level, card_brand]))
        lines = [
            "Card :",
            "",
            "Status :",
            "#CHARGED ✅",
            "",
            "Response :",
            "Charged",
            "",
            "Information :",
            info or "N/A",
            "",
            "Bank :",
            bank or "N/A",
            "",
            "Country :",
            f"{country or 'N/A'} {flag or ''}".strip(),
            "",
            "Gate :",
            gateway,
            "",
            "Took :",
            f"{execution_time} s",
            "",
            "Credits :",
            str(credits) if credits != -1 else "∞",
            "",
            "User :",
            f"@{username}",
        ]
        return "\n".join(lines)

    @staticmethod
    def declined(response, gateway, card_type, card_level, card_brand,
                 bank, country, flag, execution_time, credits, username) -> str:
        info = " • ".join(filter(None, [card_type, card_level, card_brand]))
        lines = [
            "Card :",
            "",
            "Status :",
            "#DECLINED ❌",
            "",
            "Response :",
            response,
            "",
            "Information :",
            info or "N/A",
            "",
            "Bank :",
            bank or "N/A",
            "",
            "Country :",
            f"{country or 'N/A'} {flag or ''}".strip(),
            "",
            "Gate :",
            gateway,
            "",
            "Took :",
            f"{execution_time} s",
            "",
            "Credits :",
            str(credits) if credits != -1 else "∞",
            "",
            "User :",
            f"@{username}",
        ]
        return "\n".join(lines)

    @staticmethod
    def pending_3ds(gateway, execution_time, credits, username) -> str:
        lines = [
            "Card :",
            "",
            "Status :",
            "#PENDING_3DS ⏳",
            "",
            "Response :",
            "3D Secure Required",
            "",
            "Gate :",
            gateway,
            "",
            "Took :",
            f"{execution_time} s",
            "",
            "Credits :",
            str(credits) if credits != -1 else "∞",
            "",
            "User :",
            f"@{username}",
        ]
        return "\n".join(lines)

    # ── Respuestas de error ───────────────────────────────────────────────────

    @staticmethod
    def error_format() -> str:
        return "❌ Formato inválido.\n\nUso correcto: /sc CCN|MM|AAAA|CVV"

    @staticmethod
    def error_credits(current: int) -> str:
        return f"❌ Créditos insuficientes.\n\nCréditos actuales: {current}"

    @staticmethod
    def error_permission(role: str) -> str:
        return f"❌ Sin permisos.\n\nTu rol actual ({role}) no puede usar este comando."

    @staticmethod
    def error_timeout(gateway: str) -> str:
        return f"⏱️ Timeout en {gateway}.\n\nEl proceso tardó demasiado. Intenta nuevamente."

    @staticmethod
    def error_maintenance(module: str) -> str:
        return f"🔧 {module} está en mantenimiento.\n\nIntenta más tarde."

    @staticmethod
    def error_internal(gateway: str, code: str) -> str:
        return f"⚠️ Error en {gateway}\nCódigo: {code}\n\nIntenta nuevamente más tarde."

    @staticmethod
    def error_blocked() -> str:
        return ""

    # ── Respuestas de sistema ─────────────────────────────────────────────────

    @staticmethod
    def processing(module: str) -> str:
        return f"⏳ Procesando en {module}..."

    @staticmethod
    def system_ok(detail: str = "") -> str:
        return ("✅ Sistema operativo.\n" + detail).strip()

    @staticmethod
    def system_error(detail: str = "") -> str:
        return ("⚠️ Error del sistema.\n" + detail).strip()

    # ── Constructor desde contract_out ────────────────────────────────────────

    @classmethod
    def from_contract_out(cls, contract_out: dict, credits_after: int, username: str) -> str:
        """Construye la respuesta automáticamente desde un contract_out."""
        status = contract_out.get("status", "ERR005")
        gw     = contract_out.get("gateway", "Gateway")
        card   = contract_out.get("card", {})
        time_  = contract_out.get("execution_time", 0)

        if status == "CHARGED":
            return cls.charged(
                gateway        = gw,
                card_type      = card.get("type"),
                card_level     = card.get("level"),
                card_brand     = card.get("brand"),
                bank           = contract_out.get("bank"),
                country        = contract_out.get("country"),
                flag           = contract_out.get("country_flag"),
                execution_time = time_,
                credits        = credits_after,
                username       = username,
            )
        elif status == "DECLINED":
            return cls.declined(
                response       = contract_out.get("response", "Declined"),
                gateway        = gw,
                card_type      = card.get("type"),
                card_level     = card.get("level"),
                card_brand     = card.get("brand"),
                bank           = contract_out.get("bank"),
                country        = contract_out.get("country"),
                flag           = contract_out.get("country_flag"),
                execution_time = time_,
                credits        = credits_after,
                username       = username,
            )
        elif status == "PENDING_3DS":
            return cls.pending_3ds(gw, time_, credits_after, username)
        elif status == "ERR001":
            return cls.error_format()
        elif status == "ERR003":
            return cls.error_credits(credits_after)
        elif status == "ERR004":
            return cls.error_permission("")
        elif status == "ERR006":
            return cls.error_timeout(gw)
        elif status == "ERR010":
            return cls.error_maintenance(gw)
        else:
            return cls.error_internal(gw, status)


response_builder = ResponseBuilder()
