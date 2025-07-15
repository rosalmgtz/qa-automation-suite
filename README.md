![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue)
![Google Drive API](https://img.shields.io/badge/Google%20Drive-API%20Integrated-green)
![suite.py Active](https://img.shields.io/badge/suite.py-active%20launcher-blue)

# 🧪 QA Automation Suite – Selenium + Pytest + Google Drive:

Este proyecto automatiza búsquedas en Google utilizando Selenium WebDriver y Pytest. Genera reportes HTML y Excel, guarda resultados estructurados, los sube a Google Drive y mantiene un historial de ejecuciones QA.

## 🚀 Funcionalidades principales:

- 🖱️ Pruebas automáticas en navegador sin CAPTCHA
- 📄 Reportes HTML visuales por ejecución
- 📊 Registro en Excel con estructura por fecha
- 🔍 Bitácora .txt con seguimiento técnico
- ☁️ Subida automática a Google Drive vía API
- 📈 Consolidación de resultados en `resumen_QA.xlsx`

## 🛠️ Tecnologías utilizadas:

| Herramienta        | Versión / Uso                        |
| ------------------ | ------------------------------------ |
| Python             | 3.x                                  |
| Selenium WebDriver | Control de navegador                 |
| Pytest + HTML      | Generador de reportes de prueba      |
| OpenPyXL           | Escritura y actualización de Excel   |
| Google API Client  | Subida de archivos a Drive           |
| ChromeDriver       | Ejecución sin detección automatizada |

## 📁 Estructura de archivos:

qa-automation-suite/  
├── suite.py # Launcher principal (antes run_sabrina_suite.py)  
├── test_busquedas_google.py # Script de prueba automatizada  
├── resumen_busquedas.json # Resultados estructurados  
├── resumen_QA.xlsx # Historial consolidado en Excel  
├── bitacora_QA.txt # Registro técnico de cada ejecución  
├── requirements.txt # Dependencias del proyecto para instalación  
├── .gitignore # Archivos excluidos del versionado  
├── README.md # Documentación principal del proyecto  
├── CHANGELOG.md # Historial técnico por fecha y cambios  
└── CONVERSACION_GIT_QA.md # Bitácora personal de configuración y comandos

## 🔧 Mejoras recientes:

- 🧠 Renombramiento del launcher principal a `suite.py` para mejorar semántica
- 🧹 Limpieza del repositorio: eliminación de script obsoleto y fusión remota controlada
- 📘 Actualización del README con estructura clara y nota de renombramiento
- 🖼️ Inclusión de badge visual para resaltar cambio activo

## 🧪 Ejecutar pruebas individuales:

#```bash
pytest test_busquedas_google.py --html=report.html

## 📌 Notas técnicas:

- La autenticación con Google Drive se gestiona vía OAuth 2.0 utilizando `credentials.json`
- Los reportes HTML se generan automáticamente con `pytest-html`, nombrados por fecha de ejecución
- El archivo `resumen_QA.xlsx` se actualiza en cada ejecución con resultados consolidados
- `suite.py` gestiona el flujo completo: ejecución de pruebas, generación de reportes y subida a la nube
- La bitácora técnica (`bitacora_QA.txt`) registra cada resultado con timestamp detallado

🔧 QA_Desarrollado y documentado por [Rosalba de la Merced Gutiérrez](https://github.com/rosalmgtz) – QA Automation Developer
