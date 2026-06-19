"""
dane.py — heuristic guard: is this request really DANE microdata (out of scope)?

Most DANE microdata (census/CNPV unit records, GEIH, ECV, ENUT, ...) lives on
DANE's own portal / ANDA, NOT on the Socrata portal datos.gov.co. When a request
is really DANE microdata, the Skill must BAIL cleanly instead of faking it or
returning junk.

>>> is_probably_dane("necesito los microdatos de la GEIH 2022")[0]
True
>>> is_probably_dane("accesos a internet por departamento")[0]
False

This module is the single "bail" location the GitHub issue
"Agregar soporte para DANE al skill de adquisición" points students at.
"""
from __future__ import annotations

import unicodedata

# Strong indicators of DANE *microdata* (unit-level survey/census records).
# IMPORTANT: plain "censo" or "dane" is deliberately NOT enough — aggregated
# census tables and many DANE-sourced datasets ARE published on datos.gov.co
# (e.g. "POBLACION CENSO NACIONAL 2018 POR CENTRO POBLADO"). We only bail on
# signals that specifically point at microdata or DANE's own catalogs.
MICRODATA_TERMS = [
    "microdato", "microdata",
    "anda",  # Archivo Nacional de Datos — DANE's microdata catalog
    "geih", "gran encuesta integrada de hogares",
    "ech", "encuesta continua de hogares",
    "ecv", "encuesta de calidad de vida",
    "enut", "encuesta nacional de uso del tiempo",
    "enph", "encuesta nacional de presupuestos de los hogares",
    "cnpv", "censo nacional de poblacion y vivienda",
    "registro a nivel de persona", "datos a nivel de persona",
    "datos a nivel de hogar", "unidad de observacion", "anonimizado",
]

BAIL_MESSAGE = (
    "Este skill cubre datos.gov.co (Socrata). Lo que pides parece ser MICRODATOS "
    "del DANE, que viven en el portal propio del DANE / ANDA y no en Socrata.\n"
    "Por ahora está fuera de alcance: usa Claude normal u otra herramienta para "
    "los microdatos del DANE.\n"
    "Hay un issue abierto para agregar soporte de DANE: busca "
    "\"Agregar soporte para DANE\" en el repositorio."
)


def _strip_accents(text):
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )


def is_probably_dane(text):
    """Return (is_dane: bool, reason: str). Accent- and case-insensitive."""
    norm = _strip_accents((text or "").lower())
    for term in MICRODATA_TERMS:
        if _strip_accents(term) in norm:
            return True, f"coincide con indicador de microdatos DANE: '{term}'"
    return False, ""
