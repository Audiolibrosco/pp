# 🔥 Calcifer — Developer Guide

## Estructura del Proyecto
calcifer/
├── bot/
│   └── calcifer.py          ← Bot principal de Telegram
├── core/                    ← Núcleo del sistema
│   ├── contracts.py         ← ContractIn / ContractOut
│   ├── exceptions.py        ← Excepciones personalizadas
│   ├── playwright_browser.py ← Browser base Playwright
│   ├── security.py          ← Validación de tarjetas
│   └── ...
├── modules/
│   ├── auth/                ← Módulos tipo AUTH
│   ├── charged/             ← Módulos tipo CHARGED
│   └── ccn/                 ← Módulos tipo CCN
├── database/
│   └── db.py                ← Conexión MySQL
└── utils/
└── responses.py         ← Respuestas predefinidas

## Estructura de un Módulo
modules/charged/<nombre>/
├── init.py      ← from modules.charged.<nombre>.<nombre> import run
├── config.py        ← Configuración y direcciones
├── validator.py     ← Validación del formato de tarjeta
├── bin_lookup.py    ← Consulta BIN
├── browser.py       ← Browser Playwright
└── <nombre>.py      ← Lógica principal
## Metadata del Módulo (metadata.json)

```json
{
  "name":         "start",
  "visible_name": "Start",
  "version":      "0.1.0",
  "type":         "charged",
  "command":      "/sc",
  "gateway":      "stripe",
  "commands":     ["/sc"],
  "dependencies": ["playwright","requests"]
}
```

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| ERR001 | Formato inválido |
| ERR002 | Sin permisos |
| ERR003 | Sin créditos |
| ERR004 | Sin acceso |
| ERR005 | Error interno |
| ERR006 | Timeout |
| ERR007 | Browser no inició |
| ERR008 | Error de navegación |
| ERR010 | En mantenimiento |
