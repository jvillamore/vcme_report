import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def resolve_entidad(value):
    if value is None:
        return None

    if isinstance(value, dict):
        for key in ("nombre", "entidad", "sigla", "id"):
            if key in value and value[key] not in (None, ""):
                return str(value[key])
        return str(value)

    if isinstance(value, list):
        for item in value:
            resolved = resolve_entidad(item)
            if resolved not in (None, ""):
                return resolved
        return None

    if isinstance(value, str):
        value = value.strip()
        if value.startswith("{") or value.startswith("["):
            try:
                parsed = json.loads(value)
                return resolve_entidad(parsed)
            except (TypeError, ValueError):
                pass

    return str(value)


def resolve_estado(value):
    if value is None:
        return None

    if isinstance(value, dict):
        for key in ("nombre", "estado", "descripcion", "id"):
            if key in value and value[key] not in (None, ""):
                return str(value[key])
        return str(value)

    if isinstance(value, list):
        for item in value:
            resolved = resolve_estado(item)
            if resolved not in (None, ""):
                return resolved
        return None

    if isinstance(value, str):
        value = value.strip()
        if value.startswith("{") or value.startswith("["):
            try:
                parsed = json.loads(value)
                return resolve_estado(parsed)
            except (TypeError, ValueError):
                pass

    return str(value)


def resumen_por_entidad(input_path: str, output_path: str, field_name: str, estado_field: str = "estadoFlujo"):
    counts = defaultdict(Counter)
    state_names = set()

    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            entidad_value = row.get(field_name)
            entidad = resolve_entidad(entidad_value)
            if not entidad or entidad == "None":
                continue

            estado_value = row.get(estado_field)
            estado = resolve_estado(estado_value)
            if not estado or estado == "None":
                estado = "SIN_ESTADO"

            state_names.add(estado)
            counts[entidad][estado] += 1

    ordered_states = sorted(state_names)

    with output_file.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["entidad", *ordered_states])
        for entidad in sorted(counts.keys()):
            row = [entidad]
            for estado in ordered_states:
                row.append(counts[entidad].get(estado, 0))
            writer.writerow(row)

    print(
        f"Resumen generado: {output_file} | {len(counts)} entidades | {len(ordered_states)} estados")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera un resumen de tramites por entidad y estadoFlujo")
    parser.add_argument(
        "--input", default="results/tramites_maestro.csv", help="Archivo CSV maestro")
    parser.add_argument(
        "--output", default="results/tramites_por_entidad.csv", help="Archivo CSV resumen")
    parser.add_argument(
        "--field",
        default="entidad",
        help="Nombre del campo que identifica la entidad. Prueba: entidad, nombre_entidad, id_entidad",
    )
    parser.add_argument(
        "--estado-field",
        default="estadoFlujo",
        help="Nombre del campo que identifica el estado del flujo del trámite",
    )
    args = parser.parse_args()

    resumen_por_entidad(args.input, args.output, args.field, args.estado_field)
