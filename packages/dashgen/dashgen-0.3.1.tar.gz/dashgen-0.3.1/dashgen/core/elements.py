from .components import (
    render_box,
    render_text,
    render_image,
    render_progress_bar,
    render_chart,
    render_table,
)


def Box(content, style=None):
    """Return a generic container box."""
    return render_box(content, style=style)


def Text(text, style=None):
    """Return a styled text element."""
    return render_text(text, style=style)


def Image(path, style=None):
    """Embed an image using base64."""
    return render_image(path, style=style)


def ProgressBar(percent, style=None):
    """Render a horizontal progress bar."""
    return render_progress_bar(percent, style=style)


def Chart(chart_type, title, data, options=None):
    """Render a Chart.js block."""
    return render_chart(chart_type, title, data, options=options)


def Table(title, data, headers, progress_columns=None, progress_config=None):
    """Render a table component."""
    return render_table(
        title,
        data,
        headers,
        progress_columns=progress_columns,
        progress_config=progress_config,
    )

__all__ = [
    "Box",
    "Text",
    "Image",
    "ProgressBar",
    "Chart",
    "Table",
]
