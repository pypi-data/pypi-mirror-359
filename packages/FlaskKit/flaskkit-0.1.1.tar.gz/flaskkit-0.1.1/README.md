# 🚀 FlaskKit

**FlaskKit** es una herramienta de línea de comandos (CLI) para generar de forma automática la estructura base de un proyecto Flask modular, con una organización escalable, clara y lista para iniciar el desarrollo de cualquier API o aplicación web con Flask.

---

## 📦 ¿Qué hace esta herramienta?

Al ejecutar el comando `crear-flask-app`, se generará automáticamente una estructura completa con:

- Carpeta `apps/` con módulos que contienen `routers.py` y `db.py`
- Archivo de entrada `run.py`
- Carpeta `config/` con archivo `settings.py` usando variables de entorno
- Carpeta `conexiones/` con archivo `adaptadores.py`
- Estructura preparada para usar Flask, CORS, y dotenv
- Sistema basado en patrón de fábrica y aplicación modular

---

## 📁 Estructura generada

```bash
mi_proyecto/
│
├── run.py
├── .env
├── config/
│   └── settings.py
│
├── conexiones/
│   └── adaptadores.py
│
├── apps/
│   ├── __init__.py
│   ├── modulo1/
│   │   ├── routers.py
│   │   └── db.py
│   ├── modulo2/
│   │   ├── routers.py
│   │   └── db.py
│   └── ...
