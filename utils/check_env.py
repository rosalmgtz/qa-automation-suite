import os
import sys
from pkg_resources import get_distribution, DistributionNotFound

# 📦 Validación de dependencias y sus versiones exactas
packages = {
    "selenium": "4.21.0",
    "undetected_chromedriver": "3.5.5",
    "webdriver_manager": "4.0.2",
    "pytest": "8.4.1",
    "pytest-html": "4.1.1",
    "pytest-cov": "4.1.0",
    "pytest-mock": "3.14.0",
    "openpyxl": "3.1.2",
    "python-dotenv": "1.1.1",
    "google-api-python-client": "2.126.0",
    "google-auth": "2.40.3",
    "oauth2client": "4.1.3",
    "requests": "2.32.4",
}

# 📁 Carpetas técnicas que deben existir en el proyecto
required_dirs = [
    "tests",
    "pages",
    "utils",
    "config",
    "reports",
    "drivers",
    ".github",
    "docs"
]

# --- VERIFICACIÓN DE PAQUETES ---
print("\n📦 Verificación de paquetes instalados")
print("-" * 45)
all_packages_ok = True
for package, expected_version in packages.items():
    try:
        installed_version = get_distribution(package).version
        if installed_version == expected_version:
            print(f"✅ {package} {installed_version}")
        else:
            # Reportar como advertencia, pero no necesariamente como error fatal
            print(
                f"⚠️ {package} {installed_version} - esperado: {expected_version}")
            all_packages_ok = False  # Considerar un error si la versión no coincide
    except DistributionNotFound:
        print(f"❌ {package} no está instalado")
        all_packages_ok = False
    except Exception as e:
        print(f"⚠️ Error al verificar {package}: {e}")
        all_packages_ok = False  # Considerar un error

# --- VERIFICACIÓN DE ESTRUCTURA DE CARPETAS ---
print("\n📁 Verificación de estructura de carpetas")
print("-" * 45)

# Obtiene la ruta del directorio del script actual (ej. C:\...\scripts-selenium\utils o /home/.../utils)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Sube un nivel para obtener la ruta raíz del proyecto (ej. C:\...\scripts-selenium o /home/.../qa-automation-suite)
# Parte crucial que ahora funciona de forma universal.
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))

missing_dirs = []
for folder in required_dirs:
    full_path = os.path.join(project_root, folder)
    if os.path.isdir(full_path):
        print(f"✅ Carpeta encontrada: {folder}/")
    else:
        print(f"❌ Carpeta faltante: {folder}/")
        missing_dirs.append(folder)

# --- RESULTADO FINAL ---
print("\n📝 Resultado final")
print("-" * 45)

if all_packages_ok and not missing_dirs:
    print("🎯 Entorno de automatización configurado correctamente.")
    print("📍 Fin de la validación")
    sys.exit(0)  # Salida exitosa
else:
    if not all_packages_ok:
        print("⚠️ Advertencia: Algunos paquetes requeridos no están instalados o no tienen la versión esperada.")
    if missing_dirs:
        print(
            f"⚠️ Error: Faltan las siguientes carpetas: {', '.join(missing_dirs)}")
    print("❌ La validación del entorno encontró problemas.")
    print("📍 Fin de la validación")
    sys.exit(1)  # Salida con error para GitHub Actions
