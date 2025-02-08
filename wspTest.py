from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurar Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Asistencia Vendedores").worksheet("test1")

# Configurar Selenium
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")
time.sleep(30)  # Tiempo para escanear el código QR en WhatsApp Web

wait = WebDriverWait(driver, 20)  # Ajuste del tiempo de espera

def leer_mensajes(grupo):
    try:
        print(f"Intentando leer mensajes del grupo: {grupo}")
        
        # Verificar si WhatsApp Web está cargado correctamente
        print(f"URL actual del driver: {driver.current_url}")
        
        # Verifica la presencia del cuadro de búsqueda
        try:
            search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='3']")))
            print("Cuadro de búsqueda encontrado.")
        except Exception as e:
            print(f"No se encontró el cuadro de búsqueda: {e}")
            return  # Salimos si el cuadro de búsqueda no se encuentra

        # Usar el cuadro de búsqueda para encontrar el grupo
        search_box.clear()
        search_box.send_keys(grupo)
        search_box.send_keys(Keys.ENTER)
        time.sleep(3)
        print(f"Grupo '{grupo}' buscado y seleccionado.")

        # Encuentra los últimos 5 mensajes entrantes
        mensajes = driver.find_elements(By.XPATH, "//div[contains(@class, '_amk6')]")[-5:]
        print(f"Número de mensajes encontrados: {len(mensajes)}")

        for mensaje in mensajes:
            try:
                print("Procesando mensaje...")

                # Selector para el número o nombre
                numero_element = mensaje.find_element(By.CSS_SELECTOR, "div._ahy1.copyable-text")
                numero_texto_completo = numero_element.get_attribute('data-pre-plain-text') if numero_element else ""
                numero = numero_texto_completo.split("] ", 1)[1].split(": ", 1)[0] if "] " in numero_texto_completo else numero_texto_completo
                print(f"Número encontrado: {numero}")

                # Selector para el texto del mensaje
                texto_element = mensaje.find_element(By.CSS_SELECTOR, "span._ao3e.selectable-text.copyable-text span")
                texto = texto_element.text if texto_element else ""
                print(f"Texto del mensaje encontrado: {texto}")

                # Selector para la hora
                hora_element = mensaje.find_element(By.CSS_SELECTOR, "span.x1c4vz4f.x2lah0s")
                hora = hora_element.text if hora_element else ""
                print(f"Hora del mensaje encontrada: {hora}")

                # Procesar tipo y ubicación
                tipo, ubicacion = "", ""
                if "confirmo asistencia" in texto.lower():
                    tipo = "Asistencia"
                    ubicacion = texto.lower().split("confirmo asistencia")[-1].strip()
                elif "confirmo salida" in texto.lower():
                    tipo = "Salida"
                    ubicacion = texto.lower().split("confirmo salida")[-1].strip()
                print(f"Tipo: {tipo}, Ubicación: {ubicacion}")

                # Guardar en Google Sheets
                if tipo:
                    sheet.append_row([numero, texto, tipo, ubicacion, hora])
                    print(f"Registro guardado: {numero}, {texto}, {tipo}, {ubicacion}, {hora}")
            except Exception as e_mensaje:
                print(f"Error procesando mensaje: {e_mensaje}")

    except Exception as e_grupo:
        print(f"Error al leer el grupo: {e_grupo}")
        print(f"URL actual del driver: {driver.current_url}")

        # Capturar el HTML completo para depuración
        with open("error_grupo.html", "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        print("HTML guardado para análisis.")

# Bucle principal
while True:
    leer_mensajes("wspTest")  # Usa el nombre exacto del grupo
    time.sleep(60)  # Revisa cada minuto


