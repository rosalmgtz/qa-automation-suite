import subprocess
import sys
import os
import shutil
import json
import openpyxl
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials


# Función auxiliar para construir la ruta a un archivo de credenciales
# Esto permite que el código sea flexible para encontrar archivos en CI o localmente
def get_credentials_path(filename):
    # Ruta relativa para el entorno de CI (donde GitHub Actions los recrea en 'config/')
    # Como suite.py está en 'tests/', para llegar a 'config/' (en la raíz), necesitamos '../config/'
    ci_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '..', 'config', filename)

    # DEBUG LINE
    print(f"DEBUG: get_credentials_path - Calculando ci_path: {ci_path}")

    if os.path.exists(ci_path):
        print(f"✅ Encontrado '{filename}' en la ruta CI: {ci_path}")
        return ci_path

    # Ruta para el entorno de desarrollo local (donde los guardaste de forma segura)
    local_secure_path = os.path.join(os.path.expanduser(
        "~"), "MisCredencialesSecretasQA", filename)

    # DEBUG LINE
    print(
        f"DEBUG: get_credentials_path - Calculando local_secure_path: {local_secure_path}")

    if os.path.exists(local_secure_path):
        print(
            f"✅ Encontrado '{filename}' en la ruta local segura: {local_secure_path}")
        return local_secure_path

    raise FileNotFoundError(
        f"❌ No se encontró el archivo de credenciales '{filename}' en 'config/' "
        f"(para CI) ni en 'MisCredencialesSecretasQA/' (para local)."
    )


def asegurar_dependencias():
    for pkg in ["pytest", "pytest-html", "google-api-python-client", "google-auth-oauthlib", "openpyxl"]:
        try:
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

    try:
        token_path = get_credentials_path("token.json")
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except FileNotFoundError:
        print("⚠️ token.json no encontrado. Se intentará generar uno nuevo.")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token expirado, intentando refrescar...")
            creds.refresh(Request())
        else:
            print(
                "🆕 No se encontró un token válido o está expirado/inválido. Iniciando flujo OAuth.")
            try:
                client_secrets_path = get_credentials_path(
                    "client_secret.json")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("❌ ERROR: No se pudo encontrar 'client_secret.json'. Asegúrate de que esté en 'config/' (CI) o en 'MisCredencialesSecretasQA/' (local).")
                sys.exit(1)

        try:
            if 'token_path' in locals() and token_path and os.path.exists(token_path):
                final_token_path = token_path
            else:
                final_token_path = os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), '..', 'config', "token.json")

            if not os.path.exists(final_token_path) and not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', "token.json")):
                final_token_path = os.path.join(os.path.expanduser(
                    "~"), "MisCredencialesSecretasQA", "token.json")

            with open(final_token_path, "w") as token_file:
                token_file.write(creds.to_json())
            print(f"💾 Token guardado/actualizado en: {final_token_path}")
        except Exception as e:
            print(f"❌ Error al guardar/actualizar token.json: {e}")

    print("✅ Conexión a Google Drive establecida.")
    return build("drive", "v3", credentials=creds)


def obtener_id_carpeta_drive(nombre_carpeta, service):
    query = f"name='{nombre_carpeta}' and mimeType='application/vnd.google-apps.folder'"
    resultado = service.files().list(q=query, fields="files(id)").execute()
    if resultado["files"]:
        print(
            f"📁 Carpeta '{nombre_carpeta}' encontrada (ID: {resultado['files'][0]['id']})")
        return resultado["files"][0]["id"]

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

    from mimetypes import guess_type
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
    nombre_json = "resumen_busquedas.json"
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
    terminos = ", ".join(resultados.keys()) if resultados else "(sin datos)"

    ruta_html = os.path.join("..", "reports", f"reporte_SABRINA_{fecha}.html")
    ruta_excel_test_results = os.path.join(
        "..", "reports", f"busquedas_google_SABRINA_{fecha}.xlsx")

    estado_html = "✅" if os.path.exists(ruta_html) else "❌"
    estado_excel = "✅" if os.path.exists(ruta_excel_test_results) else "❌"
    estado_final = "Completado" if estado_html == "✅" and estado_excel == "✅" else "Parcial"

    ruta_resumen_qa_excel = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '..', nombre_excel_local_resumen)

    if os.path.exists(ruta_resumen_qa_excel):
        wb = openpyxl.load_workbook(ruta_resumen_qa_excel)
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
    wb.save(ruta_resumen_qa_excel)

    print("\n📈 Resumen QA actualizado en 'resumen_QA.xlsx'")
    print("🗓️ Fecha:", fecha)
    print(f"🔍 Términos procesados ({len(resultados)}):")
    for termino, cantidad in resultados.items():
        print(f"   - {termino}: {cantidad} resultados")
    print(
        f"\n📄 Reporte HTML: {estado_html}    📊 Excel: {estado_excel}    🧪 Estado final: {estado_final}")


def ejecutar_suite():
    fecha = datetime.now().strftime("%Y-%m-%d")

    ruta_html_destino = os.path.join(
        "..", "reports", f"reporte_SABRINA_{fecha}.html")
    ruta_excel_destino = os.path.join(
        "..", "reports", f"busquedas_google_SABRINA_{fecha}.xlsx")

    reports_dir = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '..', 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    print("🚀 Ejecutando pruebas...")
    subprocess.run([
        sys.executable, "-m", "pytest",
        "test_google_reporte_html.py",  # Nombre del script de prueba
        "--html", ruta_html_destino,  # Pytest guarda el HTML aquí
        "--self-contained-html",
        "-s"  # Para ver la salida de print en los tests
    ])

    if os.path.exists(ruta_excel_destino):
        print(
            f"📊 Excel de resultados de prueba guardado en: {ruta_excel_destino}")
    else:
        print("⚠️ No se generó el Excel con resultados de prueba en la carpeta 'reports/'. Revisa tu script de prueba.")

    service = conectar_google_drive()
    folder_id = obtener_id_carpeta_drive("SABRINA_QA_Reports", service)

    subir_a_drive(ruta_html_destino, folder_id, service)
    subir_a_drive(ruta_excel_destino, folder_id, service)

    actualizar_resumen_excel()


if __name__ == "__main__":
    print("--- Iniciando Suite de Automatización QA ---")
    asegurar_dependencias()
    ejecutar_suite()
    print("--- Suite de Automatización QA Finalizada ---")
