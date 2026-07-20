import os, logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from database.db import get_bin_cache, set_bin_cache, get_usuario, registrar_usuario, obtener_transaccion, historial_transacciones
from utils.responses import formatear_respuesta

load_dotenv()
logging.basicConfig(format="%(asctime)s — %(levelname)s — %(message)s", level=logging.INFO)
TOKEN = os.environ.get("TELEGRAM_TOKEN")

PASARELAS = {
    "stripe":"💳 Stripe","paypal":"🅿️ PayPal","shopify":"🛍️ Shopify",
    "square":"⬛ Square","amazon":"📦 Amazon Pay","adyen":"🔵 Adyen",
    "moneris":"🍁 Moneris","payflow":"🌊 Payflow","zuora":"🔄 Zuora"
}
EMOJI = {"Owner":"","Seller":"","Premium":"","Basic":"","Free":"","Trial":""}

import time as _time
_bin_last_call = 0
_bin_min_interval = 6  # segundos entre consultas a binlist.net

_bin_lookup_with_cache_func = None


def _bin_lookup_with_cache(bin_number: str) -> dict:
    """BIN Lookup con caché: BD → binlist.net → guardar en BD"""
    import requests as _req_bin
    empty = {"scheme": None, "type": None, "brand": None, "bank_name": None, "country_name": None, "alpha2": None}
    
    # 1° Consultar caché en BD
    try:
        cached = get_bin_cache(bin_number[:6])
        if cached and cached.get("bank"):
            return {
                "scheme"      : cached.get("brand"),
                "type"        : cached.get("type"),
                "brand"       : cached.get("level"),
                "bank_name"   : cached.get("bank"),
                "country_name": cached.get("country"),
                "alpha2"      : None,
                "flag"        : cached.get("country_flag"),
                "from_cache"  : True
            }
    except Exception:
        pass

    # 2° Consultar binlist.net con Rate Limiting
    _bin_rate_limit()
    try:
        resp = _req_bin.get(
            f"https://lookup.binlist.net/{bin_number[:6]}",
            headers={"Accept-Version": "3"},
            timeout=8
        )
        if resp.status_code != 200:
            return empty
        data = resp.json()
        alpha2 = data.get("country", {}).get("alpha2", "")
        flag = "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in alpha2.upper()) if alpha2 else None
        result = {
            "scheme"      : (data.get("scheme") or "").upper() or None,
            "type"        : (data.get("type") or "").upper() or None,
            "brand"       : (data.get("brand") or "").upper() or None,
            "bank_name"   : (data.get("bank", {}).get("name") or "").upper() or None,
            "country_name": data.get("country", {}).get("name") or None,
            "alpha2"      : alpha2,
            "flag"        : flag,
            "from_cache"  : False
        }
        # 3° Guardar en BD
        try:
            set_bin_cache(bin_number[:6], {
                "brand"       : result["scheme"],
                "type"        : result["type"],
                "level"       : result["brand"],
                "bank"        : result["bank_name"],
                "country"     : result["country_name"],
                "country_code": alpha2,
            })
        except Exception:
            pass
        return result
    except Exception:
        return empty

def _bin_rate_limit():
    global _bin_last_call
    elapsed = _time.time() - _bin_last_call
    if elapsed < _bin_min_interval:
        _time.sleep(_bin_min_interval - elapsed)
    _bin_last_call = _time.time()



def _build_info(t, l, b):
    """Construye info sin duplicados en orden TIPO-NIVEL-MARCA."""
    seen, parts = set(), []
    for p in [t, l, b]:
        if p and str(p).upper() not in seen:
            seen.add(str(p).upper())
            parts.append(str(p).upper())
    return "-".join(parts) if parts else "N/A"

def _clean_country(country):
    """Elimina paréntesis y texto extra del nombre del país."""
    if not country:
        return "N/A"
    return country.split("(")[0].strip()

def _flag(alpha2):
    """Convierte código de país a emoji de bandera."""
    try:
        return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in alpha2.upper())
    except:
        return ""


ADMIN_ROLES = ["Owner","Seller"]

def hora():
    n = datetime.utcnow()
    return n.strftime("%H:%M:%S"), n.strftime("%Y-%m-%d")

