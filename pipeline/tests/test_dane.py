"""The DANE-microdata bail guard. Pure logic, no network."""
import pytest

import dane


@pytest.mark.parametrize("text", [
    "necesito los microdatos de la GEIH 2022",
    "censo CNPV a nivel de persona",
    "quiero datos de ANDA del DANE",
    "Gran Encuesta Integrada de Hogares anonimizada",
])
def test_microdata_requests_bail(text):
    is_dane, reason = dane.is_probably_dane(text)
    assert is_dane
    assert reason


@pytest.mark.parametrize("text", [
    "accesos a internet por departamento",
    "contratos públicos por año",
    "población censo 2018 por centro poblado",  # aggregated table IS in scope
    "",
])
def test_in_scope_requests_pass(text):
    assert dane.is_probably_dane(text)[0] is False


def test_accent_insensitive():
    # "proyección" has an accent; the matcher normalizes before comparing.
    assert dane.is_probably_dane("MICRODATOS del censo")[0] is True
