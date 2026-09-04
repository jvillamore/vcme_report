#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
PYTHON="$VENV_DIR/bin/python"

usage() {
    printf 'Uso: %s {download|summary|all} [opciones]\n' "$(basename "$0")"
    printf '\nComandos:\n'
    printf '  download  Descarga el CSV maestro\n'
    printf '  summary   Genera el resumen por entidad\n'
    printf '  all       Ejecuta ambos pasos con las opciones predeterminadas\n'
}

if [[ ! -x "$PYTHON" ]]; then
    printf 'Creando entorno virtual en %s\n' "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

"$PYTHON" -m pip install -r "$ROOT_DIR/requirements.txt"

command="${1:-}"
if [[ $# -gt 0 ]]; then
    shift
fi

case "$command" in
    download)
        exec "$PYTHON" "$ROOT_DIR/fetch_tramites_maestro.py" "$@"
        ;;
    summary)
        exec "$PYTHON" "$ROOT_DIR/resumen_tramites_por_entidad.py" "$@"
        ;;
    all)
        if [[ $# -gt 0 ]]; then
            printf 'El comando all no acepta opciones; usa download o summary.\n' >&2
            exit 2
        fi
        "$PYTHON" "$ROOT_DIR/fetch_tramites_maestro.py"
        exec "$PYTHON" "$ROOT_DIR/resumen_tramites_por_entidad.py"
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac