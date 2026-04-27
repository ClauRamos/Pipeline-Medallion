# Flujo del pipeline paso a paso

# Paso 1 — Ingesta (Bronze)

`ingesta/ingesta_gateguay.py` se conecta a la FakeStore API, descarga el catálogo de productos y lo guarda como archivo JSON con partición de fecha:

```
ventas_raw_2026-01-03.json
```

Ese archivo se sube manualmente (o via job) a Databricks como tabla Delta Bronze.

# Paso 2 — Transformación Silver

Desde el notebook Databricks, se lee la tabla Bronze y se aplican las siguientes transformaciones:

| Campo original | Campo Silver | Transformación |
|---|---|---|
| `id` | `producto_id` | rename |
| `title` | `nombre_producto` | rename |
| `category` | `categoria` | rename |
| `price` | `precio` | rename |
| `rating.rate` | `puntuacion_promedio` | **desanidado** del struct `rating` |
| `rating.count` | `cantidad_votos` | **desanidado** del struct `rating` |
| *(nuevo)* | `fecha_ingesta` | `current_timestamp()` |

La columna `image` y `description` se descartan por no ser relevantes para el análisis.

Tabla resultante: `default.dim_productos_silver`

### Paso 3 — Transformación Gold

Agrupación por `categoria` para obtener métricas de negocio:

| categoria | total_productos | precio_promedio_usd |
|---|---|---|
| electronics | 6 | 332.50 |
| jewelery | 4 | 221.00 |
| men's clothing | 4 | 51.06 |
| women's clothing | 6 | 26.29 |

Tabla resultante: `default.reporte_ventas_gold`

---

# Cómo reproducir el proyecto

# Pre-requisitos

- Python 3.8+
- Cuenta en [Databricks Community Edition](https://community.cloud.databricks.com/) (gratuita)
- Acceso a internet (para consumir la FakeStore API)

### 1. Clonar el repositorio

```bash
git clone https://github.com/ClauRamos/fakestore-medallion-pipeline.git
cd fakestore-medallion-pipeline
```

### 2. Instalar dependencias locales

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la ingesta

```bash
python ingesta/ingesta_gateguay.py
```

Esto genera el archivo `ventas_raw_{fecha}.json` en el directorio actual.

### 4. Subir el JSON a Databricks

En Databricks Community Edition:

1. Ir a **Catalog → Create table → Upload file**
2. Subir el archivo `ventas_raw_{fecha}.json`
3. Databricks lo registrará como tabla `default.ventas_raw_{fecha}` (con guiones bajos)

### 5. Ejecutar el notebook

1. Importar `notebooks/transformacion_medallion.ipynb` en Databricks
2. Conectar a un cluster (DBR 13+ recomendado)
3. Ejecutar todas las celdas en orden

Las tablas Delta `dim_productos_silver` y `reporte_ventas_gold` quedarán disponibles en el catálogo `default`.

---

# Stack tecnológico

| Herramienta | Uso |
|---|---|
| Python 3 | Script de ingesta local |
| `requests` | Consumo de la API REST |
| Apache Spark / PySpark | Transformaciones distribuidas |
| Delta Lake | Formato de almacenamiento de tablas |
| Databricks | Plataforma de ejecución del notebook |
| FakeStore API | Fuente de datos simulada de e-commerce |

---

# Decisiones de diseño

- **Partición por fecha**: el nombre del archivo JSON incluye la fecha de ejecución (`ventas_raw_YYYY-MM-DD.json`), lo que permite futuros procesamientos incrementales.
- **Desanidado del struct `rating`**: en Bronze, el campo `rating` es un struct con subcampos `rate` y `count`. En Silver se aplana con `col("rating.rate")` para facilitar las agregaciones.
- **Timestamp de ingesta**: se agrega `current_timestamp()` en Silver para trazabilidad y auditoría del dato.
- **Capa Gold orientada al negocio**: la tabla Gold responde preguntas de negocio concretas (¿qué categoría tiene el precio promedio más alto?) sin exponer complejidad técnica.

---

# Posibles mejoras

- [ ] Automatizar la ingesta con **Databricks Jobs** o **Apache Airflow**
- [ ] Agregar validaciones de calidad de datos con **Great Expectations**
- [ ] Parametrizar la fecha de ingesta como widget de Databricks
- [ ] Agregar capa de visualización con **Power BI** conectado a Delta Lake
- [ ] Implementar escritura incremental con `MERGE INTO` en lugar de `overwrite`

---



**Claudia Ramos** — Junior Data Engineer  
[GitHub](https://github.com/ClauRamos) · [LinkedIn](https://linkedin.com/in/claudia-ramos)
