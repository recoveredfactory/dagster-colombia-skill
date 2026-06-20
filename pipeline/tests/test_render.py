"""Tests for the skill's HTML renderer (render.py) — pure, offline."""
import render


def test_to_number_handles_socrata_text():
    assert render.to_number("2251960") == 2251960
    assert render.to_number("1.5") == 1.5
    assert render.to_number("") is None
    assert render.to_number(None) is None
    assert render.to_number("n/a") is None


def test_format_number_colombian_thousands():
    assert render.format_number(2251960) == "2.251.960"
    assert render.format_number(0) == "0"


def test_bar_chart_html_sorts_scales_and_drops_non_numeric():
    rows = [
        {"dep": "Aaa", "v": "100"},
        {"dep": "Bbb", "v": "200"},
        {"dep": "Ccc", "v": "n/a"},  # non-numeric -> dropped from the chart
    ]
    html = render.bar_chart_html(rows, label_key="dep", value_key="v",
                                 title="T", source="src")
    body = html.split("<table>")[1].split("</table>")[0]
    assert body.index(">Bbb<") < body.index(">Aaa<")  # largest first
    assert ">Ccc<" not in body                         # non-numeric dropped
    assert "width:100.0%" in body                      # Bbb is the max
    assert "width:50.0%" in body                       # Aaa is half of Bbb
    assert html.startswith("<!doctype html>")
    assert "src" in html                               # source shows in the footer
