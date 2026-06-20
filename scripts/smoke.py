#!/usr/bin/env python3
"""
smoke.py — verificación rápida (en vivo) de la instalación y del skill.

Corre con `python3 scripts/smoke.py` — solo usa la librería estándar, así que
funciona ANTES de instalar nada más. Llama al skill `colombia-open-data` contra
datos.gov.co y reporta PASS/FAIL. Úsalo después de instalar para confirmar que
todo funciona en TU máquina (y que tienes conexión a internet).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skill" / "colombia-open-data" / "scripts" / "cli.py"

OK, BAD = "✅", "❌"


def run(label: str, args: list[str]) -> bool:
    print(f"… {label}")
    try:
        proc = subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as exc:  # network down, python missing, etc.
        print(f"  {BAD} no se pudo ejecutar: {exc}")
        return False
    if proc.returncode != 0:
        tail = (proc.stderr.strip().splitlines() or [""])[-1]
        print(f"  {BAD} código de salida {proc.returncode}: {tail}")
        return False
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(f"  {BAD} la salida no es JSON válido")
        return False
    n = len(data) if isinstance(data, list) else 1
    print(f"  {OK} {n} resultado(s)")
    return True


def check_deps() -> None:
    print("\nDependencias de la capa de procesamiento (opcionales para el skill):")
    for mod in ("pandas", "dagster", "vcr"):
        try:
            __import__(mod)
            print(f"  {OK} {mod}")
        except ImportError:
            print(f"  ·  {mod} no instalado  (instala con: pip install -r pipeline/requirements.txt)")


def main() -> int:
    print(f"Python {sys.version.split()[0]}  ·  {CLI.relative_to(ROOT)}\n")
    if sys.version_info < (3, 10):
        print(f"{BAD} Se requiere Python 3.10 o superior.")
        return 1

    results = [
        run("buscar datasets (search)",
            ["search", "internet por departamento", "--limit", "3"]),
        run("leer columnas (schema)",
            ["schema", "n48w-gutb"]),
        run("consulta agregada (query)",
            ["query", "n48w-gutb",
             "--select", "anno,sum(no_de_accesos::number) as accesos",
             "--group", "anno", "--order", "anno"]),
    ]

    check_deps()

    ok = all(results)
    print("\n" + (
        "🎉 Todo en orden — el skill funciona en vivo."
        if ok else
        "⚠ Hubo fallas (mira arriba). ¿Tienes conexión a internet?"
    ))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