async def acceso(update):
    """Verifica acceso — usuarios bloqueados no reciben NINGUNA respuesta."""
    d = get_usuario(str(update.effective_user.id))
    if not d:
        await update.message.reply_text(
            "🚫 No tienes acceso al bot🥺🫩\nUsa /register para registrarte."
        )
        return False
    if not d.get("activo"):
        # Usuario bloqueado — NO responde nada
        return False
    return True

async def es_admin(update):
    d = get_usuario(str(update.effective_user.id))
    return d and d.get("membresia") in ADMIN_ROLES and d.get("activo")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    h, f = hora()
    d = get_usuario(str(u.id))
    if not d:
        await update.message.reply_text(
            f"🎉🎉 Bienvenidos a [Calcifer](https://t.me/Calciferfreebot) el mejor bot del mercado ✅ 🇨🇴\n\n"
            f"Usuario: @{u.username or 'Sin usuario'}\nID: `{u.id}`\nHora: {h}\n"
            f"Fecha de activación: {f}\nMembresía: No Activo‼️🚫\n\nUsa /register para registrarte.",
            parse_mode="Markdown", disable_web_page_preview=True)
        return
    if not d.get("activo"):
        # Bloqueado — no responde nada
        return
    mem = d.get("membresia","Free")
    await update.message.reply_text(
        f"🎉🎉 Bienvenidos a Calcifer el mejor bot del mercado ✅ 🇨🇴\n\n"
        f"Usuario: @{u.username or 'Sin usuario'}\nID: <code>{u.id}</code>\nHora: {h}\n"
        f"Fecha de activación: {d.get('fecha_activacion',f)}\nMembresía: [{mem}]",
        parse_mode="HTML", disable_web_page_preview=True)

async def cmd_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    h, f = hora()
    d = get_usuario(str(u.id))
    if d:
        if not d.get("activo"):
            # Bloqueado — no responde nada
            return
        mem = d.get("membresia","Free")
        await update.message.reply_text(
            f"⚠️ Ya estás registrado.\nMembresía: {mem}\nUsa /perfil para ver tu información.",
            parse_mode="Markdown")
        return
    registrar_usuario(str(u.id), u.username or "Sin usuario", u.first_name or "Usuario")
    await update.message.reply_text(
        f"🎉🥳 Registro exitoso en <a href='https://t.me/Calciferfreebot'>Calcifer</a>! 🤑💳\n\n"
        f"Usuario: @{u.username or 'Sin usuario'}\nID: <code>{u.id}</code>\n"
        f"Membresía: [Free]\nHora: {h}\nFecha de Registro: {f}",
        parse_mode="HTML", disable_web_page_preview=True)

async def cmd_perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    u = update.effective_user
    d = get_usuario(str(u.id))
    mem = d.get("membresia","Free")
    cr = d.get("creditos",0)
    await update.message.reply_text(
        f"Perfil de @{u.username or 'Sin usuario'}\n\n"
        f"ID: <code>{u.id}</code>\nMembresía: [{mem}]\nActivación: {d.get('fecha_activacion','N/A')}\n"
        f"Vencimiento: {d.get('fecha_vencimiento','N/A')}\nCréditos: {'♾️ Ilimitados' if cr==-1 else cr}",
        parse_mode="HTML")

