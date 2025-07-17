from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapapi.http import MediaFileUpload
from googleapiclient.discovery import build
from datetime import datetime
import openpyxl
import json
import shutil
import os
import sys
iimport subprocess


# Función auxiliar para construir la ruta a un archivo de credenciales
# Esto permite que el código sea flexible para encontrar archivos en CI o localmente
def get_credentials_path(filename):
    # Ruta relativa para el entorno de CI (donde GitHub Actions los recrea en 'config/')
    # __file__ es el path del script actual, os.path.dirname(__file__) es su directorio
    # '..' sube un nivel al directorio raíz del proyecto (scripts-selenium/)
    # 'config' baja al directorio config/
    ci_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'config', filename)
    if os.path.exists(ci_path):
        print(f"✅ Encontrado '{filename}' en la ruta CI: {ci_path}")
        return ci_path

    # Ruta para el entorno de desarrollo local (donde los guardaste de forma segura)
    # os.path.expanduser("~") obtiene el directorio base del usuario (ej. C:\Users\ssabr)
    local_secure_path = os.path.join(os.path.expanduser(
        "~"), "MisCredencialesSecretasQA", filename)
    if os.path.exists(local_secure_path):
        print(
            f"✅ Encontrado '{filename}' en la ruta local segura: {local_secure_path}")
        return local_secure_path

    # Si no se encuentra en ninguna de las ubicaciones esperadas
    raise FileNotFoundError(
        f"❌ No se encontró el archivo de credenciales '{filename}' en 'config/' "
        f"(para CI) ni en 'MisCredencialesSecretasQA/' (para local)."
    )


def asegurar_dependencias():
    for pkg in ["pytest", "pytest-html", "google-api-python-client", "google-auth-oauthlib", "openpyxl"]:
        try:
            # Asegurarse de que el nombre del módulo sea el correcto para importación
            if pkg == "pytest-html":
                __import__("pytest_html")
            elif pkg == "google-api-python-client":
                __import__("googleapiclient")
            elif pkg == "google-auth-oauthlib":
                __import__("google_auth_oauthlib")
            else:
                __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Instalando módulo: {pkg}")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg])
    print("✅ Todas las dependencias verificadas/instaladas.")


def conectar_google_drive():
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    # Primero intenta obtener la ruta del token.json
    try:
        token_path = get_credentials_path("token.json")
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except FileNotFoundError:
        print("⚠️ token.json no encontrado. Se intentará generar uno nuevo.")

    # Si las credenciales no son válidas, expiran o no existen
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token expirado, intentando refrescar...")
            creds.refresh(Request())
        else:
            print(
                "🆕 No se encontró un token válido o está expirado/inválido. Iniciando flujo OAuth.")
            # Obtiene la ruta de credentials.json
            try:
                client_secrets_path = get_credentials_path(
                    "client_secret.json")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("❌ ERROR: No se pudo encontrar 'client_secret.json'. Asegúrate de que esté en 'config/' (CI) o en 'MisCredencialesSecretasQA/' (local).")
                sys.exit(1)  # Salir si no se pueden obtener las credenciales

        # Guarda el nuevo token (o refrescado) en la ubicación donde se encontró el token original (o se espera en CI)
        # Esto es importante para que en CI se escriba en config/token.json
        # y localmente en C:\Users\ssabr\MisCredencialesSecretasQA\token.json
        try:
            # Si el token_path fue encontrado previamente, úsalo.
            # Si no, asumimos que estamos en CI y lo escribimos en config/
            final_token_path = token_path if 'token_path' in locals() and os.path.exists(
                token_path) else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', "token.json")

            # Si estamos en local y el token se generó por primera vez, asegurar que se guarde en la carpeta segura
            if not os.path.exists(final_token_path) and not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', "token.json")):
                final_token_path = os.path.join(os.path.expanduser(
                    "~"), "MisCredencialesSecretasQA", "token.json")

            with open(final_token_path, "w") as token_file:
                token_file.write(creds.to_json())
            print(f"💾 Token guardado/actualizado en: {final_token_path}")
        except Exception as e:
            print(f"❌ Error al guardar/actualizar token.json: {e}")
            # No es un error crítico si la conexión se logró, pero se alerta.

    print("✅ Conexión a Google Drive establecida.")
    return build("drive", "v3", credentials=creds)


def obtener_id_carpeta_drive(nombre_carpeta, service):
    query = f"name='{nombre_carpeta}' and mimeType='application/vnd.google-apps.folder'"
    resultado = service.files().list(q=query, fields="files(id)").execute()
    if resultado["files"]:
        print(
            f"📁 Carpeta '{nombre_carpeta}' encontrada (ID: {resultado['files'][0]['id']})")
        return resultado["files"][0]["id"]

    # Si la carpeta no existe, la crea
    print(f"🆕 Carpeta '{nombre_carpeta}' no encontrada. Creando...")
    metadata = {"name": nombre_carpeta,
                "mimeType": "application/vnd.google-apps.folder"}
    carpeta = service.files().create(body=metadata, fields="id").execute()
    print(f"✅ Carpeta '{nombre_carpeta}' creada (ID: {carpeta['id']})")
    return carpeta["id"]


