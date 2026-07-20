"""
Calcifer — Códigos de respuesta unificados para las 9 pasarelas
Maneja: #AUTH, #CHARGED, #DECLINED, CVV, AVS, 3D Secure
"""

# ── MENSAJES POR ESTADO ──────────────────────────────────────────────────────

MENSAJES_ESTADO = {
    "AUTH": (
        "🔍 *#AUTH — Tarjeta verificada*\n"
        "El banco confirmó que la tarjeta existe.\n"
        "El cobro real aún no se ha realizado."
    ),
    "CHARGED": (
        "💰 *#CHARGED — Pago exitoso*\n"
        "El cobro fue realizado correctamente.\n"
        "El dinero fue debitado de la cuenta."
    ),
    "DECLINED": (
        "❌ *#DECLINED — Pago rechazado*\n"
        "El banco rechazó la transacción."
    ),
    "PENDING": (
        "⏳ *PENDING — En proceso*\n"
        "Verificación 3D Secure en curso.\n"
        "Esperando confirmación del banco."
    ),
    "CANCELLED": (
        "🚫 *CANCELLED — Cancelado*\n"
        "El pago fue cancelado."
    ),
    "EXPIRED": (
        "⌛ *EXPIRED — Vencido*\n"
        "El link de pago venció.\n"
        "Intenta de nuevo."
    ),
}

# ── MENSAJES DE ERROR (#DECLINED) ────────────────────────────────────────────

MENSAJES_ERROR = {
    # CVV
    "INVALID_SECURITY_CODE":     "❌ *CVV incorrecto*\nEl código de seguridad no coincide con el del banco.",
    "CVV_FAILURE":               "❌ *CVV incorrecto*\nEl código de seguridad no coincide con el del banco.",

    # Fondos
    "INSUFFICIENT_FUNDS":        "❌ *Fondos insuficientes*\nLa tarjeta no tiene saldo suficiente.",
    "INSUFFICIENT_BALANCE":      "❌ *Fondos insuficientes*\nLa tarjeta no tiene saldo suficiente.",

    # Tarjeta vencida
    "EXPIRED_CARD":              "❌ *Tarjeta vencida*\nLa tarjeta está expirada. Usa otra.",
    "INVALID_EXPIRY_DATE":       "❌ *Tarjeta vencida*\nLa fecha de vencimiento es inválida.",

    # Tarjeta bloqueada
    "CARD_BLOCKED":              "❌ *Tarjeta bloqueada*\nComunícate con tu banco.",
    "RESTRICTED_CARD":           "❌ *Tarjeta restringida*\nComunícate con tu banco.",
    "STOLEN_CARD":               "❌ *Tarjeta reportada*\nComunícate con tu banco.",
    "LOST_CARD":                 "❌ *Tarjeta reportada como perdida*\nComunícate con tu banco.",

    # Límite
    "EXCEEDS_AMOUNT_LIMIT":      "❌ *Límite excedido*\nSuperaste el límite de la tarjeta.",
    "TRANSACTION_NOT_PERMITTED": "❌ *Transacción no permitida*\nTu banco no permite esta operación.",
    "VELOCITY_EXCEEDED":         "❌ *Demasiados intentos*\nEspera unos minutos e intenta de nuevo.",

    # 3D Secure
    "THREE_D_SECURE_FAILED":     "❌ *3D Secure fallido*\nLa verificación del banco no fue completada.",
    "THREE_D_SECURE_TIMEOUT":    "❌ *3D Secure timeout*\nEl tiempo de verificación se agotó.",
    "3DS_REQUIRED":              "⏳ *3D Secure requerido*\nEl banco necesita verificación adicional.",
    "3DS_FAILURE":               "❌ *3D Secure fallido*\nNo se pudo completar la verificación.",

    # AVS
    "AVS_MISMATCH":              "❌ *AVS no coincide*\nLa dirección de facturación no coincide con la del banco.",
    "ADDRESS_VERIFICATION_FAILURE": "❌ *AVS fallido*\nLa dirección registrada no coincide.",

    # Fraude
    "FRAUD_DETECTED":            "❌ *Fraude detectado*\nTransacción bloqueada por seguridad.",
    "DO_NOT_HONOR":              "❌ *Banco rechazó el pago*\nComunícate con tu banco para más información.",

    # Errores generales
    "INVALID_CARD":              "❌ *Tarjeta inválida*\nVerifica los datos e intenta de nuevo.",
    "INVALID_TRANSACTION":       "❌ *Transacción inválida*\nIntenta de nuevo.",
    "SYSTEM_ERROR":              "❌ *Error del sistema*\nIntenta en unos minutos.",
    "CALL_ISSUER":               "❌ *Contacta tu banco*\nEl banco requiere que lo llames.",
}

