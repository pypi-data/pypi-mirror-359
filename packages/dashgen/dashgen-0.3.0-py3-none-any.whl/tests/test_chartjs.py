from dashgen.charts.chartjs import generate_chartjs_block


def test_generate_chartjs_default_type():
    data = [{"label": "A", "value": 1}, {"label": "B", "value": 2}]
    html = generate_chartjs_block("My Chart", data, chart_type="invalid")
    assert "type: 'bar'" in html
    assert 'canvas id="chart_' in html
    assert 'labels: ["A", "B"]' in html
    assert '"data": [1, 2]' in html


def test_generate_chartjs_options():
    data = [{"label": "A", "value": 1}]
    html = generate_chartjs_block(
        "Hidden Title",
        data,
        chart_type="line",
        options={"show_title": False, "autosize_x": False, "autosize_y": True}
    )
    assert "<h3" not in html
    assert "type: 'line'" in html
    assert 'class="h-full"' in html
    assert 'class="w-full"' not in html


def test_generate_chartjs_pie_and_scatter():
    pie_data = [
        {"label": "A", "value": 1, "color": "#111"},
        {"label": "B", "value": 2, "color": "#222"},
    ]
    pie_html = generate_chartjs_block("Pie", pie_data, chart_type="pie")
    assert "type: 'pie'" in pie_html
    assert 'labels: ["A", "B"]' in pie_html
    assert '"data": [1, 2]' in pie_html
    assert '"backgroundColor": ["#111", "#222"]' in pie_html

    scatter_data = [{"x": 1, "y": 2}, {"x": 2, "y": 3}]
    scatter_html = generate_chartjs_block("S", scatter_data, chart_type="scatter")
    assert "type: 'scatter'" in scatter_html
    assert '"data": [{"x": 1, "y": 2}, {"x": 2, "y": 3}]' in scatter_html


def test_generate_chartjs_datalabel_customization():
    data = [{"label": "A", "value": 10}]
    html = generate_chartjs_block(
        "DL", data, options={
            "show_data_labels": True,
            "data_label_color": "#ff0000",
            "data_label_format": "value + '%'",
        }
    )
    assert "color: '#ff0000'" in html
    assert "return value + '%'" in html
