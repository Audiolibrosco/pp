# 🔥 Calcifer Bot

Bot de Telegram para procesamiento y verificación de pagos multi-pasarela.

## Pasarelas (9)
Stripe · PayPal · Shopify · Square · Amazon Pay · Adyen · Moneris · Payflow · Zuora

## Stack
Python · Telegram · MySQL · Playwright · DigitalOcean

## Comandos
- `/start` — Iniciar el bot
- `/menu` — Menú principal
- `/verificar <ref>` — Verificar pago
- `/historial` — Últimas transacciones
- `/pasarelas` — Ver pasarelas
- `/estado` — Estado del sistema
- `/ayuda` — Ayuda completa

## Instalación
```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
python bot/calcifer.py
```

## Estructura
```
calcifer/
├── bot/           # Bot de Telegram
├── webhooks/      # Endpoints de webhooks
├── database/      # MySQL + schema
├── utils/         # Respuestas y utilidades
├── panel/         # Panel PHP (Hostinger)
├── .env.example   # Variables de entorno
└── requirements.txt
```
