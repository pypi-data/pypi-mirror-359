import base64
from dashgen.core.components import (
    render_box,
    render_text,
    render_image,
    render_progress_bar,
)


def test_render_box_defaults():
    html = render_box("content")
    assert "border" in html
    assert "p-4" in html
    assert "bg-white" in html
    assert "content" in html


def test_render_text_styles():
    html = render_text(
        "hello",
        style={"size": "text-2xl", "weight": "bold", "color": "text-red-500", "align": "center"},
    )
    assert "text-2xl" in html
    assert "font-bold" in html
    assert "text-red-500" in html
    assert "text-center" in html


def test_render_image_base64(tmp_path):
    img = tmp_path / "x.bin"
    img.write_bytes(b"img")
    html = render_image(str(img), style={"width": "10px"})
    b64 = base64.b64encode(b"img").decode()
    assert b64 in html
    assert "width:10px" in html


def test_render_progress_bar_clamp():
    html = render_progress_bar(120, style={"bar_color": "bg-blue-500"})
    assert "bg-blue-500" in html
    assert "width:100%" in html

