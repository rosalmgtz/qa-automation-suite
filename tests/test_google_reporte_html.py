import pytest
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime
import time
import re
import os

# --- CONFIGURACIÓN INICIAL Y RUTAS ---
fecha_actual = datetime.now().strftime("%Y-%m-%d")

reports_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..', 'reports')
os.makedirs(reports_dir, exist_ok=True)

nombre_excel_final = os.path.join(
    reports_dir, f"busquedas_google_SABRINA_{fecha_actual}.xlsx")

wb = Workbook()
ws_resumen = wb.active
ws_resumen.title = "Resumen"
ws_resumen.append(["Término", "Título", "Enlace"])

busquedas = [
    "automatización de pruebas con IA",
    "herramientas de testing con Selenium",
    "evitar CAPTCHA en Selenium"
]
# --- FIN CONFIGURACIÓN INICIAL Y RUTAS ---


def limpiar(texto):
    texto = re.sub(r'[^\x00-\x7F]+', '', texto)
    return texto.strip()


def aplicar_estilos(ws):
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4F81BD",
                                end_color="4F81BD", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")

    for i, row in enumerate(ws.iter_rows(min_row=2), start=2):
        fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7",
                           fill_type="solid") if i % 2 == 0 else None
        for cell in row:
            if fill:
                cell.fill = fill

    for col in ws.columns:
        max_length = 0
        column = []
        for cell in col:
            column.append(str(cell.value))
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        adjusted_width = (max_length + 2)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = adjusted_width


@pytest.fixture(scope="module")
def driver():
    headless_mode = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
    print(f"🟢 Iniciando navegador stealth (headless={headless_mode})...")

    # Configuración de opciones de Chrome para mayor robustez en CI
    options = uc.ChromeOptions()
    # Necesario para entornos Linux como GitHub Actions
    options.add_argument('--no-sandbox')
    # Previene problemas de memoria en CI
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # Recomendado para headless
    # Asegura un tamaño de ventana consistente
    options.add_argument('--window-size=1920,1080')

    d = uc.Chrome(headless=headless_mode, use_subprocess=True, options=options)
    d.maximize_window()
    yield d

    try:
        d.quit()
    except Exception as e:
        print(f"⚠️ Error al cerrar el navegador: {e}")
    print("🛑 Navegador cerrado.")


def pytest_configure(config):
    config._metadata["Autor"] = "SABRINA"
    config._metadata["Proyecto"] = "Scraping con Selenium"
    config._metadata["Fecha"] = fecha_actual
    config._metadata["Ubicación"] = "Buenavista, México"


@pytest.mark.parametrize("query", busquedas)
def test_busqueda_google(driver, query):
    print(f"\n🔎 Buscando: {query}")
    driver.get("https://www.google.com")

    # Aumentar tiempo de espera para el campo de búsqueda
    WebDriverWait(driver, 15).until(  # Aumentado a 15 segundos
        EC.presence_of_element_located((By.NAME, "q"))
    )

    # Consentimiento de cookies / CAPTCHA bypass básico
    try:
        # Intenta aceptar cookies buscando botones comunes
        aceptar_button = WebDriverWait(driver, 10).until(  # Aumentado a 10 segundos
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Aceptar')] | //button[contains(., 'I agree')] | //button[contains(., 'Accept all')]"))
        )
        aceptar_button.click()
        print("🍪 Botón de aceptar cookies clickeado.")
        time.sleep(3)  # Un poco más de tiempo después de clickear
    except:
        # Si no encuentra el botón o falla, intentar cerrar modales con JS
        try:
            driver.execute_script(
                "document.querySelectorAll('iframe, dialog, [aria-modal=\"true\"], [role=\"dialog\"]').forEach(e => e.remove());"
            )
            print("👁️ Modales/iframes removidos con JavaScript.")
            time.sleep(2)
        except:
            print("🚫 No se encontró botón de aceptar cookies ni modales para remover.")
            pass

    caja = driver.find_element(By.NAME, "q")
    caja.send_keys(query)
    caja.send_keys(Keys.RETURN)

    # Aumentar tiempo de espera para los resultados de búsqueda
    WebDriverWait(driver, 15).until(  # Aumentado a 15 segundos
        EC.presence_of_element_located((By.ID, "search"))
    )
    time.sleep(5)  # Un tiempo extra para que la página cargue completamente

    bloques = driver.find_elements(
        By.CSS_SELECTOR, "div#search .tF2Cxc, div.g")

    if len(bloques) == 0:
        print(
            f"⚠️ No se encontraron bloques de resultados estándar para '{query}'. Reintentando con selectores alternativos.")
        # Podrías añadir aquí otra capa de lógica o reintentos si es necesario

    assert len(
        bloques) > 0, f"No se encontraron resultados visibles para '{query}' después de la búsqueda."

    ws = wb.create_sheet(title=query[:31])
    ws.append(["Título", "Enlace"])
    count = 0

    for bloque in bloques:
        try:
            titulo_elem = bloque.find_element(By.TAG_NAME, "h3")
            enlace_elem = bloque.find_element(By.TAG_NAME, "a")

            titulo = limpiar(titulo_elem.text)
            enlace = enlace_elem.get_attribute("href").strip()

            if len(titulo) > 5 and enlace and enlace.startswith("http"):
                ws.append([titulo, enlace])
                ws_resumen.append([query, titulo, enlace])
                count += 1
            if count >= 5:
                break
        except Exception as e:
            # print(f"🚫 Error al procesar bloque de resultado: {e}")
            continue

    aplicar_estilos(ws)
    print(f"📋 {count} resultados guardados en hoja: '{query}'")


def pytest_sessionfinish(session, exitstatus):
    if "Sheet" in wb.sheetnames and wb["Sheet"].max_row == 0:
        del wb["Sheet"]

    aplicar_estilos(ws_resumen)

    wb.save(nombre_excel_final)
    print(f"\n✅ Archivo Excel generado: {nombre_excel_final}")
