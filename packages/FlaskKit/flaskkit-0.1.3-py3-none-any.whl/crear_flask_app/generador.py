import os

def crear_archivo(ruta, contenido=""):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)

def crear_modulo(ruta_base, nombre):
    path = os.path.join(ruta_base, "app", nombre)
    os.makedirs(path, exist_ok=True)

    # routers.py
    routers_content = f"""from flask import Blueprint

bp = Blueprint('{nombre}', __name__, url_prefix='/{nombre}')

@bp.route('/')
def index():
    return "Hola desde el módulo {nombre}"
"""
    crear_archivo(os.path.join(path, "routers.py"), routers_content)

    # db.py
    crear_archivo(os.path.join(path, "db.py"), "# Configuración o modelos del módulo\n")

    # __init__.py
    crear_archivo(os.path.join(path, "__init__.py"), "")

def actualizar_init(ruta_base, modulos):
    contenido = """from flask import Flask
import os
from config import settings
from flask_cors import CORS
"""

    for mod in modulos:
        contenido += f"from app.{mod}.routers import bp as {mod}_bp\n"

    contenido += """

def create_app():
    app = Flask(__name__)
    app.config['SESSION_COOKIE_NAME'] = 'session'
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG
    CORS(app, supports_credentials=True, origins=["*"])
"""

    for mod in modulos:
        contenido += f"    app.register_blueprint({mod}_bp)\n"

    contenido += "\n    return app\n"
    crear_archivo(os.path.join(ruta_base, "app", "__init__.py"), contenido)
