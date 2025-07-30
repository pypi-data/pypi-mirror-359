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

if __name__ == "__main__":
    crear_estructura()
