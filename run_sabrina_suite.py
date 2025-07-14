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


def asegurar_dependencias():
    for pkg in ["pytest", "pytest-html"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Instalando módulo: {pkg}")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg])


def conectar_google_drive():
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def obtener_id_carpeta_drive(nombre_carpeta, service):
    query = f"name='{nombre_carpeta}' and mimeType='application/vnd.google-apps.folder'"
    resultado = service.files().list(q=query, fields="files(id)").execute()
    if resultado["files"]:
        return resultado["files"][0]["id"]
    metadata = {"name": nombre_carpeta,
                "mimeType": "application/vnd.google-apps.folder"}
    carpeta = service.files().create(body=metadata, fields="id").execute()
    return carpeta["id"]


def subir_a_drive(ruta, folder_id, service):
    if not os.path.exists(ruta):
        print(f"❌ Archivo no encontrado, se omite subida: {ruta}")
        return
    metadata = {"name": os.path.basename(ruta), "parents": [folder_id]}
    media = MediaFileUpload(ruta)
    archivo = service.files().create(
        body=metadata, media_body=media, fields='id').execute()
    print(f"📤 Subido: {os.path.basename(ruta)} (ID: {archivo['id']})")


def actualizar_resumen_excel():
    nombre_json = "resumen_busquedas.json"
    nombre_excel = "resumen_QA.xlsx"

    if not os.path.exists(nombre_json):
        print("⚠️ No se encontró resumen_busquedas.json, se omite actualización del resumen QA.")
        return

    try:
        with open(nombre_json, "r", encoding="utf-8") as f:
            resumen = json.load(f)
    except Exception as e:
        print(f"❌ Error al leer el JSON: {e}")
        return

    fecha = resumen.get("fecha", "desconocida")
    resultados = resumen.get("resultados", {})
    total_busquedas = sum(resultados.values())
    terminos = ", ".join(resultados.keys()) if resultados else "(sin datos)"

    ruta_html = f"resultados_{fecha}/reporte_SABRINA_{fecha}.html"
    ruta_excel = f"resultados_{fecha}/busquedas_google_SABRINA_{fecha}.xlsx"
    estado_html = "✅" if os.path.exists(ruta_html) else "❌"
    estado_excel = "✅" if os.path.exists(ruta_excel) else "❌"
    estado_final = "Completado" if estado_html == "✅" and estado_excel == "✅" else "Parcial"

    if os.path.exists(nombre_excel):
        wb = openpyxl.load_workbook(nombre_excel)
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
    wb.save(nombre_excel)

    print("\n📈 Resumen QA actualizado en 'resumen_QA.xlsx'")
    print("🗓️ Fecha:", fecha)
    print(f"🔍 Términos procesados ({len(resultados)}):")
    for termino, cantidad in resultados.items():
        print(f"   - {termino}: {cantidad} resultados")
    print(
        f"\n📄 Reporte HTML: {estado_html}    📊 Excel: {estado_excel}    🧪 Estado final: {estado_final}")


def ejecutar_suite():
    fecha = datetime.now().strftime("%Y-%m-%d")
    carpeta_local = f"resultados_{fecha}"
    os.makedirs(carpeta_local, exist_ok=True)

    nombre_html = f"reporte_SABRINA_{fecha}.html"
    nombre_excel = f"busquedas_google_SABRINA_{fecha}.xlsx"
    ruta_html = os.path.join(carpeta_local, nombre_html)
    ruta_excel = os.path.join(carpeta_local, nombre_excel)

    print("🚀 Ejecutando pruebas...")
    subprocess.run([
        sys.executable, "-m", "pytest",
        "test_google_reporte_hml.py",
        "--html", ruta_html,
        "--self-contained-html",
        "-s"
    ])

    if os.path.exists(nombre_excel):
        shutil.move(nombre_excel, ruta_excel)
        print(f"📊 Excel guardado en: {ruta_excel}")
    else:
        print("⚠️ No se generó el Excel. Revisa si hay errores en tu script de prueba.")

    service = conectar_google_drive()
    folder_id = obtener_id_carpeta_drive("SABRINA_QA_Reports", service)
    subir_a_drive(ruta_html, folder_id, service)
    subir_a_drive(ruta_excel, folder_id, service)

    actualizar_resumen_excel()


if __name__ == "__main__":
    asegurar_dependencias()
    ejecutar_suite()
