import sys
import os
from crear_flask_app.generador import crear_modulo, actualizar_init

def crear_estructura():
    nombre_proyecto = input("🔹 Nombre del proyecto: ").strip()
    ruta_base = os.path.abspath(nombre_proyecto)
    os.makedirs(ruta_base, exist_ok=True)

    os.makedirs(os.path.join(ruta_base, "app"), exist_ok=True)
    os.makedirs(os.path.join(ruta_base, "config"), exist_ok=True)
    os.makedirs(os.path.join(ruta_base, "conexiones"), exist_ok=True)

    # Archivos raíz
    crear_archivo(os.path.join(ruta_base, "run.py"), """from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5041)
""")

    crear_archivo(os.path.join(ruta_base, "config", "settings.py"), """import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "False") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
""")

    crear_archivo(os.path.join(ruta_base, "config", "__init__.py"), "")

    crear_archivo(os.path.join(ruta_base, "conexiones", "adaptadores.py"), "# Aquí puedes definir adaptadores de base de datos o servicios externos.\n")

    crear_archivo(os.path.join(ruta_base, ".env"), "DEBUG=True\nSECRET_KEY=mi-clave-super-secreta\n")

    # Módulos
    n = int(input("🔹 ¿Cuántos módulos deseas crear?: "))
    modulos = []
    for i in range(n):
        nombre = input(f"   ▪ Nombre del módulo #{i + 1}: ").strip().lower()
        crear_modulo(ruta_base, nombre)
        modulos.append(nombre)

    actualizar_init(ruta_base, modulos)
    print(f"\n✅ Proyecto '{nombre_proyecto}' generado exitosamente en: {ruta_base}")


def crear_archivo(ruta, contenido=""):
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)

def main():
    args = sys.argv

    if len(args) == 1:
        crear_estructura()

    elif len(args) == 4 and args[1] == "create" and args[2] == "module":
        nombre_modulo = args[3]
        ruta_base = os.getcwd()

        crear_modulo(ruta_base, nombre_modulo)

        # Actualizar __init__.py
        app_path = os.path.join(ruta_base, "app")
        modulos = [d for d in os.listdir(app_path) if os.path.isdir(os.path.join(app_path, d))]
        actualizar_init(ruta_base, modulos)

        print(f"✅ Módulo '{nombre_modulo}' creado correctamente en {ruta_base}/app/{nombre_modulo}")

    else:
        print("❌ Comando no reconocido.")
        print("\nUso:")
        print("  fk                            → Crea un nuevo proyecto Flask")
        print("  fk create module <nombre>    → Crea un nuevo módulo en 'app/'")

if __name__ == "__main__":
    main()
