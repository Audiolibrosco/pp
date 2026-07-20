"""
🔥 Calcifer Core — Security
Autor: Calcifer Team | Versión: 1.0.0
Validación, sanitización y protección de entradas.
"""
import re
from typing import Optional
from core.exceptions import InvalidFormatError, InvalidParameterError


# Patrón válido para tarjeta: CCN|MM|AAAA|CVV
CARD_PATTERN = re.compile(r"^\d{13,19}\|\d{2}\|\d{4}\|\d{3,4}$")

# Patrón para username de Telegram
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


class Security:
    """Validación y sanitización de entradas de Calcifer."""

    @staticmethod
    def sanitize_text(text: str, max_length: int = 500) -> str:
        """Elimina caracteres peligrosos y limita la longitud."""
        if not isinstance(text, str):
            return ""
        # Eliminar caracteres de control
        text = re.sub(r"[\x00-\x1f\x7f]", "", text)
        # Limitar longitud
        return text[:max_length].strip()

    @staticmethod
    def validate_card_format(raw: str) -> tuple:
        """
        Valida el formato CCN|MM|AAAA|CVV.
        Retorna (ccn, month, year, cvv) si es válido.
        Lanza InvalidFormatError si no.
        """
        raw = (raw or "").strip()
        if not CARD_PATTERN.match(raw):
            raise InvalidFormatError(
                f"Formato inválido. Usa: CCN|MM|AAAA|CVV"
            )
        parts = raw.split("|")
        ccn, month, year, cvv = parts[0], parts[1], parts[2], parts[3]

        # Validar mes
        if not (1 <= int(month) <= 12):
            raise InvalidFormatError("Mes inválido (01-12)")

        return ccn, month, year, cvv

    @staticmethod
    def validate_card_expiry(month: str, year: str) -> bool:
        """Valida que la tarjeta no esté vencida."""
        from datetime import datetime
        from core.exceptions import ExpiredCardError
        now = datetime.utcnow()
        try:
            exp_year  = int(year)
            exp_month = int(month)
        except ValueError:
            raise InvalidFormatError("Fecha inválida")

        if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
            raise ExpiredCardError("Tarjeta vencida")
        return True

    @staticmethod
    def validate_telegram_id(telegram_id) -> int:
        """Valida que el telegram_id sea un entero positivo."""
        try:
            tid = int(telegram_id)
            if tid <= 0:
                raise ValueError
            return tid
        except (ValueError, TypeError):
            raise InvalidParameterError(f"telegram_id inválido: {telegram_id}")

    @staticmethod
    def validate_credits_amount(amount: int) -> int:
        """Valida que el monto de créditos sea 250 o 500."""
        valid_amounts = {250, 500}
        if amount not in valid_amounts:
            raise InvalidParameterError(
                f"Monto inválido: {amount}. Los valores permitidos son: 250 o 500"
            )
        return amount

    @staticmethod
    def sanitize_contract_params(raw_params: str) -> str:
        """Sanitiza los parámetros antes de pasarlos al módulo."""
        if not raw_params:
            return ""
        # Solo permitir: dígitos, letras, pipes, guiones y puntos
        return re.sub(r"[^\w|.\-]", "", raw_params)[:200]

    @staticmethod
    def mask_ccn(ccn: str) -> str:
        """Enmascara el CCN para logs: 424242xxxxxxxxxx."""
        if len(ccn) < 6:
            return "****"
        return ccn[:6] + "x" * (len(ccn) - 6)


    @staticmethod
    def validate_not_null(value, field_name: str):
        """Valida que un valor no sea None ni vacío."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise InvalidParameterError(field_name + " no puede estar vacío")
        return value

    @staticmethod
    def validate_max_length(value: str, field_name: str, max_len: int) -> str:
        """Valida que un string no supere la longitud máxima."""
        if len(value) > max_len:
            raise InvalidParameterError(
                field_name + " supera la longitud máxima de " + str(max_len) + " caracteres"
            )
        return value

    @staticmethod
    def validate_type(value, expected_type, field_name: str):
        """Valida que un valor sea del tipo esperado."""
        if not isinstance(value, expected_type):
            raise InvalidParameterError(
                field_name + " debe ser " + expected_type.__name__ +
                ", recibido: " + type(value).__name__
            )
        return value

    @staticmethod
    def validate_command(command: str) -> str:
        """Valida que un comando tenga formato válido (/comando)."""
        import re
        command = (command or "").strip()
        if not re.match(r"^/[a-zA-Z0-9_]+$", command):
            raise InvalidParameterError("Comando inválido: " + command)
        return command

    @staticmethod
    def validate_contract_structure(contract_in) -> bool:
        """Valida la estructura completa de un ContractIn antes de ejecutar."""
        from core.contracts import validate_contract_in
        data = contract_in.to_dict() if hasattr(contract_in, "to_dict") else contract_in
        if not validate_contract_in(data):
            raise InvalidParameterError("ContractIn inválido — campos requeridos faltantes")
        return True

    @staticmethod
    def sanitize_all(telegram_id, username: str, command: str, raw_params: str) -> tuple:
        """
        Punto único de sanitización completa de una solicitud entrante.
        Retorna (telegram_id, username, command, raw_params) sanitizados.
        """
        from core.security import Security
        s = Security()
        telegram_id = s.validate_telegram_id(telegram_id)
        username    = s.sanitize_text(username or "", 50)
        command     = s.validate_command(command)
        raw_params  = s.sanitize_contract_params(raw_params or "")
        return telegram_id, username, command, raw_params


security = Security()