async def cmd_addmembresia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    if not await es_admin(update):
        await update.message.reply_text("🚫 No tienes permiso."); return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "❓ *Uso:*\n`/addmembresia @usuario membresia dias`\n\n"
            "*Ejemplos:*\n`/addmembresia @usuario Basic 15`\n"
            "`/addmembresia @usuario Basic 30`\n"
            "`/addmembresia @usuario Premium 15`\n"
            "`/addmembresia @usuario Premium 30`",
            parse_mode="Markdown"); return
    target = args[0].replace("@","")
    mem = args[1].capitalize()
    dias = int(args[2])
    if mem not in ["Basic","Premium","Free"]:
        await update.message.reply_text("❌ Membresía inválida. Usa: Basic, Premium, Free"); return
    from database.db import get_bin_cache, set_bin_cache, asignar_membresia, asignar_membresia_por_id
    # Detectar si es ID o username
    if target.isdigit():
        resultado = asignar_membresia_por_id(target, mem, dias)
        label = f"ID: {target}"
    else:
        resultado = asignar_membresia(target, mem, dias)
        label = f"@{target}"
    if resultado:
        cr = f"\nCréditos: `{250 if dias==15 else 500}`" if mem=="Premium" else ""
        await update.message.reply_text(
            f"✅ *Membresía asignada*\n\nUsuario: {label}\n"
            f"Membresía: [{mem}]\nDías: {dias}{cr}",
            parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ No se encontró {label}.\nDebe registrarse con /register")

async def cmd_deluser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    if not await es_admin(update):
        await update.message.reply_text("🚫 No tienes permiso."); return
    args = context.args
    if not args:
        await update.message.reply_text(
            "❓ *Uso:*\n`/deluser @usuario` o `/deluser ID`",
            parse_mode="Markdown"); return
    from database.db import get_bin_cache, set_bin_cache, eliminar_usuario
    identificador = args[0].replace("@","")
    if eliminar_usuario(identificador):
        await update.message.reply_text(f"✅ Usuario `{identificador}` eliminado.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ No se encontró `{identificador}`.", parse_mode="Markdown")

async def cmd_blockuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    if not await es_admin(update):
        await update.message.reply_text("🚫 No tienes permiso."); return
    args = context.args
    if not args:
        await update.message.reply_text(
            "❓ *Uso:*\n`/blockuser @usuario` o `/blockuser ID`",
            parse_mode="Markdown"); return
    from database.db import get_bin_cache, set_bin_cache, bloquear_usuario
    identificador = args[0].replace("@","")
    if bloquear_usuario(identificador):
        await update.message.reply_text(f"🚫 Usuario `{identificador}` bloqueado.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ No se encontró `{identificador}`.", parse_mode="Markdown")

async def cmd_unblockuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    if not await es_admin(update):
        await update.message.reply_text("🚫 No tienes permiso."); return
    args = context.args
    if not args:
        await update.message.reply_text(
            "❓ *Uso:*\n`/unblockuser @usuario` o `/unblockuser ID`",
            parse_mode="Markdown"); return
    from database.db import get_bin_cache, set_bin_cache, desbloquear_usuario
    identificador = args[0].replace("@","")
    if desbloquear_usuario(identificador):
        await update.message.reply_text(f"✅ Usuario `{identificador}` desbloqueado.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ No se encontró `{identificador}`.", parse_mode="Markdown")

async def cmd_verificar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    args = context.args
    if not args:
        await update.message.reply_text("❓ Uso: `/verificar REFERENCIA`", parse_mode="Markdown"); return
    t = obtener_transaccion(args[0])
    if not t:
        await update.message.reply_text(f"❌ No se encontró `{args[0]}`.", parse_mode="Markdown"); return
    await update.message.reply_text(
        formatear_respuesta(
            estado=t.get("estado"), response_code=t.get("response_code"),
            transaction_id=t.get("transaction_id"), auth_code=t.get("auth_code"),
            pasarela=t.get("pasarela"), monto=float(t.get("monto",0)),
            moneda=t.get("moneda","USD")),
        parse_mode="Markdown")

async def cmd_historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    ts = historial_transacciones(10)
    if not ts:
        await update.message.reply_text("📊 No hay transacciones aún."); return
    lineas = ["📊 *Últimas transacciones:*\n"]
    for t in ts:
        e = {"CHARGED":"💰","AUTH":"🔍","DECLINED":"❌","PENDING":"⏳"}.get(t["estado"],"❓")
        lineas.append(f"{e} `{t['reference']}`\n   {t['pasarela'].upper()} — {t['moneda']} {float(t['monto']):,.2f}\n")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_pasarelas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    await update.message.reply_text(
        "🏦 *Pasarelas:*\n\n" + "\n".join([f"✅ {v}" for v in PASARELAS.values()]),
        parse_mode="Markdown")

async def cmd_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    h, f = hora()
    await update.message.reply_text(
        f"📈 *Estado Calcifer*\n🕐 {h} — {f}\n\n"
        f"🟢 Bot: *Activo*\n🟢 Servidor: *Corriendo*\n🟢 Base de datos: *Conectada*",
        parse_mode="Markdown")

async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await acceso(update): return
    await update.message.reply_text(
        "❓ *Ayuda — Calcifer*\n\n"
        "/start — Iniciar\n/register — Registrarse\n/perfil — Ver perfil\n"
        "/verificar — Verificar pago\n/historial — Transacciones\n"
        "/pasarelas — Ver pasarelas\n/estado — Estado\n\n"
        "*Solo Owner y Seller:*\n"
        "/addmembresia — Asignar membresía\n"
        "/deluser — Eliminar usuario\n"
        "/blockuser — Bloquear usuario\n"
        "/unblockuser — Desbloquear usuario",
        parse_mode="Markdown")

async def bloquear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        t = update.message.text
        if t.startswith("/start") or t.startswith("/register"):
            return
    # Verificar si está bloqueado — no responder nada
    d = get_usuario(str(update.effective_user.id))
    if d and not d.get("activo"):
        return
    await update.message.reply_text(
        "🚫 No tienes acceso al bot🥺🫩\nUsa /register para registrarte.")


async def cmd_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /bin — Consulta información de un BIN"""
    if not await acceso(update): return

    import requests as _req

    args = context.args
    if not args:
        await update.message.reply_text(
            "*Ejemplo:* `/bin 454676`",
            parse_mode="Markdown"
        )
        return

    bin_number = args[0].strip()[:8]

    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text(
            "❌ BIN inválido. Debe tener mínimo 6 dígitos.",
            parse_mode="Markdown"
        )
        return

    try:
        result = _bin_lookup_with_cache(bin_number)
        if not result or not result.get("bank_name"):
            await update.message.reply_text("❌ BIN no encontrado.")
            return
        brand   = result.get("scheme") or "N/A"
        tipo    = result.get("type") or "N/A"
        nivel   = result.get("brand") or "N/A"
        bank    = result.get("bank_name") or "N/A"
        country = result.get("country_name") or "N/A"
        flag    = result.get("flag") or ""
        nivel_words = (result.get("brand") or "").split()
        nivel_clean = " ".join(w for w in nivel_words if w not in [(result.get("type") or ""), (result.get("scheme") or "")])
        nivel_clean = nivel_clean.strip() or None
        info = _build_info(result.get("type") or "N/A", nivel_clean, result.get("scheme") or "N/A")

        u = update.effective_user
        d = get_usuario(str(u.id))
        membresia = d.get("membresia", "Free") if d else "Free"

        respuesta = (
            f"Bin : <code>{bin_number}</code>\n"
            f"Información : <code>{info}</code>\n"
            f"País : <code>{_clean_country(country)}</code> {flag}\n"
            f"Banco : <code>{bank}</code>\n"
            f"Usuario : @{u.username or str(u.id)} [{membresia}]\n"
            f"Bot : @Calciferfreebot\n"
            f"Canal : <a href='https://t.me/+7oC8iNDacgY4MjUx'>Official Page</a>"
        )
        await update.message.reply_text(respuesta, parse_mode="HTML", disable_web_page_preview=True)

    except Exception:
        await update.message.reply_text("❌ Error consultando el BIN.")

async def cmd_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /gen — Generador de tarjetas con algoritmo Luhn"""
    if not await acceso(update): return

    import random, re, requests as _req

    args = context.args
    if not args:
        await update.message.reply_text(
            "Por favor inserte datos.\n\n"
            "*Ejemplo:* `/gen 556110227515xxxx|10|26|xxx`\n\n"
            "*Formatos permitidos:*\n"
            "`454676xxxxxxxxxx|08|26|249`\n"
            "`454676087512xxxx|08|26|249`\n"
            "`4546760x75xx04x4|08|26|249`\n\n"
            "`454676xxxxxxxxxx|08|26|xxx`\n"
            "`454676087512xxxx|08|26|xxx`\n\n"
            "`454676xxxxxxxxxx`\n"
            "`454676087512xxxx`\n"
            "`4546760x75xx04x4`",
            parse_mode="Markdown"
        )
        return

    raw = args[0].strip()
    parts = raw.split("|")

    # Parsear CCN template
    ccn_template = parts[0] if len(parts) >= 1 else raw
    month_template = parts[1] if len(parts) >= 2 else None
    year_template  = parts[2] if len(parts) >= 3 else None
    cvv_template   = parts[3] if len(parts) >= 4 else None

    # Validar longitud del CCN template
    if len(ccn_template) != 16 or not re.match(r'^[0-9x]+$', ccn_template.lower()):
        await update.message.reply_text(
            "❌ Formato inválido. El CCN debe tener 16 dígitos (usa `x` para posiciones aleatorias).",
            parse_mode="Markdown"
        )
        return

    def luhn_complete(number_str):
        """Completa el último dígito para pasar el algoritmo de Luhn."""
        digits = [int(d) for d in number_str[:-1]]
        total = 0
        for i, d in enumerate(reversed(digits)):
            if i % 2 == 0:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        check = (10 - (total % 10)) % 10
        return number_str[:-1] + str(check)

    def gen_ccn(template):
        """Genera CCN basado en el template con x como comodín."""
        t = template.lower()
        # Reemplazar x por dígitos aleatorios
        filled = ""
        for ch in t[:-1]:
            filled += str(random.randint(0, 9)) if ch == "x" else ch
        filled += "x"  # último dígito lo calcula Luhn
        return luhn_complete(filled)

    def gen_month(template):
        if template is None or template.lower() == "xx":
            return str(random.randint(1, 12)).zfill(2)
        return template.zfill(2)

    def gen_year(template):
        if template is None or template.lower() == "xx":
            return str(random.randint(26, 30))
        return template

    def gen_cvv(template):
        if template is None or template.lower() in ("xxx", "xxxx"):
            length = 4 if template and len(template) == 4 else 3
            return str(random.randint(0, 10**length - 1)).zfill(length)
        return template

    # Generar 10 tarjetas
    cards = []
    for _ in range(10):
        ccn   = gen_ccn(ccn_template)
        month = gen_month(month_template)
        year  = gen_year(year_template)
        cvv   = gen_cvv(cvv_template)
        cards.append(f"{ccn}|{month}|{year}|{cvv}")

    # BIN Lookup
    bin_number = ccn_template[:6].replace("x", "0").replace("X", "0")
    bin_info = {"brand": None, "type": None, "level": None, "bank": None, "country": None, "flag": None}
    try:
        result_bin = _bin_lookup_with_cache(bin_number)
        if result_bin:
            bin_info["brand"]   = result_bin.get("scheme")
            bin_info["type"]    = result_bin.get("type")
            bin_info["level"]   = result_bin.get("brand")
            bin_info["bank"]    = result_bin.get("bank_name")
            bin_info["country"] = result_bin.get("country_name")
            bin_info["flag"]    = result_bin.get("flag")
    except Exception:
        pass

    u = update.effective_user
    d = get_usuario(str(u.id))
    membresia = d.get("membresia", "Free") if d else "Free"

    # Información BIN
    info = _build_info(bin_info["type"], bin_info["level"], bin_info["brand"])
    bank    = bin_info["bank"]    or "N/A"
    country = bin_info["country"] or "N/A"
    flag    = bin_info["flag"]    or ""
    sep = "━━━━━━━━╰☆╮━━━━━━━━"
    cards_text = "\n".join(f"<code>{card}</code>" for card in cards)
    country_clean = _clean_country(country)
    # Sin duplicados en info — limpiar palabras dentro del nivel
    tipo_g  = (bin_info["type"]  or "").upper()
    nivel_g = (bin_info["level"] or "").upper()
    brand_g = (bin_info["brand"] or "").upper()
    nivel_words = [w for w in nivel_g.split() if w not in tipo_g.split() and w not in brand_g.split()]
    nivel_g = " ".join(nivel_words).strip() or None
    seen, info_parts = set(), []
    for p in [tipo_g, nivel_g, brand_g]:
        if p and p.upper() not in seen:
            seen.add(p.upper())
            info_parts.append(p.upper())
    info_clean = "-".join(info_parts) if info_parts else "N/A"
    sep = "━━━━━━━━╰☆╮━━━━━━━━"
    respuesta = (
        f"{cards_text}\n"
        f"{sep}\n"
        f"Información : <code>{info_clean}</code>\n"
        f"Banco : <code>{bank}</code>\n"
        f"País : <code>{country_clean}</code> {flag}\n"
        f"{sep}\n"
        f"Usuario : @{u.username or str(u.id)} [{membresia}]\n"
        f"Bot : <a href='https://t.me/Calciferfreebot'>@Calciferfreebot</a>\n"
        f"Canal : <a href='https://t.me/+7oC8iNDacgY4MjUx'>Official Page</a>"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Generar más", callback_data=f"gen:{args[0]}")
    ]])
    await update.message.reply_text(respuesta, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)

