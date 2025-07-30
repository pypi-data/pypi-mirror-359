from dashgen.core.builder import Dashboard
from dashgen.core.layout import Row, Column
import json
import asyncio
from pathlib import Path


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


async def dummy_render_html_to_image(html, output_path, width, height):
    Path(output_path).write_text("done")


def test_generate_inside_running_loop(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "dashgen.core.builder.render_html_to_image", dummy_render_html_to_image
    )

    async def run():
        db = Dashboard()
        db.add(Row(Column(12).add_text("x")))
        out = tmp_path / "out.png"
        db.generate(out)
        assert out.exists()

    asyncio.run(run())

