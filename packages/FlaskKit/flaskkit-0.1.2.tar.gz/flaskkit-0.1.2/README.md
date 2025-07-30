# 🚀 FlaskKit

**FlaskKit** es una herramienta de línea de comandos (CLI) para generar automáticamente la estructura base de un proyecto Flask modular, con una organización escalaQble, clara y lista para iniciar el desarrollo de cualquier API o aplicación web con Flask.

---

## 📦 ¿Qué hace FlaskKit?

Al ejecutar el comando `fk`, se generará automáticamente una estructura completa con:

- Carpeta `apps/` con módulos que contienen `routers.py` y `db.py`
- Archivo principal de entrada `run.py`
- Carpeta `config/` con archivo `settings.py` usando variables de entorno
- Carpeta `conexiones/` con archivo `adaptadores.py`
- Estructura preparada para usar Flask, Flask-CORS, y python-dotenv
- Sistema basado en patrón de fábrica y arquitectura modular para facilitar escalabilidad y mantenimiento

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

🛠️ Instalación
Instala FlaskKit desde PyPI usando pip:
pip install flaskkit

Si tienes varias versiones de Python, puedes usar:
python -m pip install flaskkit


🧪 Uso
Luego de la instalación, usa el comando en la terminal para crear tu proyecto Flask:
flaskkit

Sobre el PATH y el comando flaskkit
Al instalar con pip, el comando flaskkit debería agregarse automáticamente a tu variable de entorno PATH.

Si al ejecutar flaskkit recibes un error de comando no reconocido, asegúrate de que la carpeta de scripts de Python esté en tu PATH.

En Windows, típicamente la carpeta está en:
C:\Users\<tu_usuario>\AppData\Local\Programs\Python\PythonXX\Scripts\


En Linux/macOS suele ser:
~/.local/bin
Agrega la ruta correspondiente a tu variable PATH para que el comando esté disponible desde cualquier lugar.

🚀 Próximas mejoras
Soporte para Blueprints automáticamente generados

Inclusión opcional de bases de datos con SQLAlchemy

Creación automática de entornos virtuales para cada proyecto

👤 Autor
Deiker Castilo
📧 deikerdcastillo@gmail.com


📄 Licencia
MIT License

📌 Proyecto en PyPI
🔗 https://pypi.org/project/flaskkit