# ── ESTADOS CVV ──────────────────────────────────────────────────────────────

MENSAJES_CVV = {
    "MATCH":         "✅ CVV correcto",
    "NO_MATCH":      "❌ CVV incorrecto",
    "NOT_PROVIDED":  "⚠️ CVV no proporcionado",
    "UNKNOWN":       "❓ CVV desconocido",
}

# ── ESTADOS AVS ──────────────────────────────────────────────────────────────

MENSAJES_AVS = {
    "MATCH":         "✅ Dirección verificada",
    "NO_MATCH":      "❌ Dirección no coincide",
    "PARTIAL":       "⚠️ Coincidencia parcial",
    "NOT_PROVIDED":  "⚠️ AVS no proporcionado",
    "UNKNOWN":       "❓ AVS desconocido",
}

# ── ESTADOS 3D SECURE ────────────────────────────────────────────────────────

MENSAJES_3DS = {
    "SUCCESS":       "✅ 3D Secure completado",
    "FAILED":        "❌ 3D Secure fallido",
    "PENDING":       "⏳ 3D Secure en proceso",
    "NOT_REQUIRED":  "➖ 3D Secure no requerido",
    "UNKNOWN":       "❓ 3D Secure desconocido",
}


def formatear_respuesta(estado: str, response_code: str = None,
                         cvv: str = None, avs: str = None,
                         secure_3d: str = None,
                         transaction_id: str = None,
                         auth_code: str = None,
                         pasarela: str = None,
                         monto: float = None,
                         moneda: str = "USD") -> str:
    """
    Genera el mensaje completo para Telegram según el estado de la transacción.
    """
    lineas = []

    # Pasarela
    if pasarela:
        lineas.append(f"🏦 *Pasarela:* {pasarela.upper()}")

    # Monto
    if monto:
        lineas.append(f"💵 *Monto:* {moneda} {monto:,.2f}")

    lineas.append("")

    # Estado principal
    if estado in MENSAJES_ESTADO:
        lineas.append(MENSAJES_ESTADO[estado])
    
    # Mensaje de error específico
    if response_code and estado == "DECLINED":
        mensaje_error = MENSAJES_ERROR.get(
            response_code,
            f"❌ *Pago rechazado*\nCódigo: `{response_code}`"
        )
        lineas.append(mensaje_error)

    lineas.append("")
    lineas.append("─────────────────")
    lineas.append("*Validaciones:*")

    # CVV
    if cvv:
        lineas.append(MENSAJES_CVV.get(cvv, f"CVV: {cvv}"))

    # AVS
    if avs:
        lineas.append(MENSAJES_AVS.get(avs, f"AVS: {avs}"))

    # 3D Secure
    if secure_3d:
        lineas.append(MENSAJES_3DS.get(secure_3d, f"3DS: {secure_3d}"))

    # Referencias
    if transaction_id or auth_code:
        lineas.append("")
        lineas.append("─────────────────")
        lineas.append("*Referencias:*")
        if transaction_id:
            lineas.append(f"🔍 Transaction ID: `{transaction_id}`")
        if auth_code:
            lineas.append(f"🔍 Auth Code: `{auth_code}`")

    return "\n".join(lineas)
