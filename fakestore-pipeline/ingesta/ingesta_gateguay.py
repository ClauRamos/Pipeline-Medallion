import requests
import json
import datetime

# ── Configuración ─────────────────────────────────────────────
API_URL = "https://fakestoreapi.com/products"

# ── Paso 1: Conectar a la API y descargar datos ────────────────
print("🛒 Conectando con FakeStore API...")
response = requests.get(API_URL)

# Verificamos que la petición fue exitosa (código HTTP 200)
response.raise_for_status()

data = response.json()
print(f"✅ {len(data)} productos descargados correctamente.")

# ── Paso 2: Guardar con partición de fecha ─────────────────────
# El nombre incluye la fecha para facilitar procesamientos incrementales
fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
nombre_archivo = f"ventas_raw_{fecha_hoy}.json"

with open(nombre_archivo, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"💾 Archivo guardado: '{nombre_archivo}'")
print("📤 Siguiente paso: subir este archivo a Databricks como tabla Bronze.")