def subir_a_drive(ruta, folder_id, service):
    if not os.path.exists(ruta):
        print(f"❌ Archivo no encontrado, se omite subida: {ruta}")
        return

    # Intenta determinar el MIME type automáticamente, si es posible
    from mimetypes import guess_type
    # Por defecto si no puede adivinar
    mime_type = guess_type(ruta)[0] or 'application/octet-stream'

    print(f"📤 Subiendo: {os.path.basename(ruta)} con MIME type: {mime_type}")
    metadata = {"name": os.path.basename(ruta), "parents": [folder_id]}
    media = MediaFileUpload(ruta, mimetype=mime_type)

    try:
        archivo = service.files().create(
            body=metadata, media_body=media, fields='id').execute()
        print(f"✅ Subido: {os.path.basename(ruta)} (ID: {archivo['id']})")
    except Exception as e:
        print(f"❌ Error al subir {os.path.basename(ruta)} a Drive: {e}")


def actualizar_resumen_excel():
    # Este archivo se genera localmente en el proyecto
    nombre_json = "resumen_busquedas.json"
    # Este archivo también se genera localmente
    nombre_excel_local_resumen = "resumen_QA.xlsx"

    if not os.path.exists(nombre_json):
        print("⚠️ No se encontró resumen_busquedas.json, se omite actualización del resumen QA.")
        return

    try:
        with open(nombre_json, "r", encoding="utf-8") as f:
            resumen = json.load(f)
    except Exception as e:
        print(f"❌ Error al leer el JSON '{nombre_json}': {e}")
        return

    fecha = resumen.get("fecha", "desconocida")
    resultados = resumen.get("resultados", {})
    total_busquedas = sum(resultados.values())
    terminos = ", ".join(results.keys()) if results else "(sin datos)"

    # Rutas relativas a la carpeta donde se ejecuta Pytest y guarda los resultados
    # Asumiendo que pytest lo guarda en reports/
    ruta_html = f"reports/reporte_SABRINA_{fecha}.html"
    # Asumiendo que se mueve aquí
    ruta_excel_test_results = f"reports/busquedas_google_SABRINA_{fecha}.xlsx"

    estado_html = "✅" if os.path.exists(ruta_html) else "❌"
    estado_excel = "✅" if os.path.exists(ruta_excel_test_results) else "❌"
    estado_final = "Completado" if estado_html == "✅" and estado_excel == "✅" else "Parcial"

    # Cargamos o creamos el resumen_QA.xlsx que es global al proyecto
    if os.path.exists(nombre_excel_local_resumen):
        wb = openpyxl.load_workbook(nombre_excel_local_resumen)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Historial QA"
        encabezados = ["Fecha", "Total de búsquedas", "Términos usados",
                       "HTML generado", "Excel generado", "Estado"]
        ws.append(encabezados)

    nueva_fila = [fecha, total_busquedas, terminos,
                  estado_html, estado_excel, estado_final]
    ws.append(nueva_fila)
    wb.save(nombre_excel_local_resumen)

    print("\n📈 Resumen QA actualizado en 'resumen_QA.xlsx'")
    print("🗓️ Fecha:", fecha)
    print(f"🔍 Términos procesados ({len(resultados)}):")
    for termino, cantidad in resultados.items():
        print(f"   - {termino}: {cantidad} resultados")
    print(
        f"\n📄 Reporte HTML: {estado_html}    📊 Excel: {estado_excel}    🧪 Estado final: {estado_final}")


def ejecutar_suite():
    fecha = datetime.now().strftime("%Y-%m-%d")
    # La carpeta resultados_YYYY-MM-DD se crea dentro de la raíz del proyecto para los resultados temporales
    carpeta_local_resultados = f"resultados_{fecha}"
    os.makedirs(carpeta_local_resultados, exist_ok=True)

    nombre_html = f"reporte_SABRINA_{fecha}.html"
    nombre_excel = f"busquedas_google_SABRINA_{fecha}.xlsx"
    ruta_html_destino = os.path.join(carpeta_local_resultados, nombre_html)
    ruta_excel_destino = os.path.join(carpeta_local_resultados, nombre_excel)

    print("🚀 Ejecutando pruebas...")
    # Ejecuta pytest. Nota: si tu test_google_reporte_hml.py guarda el Excel directamente
    # en la raíz o en otra parte, asegúrate de que shutil.move lo encuentre.
    subprocess.run([
        sys.executable, "-m", "pytest",
        "test_google_reporte_hml.py",  # Asume que este es el script de prueba principal
        "--html", ruta_html_destino,  # Pytest guarda el HTML aquí
        "--self-contained-html",
        "-s"  # Para ver la salida de print en los tests
    ])

    # El archivo Excel puede ser generado por el test_google_reporte_hml.py
    # Si lo genera en la misma carpeta de ejecución, lo moveremos a la carpeta de resultados
    # Asegúrate de que el nombre del excel aquí coincida con el que genera tu test
    # <-- Revisa si tu test genera este nombre
    generated_excel_name = "busquedas_google.xlsx"
    if os.path.exists(generated_excel_name):
        shutil.move(generated_excel_name, ruta_excel_destino)
        print(
            f"📊 Excel de resultados de prueba guardado en: {ruta_excel_destino}")
    else:
        print(
            "⚠️ No se generó el Excel con resultados de prueba. Revisa tu script de prueba.")

    # Conectar a Google Drive usando la lógica de búsqueda de rutas
    service = conectar_google_drive()
    # Obtener ID de la carpeta principal en Google Drive
    folder_id = obtener_id_carpeta_drive("SABRINA_QA_Reports", service)

    # Subir los reportes generados a Google Drive
    subir_a_drive(ruta_html_destino, folder_id, service)
    # Sube el excel de los tests
    subir_a_drive(ruta_excel_destino, folder_id, service)

    # Actualizar el resumen general en Excel
    actualizar_resumen_excel()


if __name__ == "__main__":
    print("--- Iniciando Suite de Automatización QA ---")
    asegurar_dependencias()
    ejecutar_suite()
    print("--- Suite de Automatización QA Finalizada ---")
