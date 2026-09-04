# Reporte de trámites

Proyecto de Python para descargar trámites desde una API paginada y generar un resumen por entidad y estado del flujo.

## Flujo

1. `fetch_tramites_maestro.py` consulta todas las páginas de la API y guarda los registros en `results/tramites_maestro.csv`.
2. `resumen_tramites_por_entidad.py` lee el CSV maestro y genera `results/tramites_por_entidad.csv`, con una fila por entidad y una columna por estado.

## Requisitos

- Python 3.9 o superior
- Acceso a la API de trámites
- URL base y token de autenticación

Instala las dependencias con:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

También puedes dejar que el lanzador cree y use `.venv` automáticamente:

```bash
./run.sh summary
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```dotenv
API_BASE=https://ejemplo.gob/api/tramites
API_TOKEN=tu_token
```

`API_BASE` es la URL que recibe los parámetros `pagina` y `limite`. El token se envía como `Authorization: Bearer <token>`.

No incluyas `.env` ni tokens reales en el repositorio.

## Uso

Descarga todos los trámites:

```bash
./run.sh download
```

Opciones disponibles:

```bash
./run.sh download \
  --output results/tramites_maestro.csv \
  --limit 50 \
  --start-page 1
```

- `--output`: ruta del CSV maestro. Por defecto, `results/tramites_maestro.csv`.
- `--limit`: cantidad de registros solicitados por página. Por defecto, `50`.
- `--start-page`: página inicial. Por defecto, `1`.

Genera el resumen por entidad. Si el CSV maestro no existe, se descarga automáticamente antes de generar el resumen:

```bash
./run.sh summary
```

Para adaptar los nombres de campos del CSV:

```bash
./run.sh summary \
  --input results/tramites_maestro.csv \
  --output results/tramites_por_entidad.csv \
  --field entidad \
  --estado-field estadoFlujo
```

- `--input`: CSV de entrada.
- `--output`: CSV de salida.
- `--field`: campo que identifica la entidad. Por defecto, `entidad`.
- `--estado-field`: campo que identifica el estado. Por defecto, `estadoFlujo`.

Para ejecutar el flujo completo con los valores predeterminados:

```bash
./run.sh all
```

El lanzador crea `.venv` si no existe, instala las dependencias y ejecuta los scripts con el Python del entorno virtual. También permite indicar otra ubicación mediante `VENV_DIR`:

```bash
VENV_DIR=/ruta/a/mi-venv ./run.sh summary
```

## Formato de la API

El descargador acepta una respuesta JSON que sea directamente una lista o que contenga los registros bajo claves habituales como `datos`, `data`, `results`, `items`, `tramites` o `records`. También reconoce metadatos de paginación como `total_pages`, `totalPages`, `total_paginas`, `totalPaginas`, `pages`, `last_page`, `lastPage` y `total`.

La descarga termina cuando se alcanza el total de páginas informado o cuando una página devuelve menos registros que el límite solicitado. Las respuestas no JSON y los errores HTTP detienen la ejecución.

## Archivos generados

- `results/tramites_maestro.csv`: conserva las columnas encontradas en los registros descargados. Los valores anidados se serializan como JSON dentro de la celda.
- `results/tramites_por_entidad.csv`: contiene `entidad` y una columna por cada estado encontrado. Los estados ausentes para una entidad se representan con `0`; los trámites sin estado se agrupan como `SIN_ESTADO`.

La carpeta de salida se crea automáticamente cuando no existe.

## Limitaciones conocidas

- El proyecto no incluye pruebas automatizadas ni reintentos para fallos temporales de red.
- El campo de entidad y el campo de estado deben coincidir con los nombres de las columnas del CSV.
- Las credenciales se cargan desde variables de entorno mediante `python-dotenv`.