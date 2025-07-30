import json
import uuid


def generate_chartjs_block(title, data, chart_type="bar", options=None):
    """Return a Chart.js HTML block for different chart types."""
    options = options or {}

    allowed_types = {"bar", "line", "pie", "scatter"}
    chart_type = chart_type if chart_type in allowed_types else "bar"

    chart_id = "chart_" + uuid.uuid4().hex[:8]

    # Prepare labels and datasets depending on chart type
    if chart_type in {"bar", "line"}:
        labels = [item["label"] for item in data]
        values = [item["value"] for item in data]
        datasets = [
            {
                "label": title if options.get("show_legend", False) else "",
                "data": values,
                "backgroundColor": options.get("bar_color", "#73060F"),
                "borderColor": options.get("border_color", "#73060F"),
                "tension": options.get("tension", 0.3),
                "fill": options.get("fill", False),
            }
        ]
    elif chart_type == "pie":
        labels = [item["label"] for item in data]
        values = [item["value"] for item in data]
        colors = [item.get("color", options.get("bar_color", "#73060F")) for item in data]
        datasets = [
            {
                "label": title if options.get("show_legend", False) else "",
                "data": values,
                "backgroundColor": colors,
            }
        ]
    else:  # scatter
        labels = []
        datasets = [
            {
                "label": title if options.get("show_legend", False) else "",
                "data": data,
                "backgroundColor": options.get("bar_color", "#73060F"),
                "borderColor": options.get("border_color", "#73060F"),
                "showLine": False,
            }
        ]

    # Personalizações via options
    show_legend = options.get("show_legend", False)
    show_data_labels = options.get("show_data_labels", False)
    show_x_axis = options.get("show_x_axis", True)
    show_y_axis = options.get("show_y_axis", True)
    autosize_x = options.get("autosize_x", True)
    autosize_y = options.get("autosize_y", False)
    height_px = options.get("height", 300)

    title_visible = options.get("show_title", True)
    title_html = (
        f'<h3 class="text-lg font-semibold mb-3">{title}</h3>'
        if title_visible
        else ""
    )

    # Datalabels config
    anchor = options.get(
        "data_label_anchor",
        "end" if chart_type == "bar" else "center",
    )
    align = "top" if chart_type == "bar" else "bottom"

    data_label_color = options.get("data_label_color", "#111")
    data_label_font = options.get(
        "data_label_font",
        {"size": 11, "weight": "bold"},
    )
    data_label_format = options.get("data_label_format")

    if isinstance(data_label_font, dict):
        data_label_font_json = json.dumps(data_label_font)
    else:
        data_label_font_json = str(data_label_font)

    if callable(data_label_format):
        format_expr = data_label_format("value")
        data_label_formatter = f"function(value) {{ return {format_expr}; }}"
    elif isinstance(data_label_format, str):
        if data_label_format.strip().startswith("function"):
            data_label_formatter = data_label_format
        else:
            data_label_formatter = (
                f"function(value) {{ return {data_label_format}; }}"
            )
    else:
        data_label_formatter = "function(value) { return value; }"

    class_attr = (
        f"{'w-full' if autosize_x else ''} "
        f"{'h-full' if autosize_y else ''}"
    ).strip()

    datasets_json = json.dumps(datasets)

    return f'''
    <div class="bg-white rounded-lg shadow p-4 flex flex-col gap-2">
      {title_html}
      <canvas id="{chart_id}" class="{class_attr}" \
        height="{height_px}"></canvas>
      <script>
        const ctx_{chart_id} =
          document.getElementById('{chart_id}').getContext('2d');
        new Chart(ctx_{chart_id}, {{
          type: '{chart_type}',
          data: {{
            labels: {json.dumps(labels)},
            datasets: {datasets_json}
          }},
          options: {{
            responsive: false,
            maintainAspectRatio: false,
            plugins: {{
              legend: {{ display: {str(show_legend).lower()} }},
              datalabels: {{
                display: {str(show_data_labels).lower()},
                color: '{data_label_color}',
                anchor: '{anchor}',
                align: '{align}',
                font: {data_label_font_json},
                formatter: {data_label_formatter}
              }}
            }},
            scales: {{
              x: {{ display: {str(show_x_axis).lower()} }},
              y: {{ display: {str(show_y_axis).lower()} }}
            }}
          }},
          plugins: [ChartDataLabels]
        }});
      </script>
    </div>
    '''