async def callback_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random, re, requests as _req
    query = update.callback_query
    await query.answer()
    if not query.data.startswith("gen:"):
        return
    raw = query.data.split("gen:")[1]

    def luhn_complete(number_str):
        digits = [int(d) for d in number_str[:-1]]
        total = 0
        for i, d in enumerate(reversed(digits)):
            if i % 2 == 0:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
        return number_str[:-1] + str((10 - (total % 10)) % 10)

    def gen_ccn(template):
        t = template.lower()
        filled = "".join(str(random.randint(0,9)) if ch=="x" else ch for ch in t[:-1]) + "x"
        return luhn_complete(filled)

    parts = raw.split("|")
    ccn_template   = parts[0]
    month_template = parts[1] if len(parts) >= 2 else None
    year_template  = parts[2] if len(parts) >= 3 else None
    cvv_template   = parts[3] if len(parts) >= 4 else None

    def gen_month(t):
        return str(random.randint(1,12)).zfill(2) if not t or re.match(r"^x+$", t.lower()) else t.zfill(2)

    def gen_year(t):
        return str(random.randint(26,30)) if not t or re.match(r"^x+$", t.lower()) else t

    def gen_cvv(t):
        if not t or re.match(r"^x+$", t.lower()):
            return str(random.randint(0, 10**len(t if t else "xxx") - 1)).zfill(len(t if t else "xxx"))
        return t

    cards = []
    for _ in range(10):
        cards.append(f"{gen_ccn(ccn_template)}|{gen_month(month_template)}|{gen_year(year_template)}|{gen_cvv(cvv_template)}")

    cards_text = "\n".join(f"<code>{card}</code>" for card in cards)

    # BIN lookup
    bin_number = ccn_template[:6].replace("x","0").replace("X","0")
    bin_info = {"type":None,"level":None,"brand":None,"bank":None,"country":None,"flag":None}
    try:
        result_bin = _bin_lookup_with_cache(bin_number)
        if result_bin:
            bin_info["brand"]   = result_bin.get("scheme")
            bin_info["type"]    = result_bin.get("type")
            bin_info["level"]   = result_bin.get("brand")
            bin_info["bank"]    = result_bin.get("bank_name")
            bin_info["country"] = result_bin.get("country_name")
            bin_info["flag"]    = result_bin.get("flag")
    except Exception:
        pass

    tipo_cb  = (bin_info["type"]  or "").upper()
    nivel_cb = (bin_info["level"] or "").upper()
    brand_cb = (bin_info["brand"] or "").upper()
    nivel_words = [w for w in nivel_cb.split() if w not in tipo_cb.split() and w not in brand_cb.split()]
    nivel_cb = " ".join(nivel_words).strip() or None
    seen, info_parts = set(), []
    for p in [tipo_cb, nivel_cb, brand_cb]:
        if p and p.upper() not in seen:
            seen.add(p.upper())
            info_parts.append(p.upper())
    info_clean = "-".join(info_parts) if info_parts else "N/A"
    bank    = bin_info["bank"]    or "N/A"
    country = _clean_country(bin_info["country"] or "N/A")
    flag    = bin_info["flag"]    or ""
    sep     = "━━━━━━━━╰☆╮━━━━━━━━"

    u = query.from_user
    d = get_usuario(str(u.id))
    membresia = d.get("membresia","Free") if d else "Free"

    respuesta = (
        f"{cards_text}\n"
        f"{sep}\n"
        f"Información : <code>{info_clean}</code>\n"
        f"Banco : <code>{bank}</code>\n"
        f"País : <code>{country}</code> {flag}\n"
        f"{sep}\n"
        f"Usuario : @{u.username or str(u.id)} [{membresia}]\n"
        f"Bot : <a href='https://t.me/Calciferfreebot'>@Calciferfreebot</a>\n"
        f"Canal : <a href='https://t.me/+7oC8iNDacgY4MjUx'>Official Page</a>"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Generar más", callback_data=f"gen:{raw}")
    ]])
    await query.edit_message_text(respuesta, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",         cmd_start))
    app.add_handler(CommandHandler("register",      cmd_register))
    app.add_handler(CommandHandler("perfil",        cmd_perfil))
    app.add_handler(CommandHandler("addmembresia",  cmd_addmembresia))
    app.add_handler(CommandHandler("deluser",       cmd_deluser))
    app.add_handler(CommandHandler("blockuser",     cmd_blockuser))
    app.add_handler(CommandHandler("unblockuser",   cmd_unblockuser))
    app.add_handler(CommandHandler("bin",          cmd_bin))
    app.add_handler(CommandHandler("gen",          cmd_gen))
    app.add_handler(CallbackQueryHandler(callback_gen, pattern="^gen:"))
    app.add_handler(MessageHandler(filters.ALL, bloquear))
    print("🔥 Calcifer Bot arrancando...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
