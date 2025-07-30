from dashgen.core.layout import Row, Column


def test_column_breakpoints_and_order():
    col = Column(6, order=2, breakpoints={"md": 4}).add_text("x")
    html = col.render()
    assert "col-span-6" in html
    assert "md:col-span-4" in html
    assert "order-2" in html


def test_row_alignment_and_margin():
    row = Row(
        Column(12).add_text("x"),
        align={"horizontal": "center", "vertical": "end"},
        margin="mt-2 mb-2",
    )
    html = row.render()
    assert "justify-center" in html
    assert "items-end" in html
    assert "mt-2" in html and "mb-2" in html

