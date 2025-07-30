from dashgen.core.builder import Dashboard
from dashgen.core.layout import Row, Column
import json


def test_generate_page_resets_components():
    db = Dashboard()
    db.add(Row(Column(12).add_text("x")))
    db.generate_page()
    assert len(db.pages) == 1
    assert db.components == []


def test_save_and_load_theme(tmp_path):
    theme = {"primary": "#fff", "accent": "#000"}
    file = tmp_path / "theme.json"
    db = Dashboard(theme=theme)
    db.save_theme(file)
    db2 = Dashboard()
    db2.load_theme(file)
    assert db2.theme == theme

