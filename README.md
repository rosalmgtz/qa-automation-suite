![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue)
![Google Drive API](https://img.shields.io/badge/Google%20Drive-API%20Integrated-green)
![suite.py Active](https://img.shields.io/badge/suite.py-active%20launcher-blue)
![CI Status](https://img.shields.io/github/actions/workflow/status/rosalmgtz/qa-automation-suite/python-ci.yml?branch=main)

# 🧪 QA Automation Suite – Selenium + Pytest + Google Drive:

Este proyecto automatiza búsquedas en Google utilizando Selenium WebDriver y Pytest. Genera reportes HTML y Excel, guarda resultados estructurados, los sube a Google Drive y mantiene un historial de ejecuciones QA. **Se ha implementado una robusta pipeline de Integración Continua (CI) con GitHub Actions para automatizar y asegurar todo el proceso.**

---

## 🚀 Funcionalidades Principales:

- 🖱️ **Pruebas automáticas en navegador (headless en CI) sin CAPTCHA:** Automatización de búsquedas en Google, diseñada para interactuar como un usuario real utilizando `undetected_chromedriver` para evadir detecciones y configurada para ejecutar en modo sin cabeza en el pipeline de CI.
- 📄 **Reportes HTML visuales por ejecución:** Generación de reportes de Pytest detallados y visuales para cada ejecución de prueba, proporcionando un resumen interactivo.
- 📊 **Registro en Excel con estructura por fecha:** Creación de archivos Excel (`.xlsx`) específicos por ejecución que contienen los resultados de las búsquedas, con hojas detalladas por término y un resumen general consolidado.
- 🔍 **Bitácora .txt con seguimiento técnico:** Mantenimiento de un archivo `.txt` con un registro detallado y técnico de cada ejecución, incluyendo timestamps y resultados clave.
- ☁️ **Subida automática a Google Drive vía API:** Integración completa para cargar los reportes HTML y Excel generados a una carpeta designada en Google Drive, facilitando la centralización y el acceso remoto.
- 📈 **Consolidación de resultados en `resumen_QA.xlsx`:** Un archivo Excel que actúa como un historial consolidado de todas las ejecuciones de QA, permitiendo un seguimiento a largo plazo del rendimiento.
- 🔐 **Gestión Segura de Credenciales:** Implementación de un sistema robusto para el manejo de credenciales sensibles de Google Drive, utilizando **Secretos de Repositorio en GitHub** para el entorno de CI y una carpeta local segura para el desarrollo (`MisCredencialesSecretasQA`).

## 🛠️ Tecnologías utilizadas:

| Herramienta             | Propósito                             |
| ----------------------- | ------------------------------------- |
| Python 3.x              | Lenguaje de programación principal    |
| Selenium WebDriver      | Automatización del navegador          |
| undetected-chromedriver | Evasión de detección tipo CAPTCHA     |
| Pytest + pytest-html    | Framework de pruebas + reportes HTML  |
| OpenPyXL                | Lectura y escritura en archivos Excel |
| Google API Client       | Subida a Drive con OAuth 2.0          |
| GitHub Actions          | Integración continua (CI/CD)          |

## 📁 Estructura de archivos:

qa-automation-suite/
├── .github/
│ └── workflows/
│ └── python-ci.yml # Definición del workflow de CI/CD para GitHub Actions.
├── config/ # Carpeta para almacenar temporalmente credenciales sensibles en CI (excluida de Git).
│ └── .gitkeep # Asegura que la carpeta 'config/' se suba a Git, incluso vacía.
├── reports/ # Directorio donde se guardan los reportes HTML y Excel generados localmente (excluido de Git).
│ └── .gitkeep # Asegura que la carpeta 'reports/' se suba a Git, incluso vacía.
├── utils/
│ └── check_env.py # Script de utilidad para verificar el ambiente y la estructura de carpetas necesaria.
├── suite.py # **Launcher Principal:** Orquesta la ejecución de pruebas, la generación de reportes y la subida a Google Drive.
├── test_google_reporte_html.py # Script principal de pruebas automatizadas para búsquedas en Google usando Pytest.
├── resumen_busquedas.json # Almacena los resultados estructurados de la última sesión de búsqueda.
├── resumen_QA.xlsx # Historial consolidado de todas las ejecuciones QA en formato Excel.
├── bitacora_QA.txt # Registro técnico detallado (bitácora) de cada ejecución con timestamps.
├── requirements.txt # Lista de dependencias de Python requeridas para la instalación del proyecto.
├── .gitignore # Define los archivos y directorios a excluir del control de versiones de Git.
├── README.md # Este documento de documentación principal del proyecto.
├── CHANGELOG.md # Historial técnico de cambios y versiones del proyecto.
└── CONVERSACION_GIT_QA.md # Bitácora personal/notas sobre la configuración y comandos Git/QA.

## 🔧 Mejoras recientes:

🧠 Orquestación Centralizada y Semántica: El lanzador principal run_sabrina_suite.py ha sido renombrado a suite.py para mejorar la claridad y centralizar todo el flujo de automatización del proyecto.

🧹 Limpieza y Consistencia del Repositorio: Se realizó una limpieza exhaustiva del repositorio, eliminando scripts obsoletos y unificando archivos de prueba, culminando en una fusión remota controlada para mantener un historial Git limpio.

📘 Documentación Exhaustiva: Actualización y expansión del README.md con una estructura clara, detalles sobre la integración de CI/CD, instrucciones de uso local y una descripción precisa de todos los componentes del proyecto.

🔐 Seguridad de Credenciales Robusta: Se implementó un sistema avanzado para el manejo seguro de credenciales sensibles de Google Drive, aprovechando GitHub Repository Secrets para el entorno de CI y una ruta de archivo segura (MisCredencialesSecretasQA) para el desarrollo local.

🚀 Pipeline de Integración Continua (CI) Completo: Configuración y depuración de un workflow de GitHub Actions que automatiza la ejecución de la suite de pruebas. Esto incluye la gestión de dependencias (con una solución específica para setuptools/pkg_resources), la inyección segura de credenciales y la subida de reportes como artefactos del workflow.

🖼️ Badges Informativos y Actualizados: Inclusión de badges visuales al inicio del README que resumen el estado del CI y las tecnologías clave utilizadas, proporcionando una vista rápida del proyecto.

## 💻 Instalación y Uso Local

Sigue estos pasos para configurar y ejecutar la suite de automatización en tu máquina local.

### Prerequisitos:

- **Python 3.x** instalado.
- Un **Proyecto de Google Cloud** con la **API de Google Drive** habilitada y credenciales OAuth 2.0 configuradas. Necesitarás descargar tu `client_secret.json`.

### Pasos de Instalación:

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/rosalmgtz/qa-automation-suite.git](https://github.com/rosalmgtz/qa-automation-suite.git)
    cd qa-automation-suite
    ```
2.  **Configurar Entorno Virtual (Recomendado):**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```
3.  **Instalar Dependencias del Proyecto:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuración Segura de Credenciales de Google Drive (Local):

Para que la suite pueda interactuar con Google Drive en tu entorno local, tus credenciales (`client_secret.json` y `token.json`) deben estar almacenadas de forma segura y **fuera del repositorio**.

- Crea una carpeta llamada `MisCredencialesSecretasQA` en tu directorio de usuario:
  - **Windows:** `C:\Users\tu_usuario\MisCredencialesSecretasQA`
  - **macOS/Linux:** `/home/tu_usuario/MisCredencialesSecretasQA`
- Coloca tu archivo `client_secret.json` (descargado de Google Cloud Platform) dentro de esta carpeta.
- El archivo `token.json` (que almacena tus tokens de acceso y refresco de OAuth) se creará automáticamente en esta misma ubicación la primera vez que ejecutes `python suite.py` y completes el flujo de autenticación.

---

## 🧪 Ejecutar pruebas individuales:

Ejecución Completa (Local):
Para iniciar la ejecución completa de la suite (tests, generación de reportes, subida a Drive):

Bash

python suite.py
Ejecutar Pruebas Individuales (Desarrollo/Debugging):
Para ejecutar un test específico o generar reportes HTML de forma manual (sin pasar por suite.py):

Bash

pytest test_google_reporte_html.py --html=reports/reporte_manual.html --self-contained-html

# Generar un reporte de cobertura de código (requiere pytest-cov en requirements.txt)

pytest --cov=. --cov-report=html

## ⚙️ Configuración de Integración Continua (CI) con GitHub Actions

Este proyecto cuenta con un pipeline de CI completamente funcional mediante GitHub Actions, definido en .github/workflows/python-ci.yml.

1. Configurar Secretos de Repositorio en GitHub
   Para que el workflow de CI pueda acceder a la API de Google Drive de forma segura, debes almacenar el contenido de tus archivos de credenciales como Secretos en tu repositorio de GitHub.

Abre el contenido de tus archivos client_secret.json, credentials.json (si aplica) y token.json (una vez generado localmente) con un editor de texto.

Copia el contenido JSON completo de cada archivo.

En tu repositorio de GitHub, navega a: Settings > Secrets and variables > Actions.

Haz clic en New repository secret y crea los siguientes secretos, pegando el contenido JSON correspondiente:

GOOGLE_CLIENT_SECRET_JSON

GOOGLE_CREDENTIALS_JSON (Si tu setup lo requiere; de lo contrario, puede omitirse.)

GOOGLE_API_TOKEN_JSON

2. Comportamiento del Workflow de CI
   El workflow python-ci.yml se dispara automáticamente en cada push a la rama main (y otras configuradas) y en cada pull_request. Realiza los siguientes pasos clave:

Configuración de Entorno: Configura el ambiente Python, instala dependencias del sistema y Python (incluyendo la solución para setuptools).

Inyección Segura de Credenciales: Lee los secretos de GitHub y recrea temporalmente los archivos de credenciales en la carpeta config/ del runner de CI. Estos archivos son efímeros y se eliminan al finalizar el job.

Ejecución de Pruebas: Ejecuta el script principal python suite.py en un navegador headless.

Generación y Subida de Artefactos: Los reportes HTML y Excel se generan en reports/ y se suben como artefactos del workflow, disponibles para descarga desde la página de GitHub Actions.

📌 Notas Técnicas Adicionales:
Autenticación Robusta: La autenticación con Google Drive se gestiona vía OAuth 2.0, utilizando el archivo token.json para mantener la sesión de forma segura y persistente.

Reportes Dinámicos: Los reportes HTML son generados automáticamente por pytest-html, nombrados por la fecha de ejecución para fácil seguimiento.

Gestión de Flujo: suite.py es el orquestador que gestiona el flujo completo: preparación del ambiente, ejecución de pruebas, generación y organización de reportes, y subida a la nube.

Registro Detallado: La bitácora técnica (bitacora_QA.txt) registra cada resultado con timestamp detallado para fines de auditoría y depuración.

## 📌 Notas técnicas:

- La autenticación con Google Drive se gestiona vía OAuth 2.0 utilizando `credentials.json`
- Los reportes HTML se generan automáticamente con `pytest-html`, nombrados por fecha de ejecución
- El archivo `resumen_QA.xlsx` se actualiza en cada ejecución con resultados consolidados
- `suite.py` gestiona el flujo completo: ejecución de pruebas, generación de reportes y subida a la nube
- La bitácora técnica (`bitacora_QA.txt`) registra cada resultado con timestamp detallado

## 📦 Versión estable

La versión actual de la suite está disponible como [Release v1.2 – Suite QA lista para CI.]

Esta versión incluye:

Soporte para ejecución headless controlada desde GitHub Actions.

Generación de reportes HTML y Excel automatizados.

Sincronización robusta con Google Drive.

Scripts listos para ser integrados en un pipeline CI/CD con Python y Selenium.

🔧 QA_Desarrollado y documentado por [Rosalba de la Merced Gutiérrez](https://github.com/rosalmgtz) – QA Automation Developer
