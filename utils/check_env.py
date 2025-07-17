import os
from pkg_resources import get_distribution, DistributionNotFound

# 📦 Validación de dependencias
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

print("\n📦 Verificación de paquetes instalados")
print("-" * 45)
for package, expected_version in packages.items():
    try:
        installed_version = get_distribution(package).version
        if installed_version == expected_version:
            print(f"✅ {package} {installed_version}")
        else:
            print(
                f"⚠️ {package} {installed_version} - esperado: {expected_version}")
    except DistributionNotFound:
        print(f"❌ {package} no está instalado")

print("\n📁 Verificación de estructura de carpetas")
print("-" * 45)
base_path = os.path.abspath(os.path.dirname(__file__)).replace("\\utils", "")
missing_dirs = []
for folder in required_dirs:
    full_path = os.path.join(base_path, folder)
    if os.path.isdir(full_path):
        print(f"✅ Carpeta encontrada: {folder}/")
    else:
        print(f"❌ Carpeta faltante: {folder}/")
        missing_dirs.append(folder)

print("\n📝 Resultado final")
print("-" * 45)
if not missing_dirs:
    print("🎯 Estructura de carpetas completa")
else:
    print(f"⚠️ Faltan las siguientes carpetas: {', '.join(missing_dirs)}")

print("\n📍 Fin de la validación")
