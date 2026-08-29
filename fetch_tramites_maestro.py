import argparse
import csv
import json
import math
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()


def get_api_base() -> str:
    base = os.getenv("API_BASE")
    if not base:
        raise ValueError("Falta API_BASE en el archivo .env")
    return base.rstrip("/")


def get_api_token() -> str:
    token = os.getenv("API_TOKEN")
    if not token:
        raise ValueError("Falta API_TOKEN en el archivo .env")
    return token


def fetch_page(api_base: str, api_token: str, page: int, limit: int):
    params = {"pagina": page, "limite": limit}
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }

    response = requests.get(api_base, params=params,
                            headers=headers, timeout=60)
    response.raise_for_status()

    try:
        return response.json()
    except ValueError as exc:
        raise ValueError(
            f"La respuesta no es JSON válido para la página {page}: {response.text[:300]}") from exc


def extract_items(payload):
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        return []

    for key in ("datos", "data", "results", "items", "tramites", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for nested_key in ("filas", "data", "results", "items", "tramites", "records"):
                nested_value = value.get(nested_key)
                if isinstance(nested_value, list):
                    return nested_value

    return []


def extract_total_pages(payload, limit: int):
    if not isinstance(payload, dict):
        return None

    datos = payload.get("datos")
    if isinstance(datos, dict):
        total = datos.get("total")
        if total is not None:
            try:
                return math.ceil(int(total) / limit)
            except (TypeError, ValueError):
                pass

    for key in (
        "total_pages",
        "totalPages",
        "total_paginas",
        "totalPaginas",
        "pages",
        "last_page",
        "lastPage",
        "total",
    ):
        value = payload.get(key)
        if value is None and isinstance(datos, dict):
            value = datos.get(key)
        if value is not None:
            try:
                return math.ceil(int(value) / limit)
            except (TypeError, ValueError):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    continue
    return None


def normalize_csv_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def write_maestro_csv(rows, output_path: str):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = []

    for row in rows:
        if isinstance(row, dict):
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)

    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, extrasaction="ignore")
        if fieldnames:
            writer.writeheader()
            for row in rows:
                if isinstance(row, dict):
                    writer.writerow({key: normalize_csv_value(value)
                                    for key, value in row.items()})

    print(f"Se guardaron {len(rows)} registros en {output_file}")


def fetch_all_pages(output_path: str, limit: int = 50, start_page: int = 1):
    api_base = get_api_base()
    api_token = get_api_token()

    rows = []
    page = start_page

    while True:
        payload = fetch_page(api_base, api_token, page, limit)
        items = extract_items(payload)

        if not items:
            break

        rows.extend(items)

        total_pages = extract_total_pages(payload, limit)
        if total_pages is not None:
            if page >= total_pages:
                break
        elif len(items) < limit:
            break

        page += 1

    write_maestro_csv(rows, output_path)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Descarga todas las páginas de tramites y las guarda en CSV")
    parser.add_argument("--output", default="results/tramites_maestro.csv",
                        help="Ruta del archivo CSV maestro")
    parser.add_argument("--limit", type=int, default=50,
                        help="Cantidad de registros por página")
    parser.add_argument("--start-page", type=int,
                        default=1, help="Página inicial")
    args = parser.parse_args()

    fetch_all_pages(args.output, limit=args.limit, start_page=args.start_page)
