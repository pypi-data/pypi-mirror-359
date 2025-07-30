from dashgen.core.utils import (
    format_currency,
    format_percent,
    calculate_performance,
    image_to_base64,
)
from dashgen.charts.chartjs import generate_chartjs_block


def render_card(
    title,
    value,
    target,
    style=None,
    currency="R$",
    abreviar=True,
):
    style = style or {}

    perc = calculate_performance(value, target)
    title_color = style.get("title_color", "text-primary")
    title_size = style.get("title_size", "text-lg")
    text_size = style.get("text_size", "text-sm")
    bar_color = style.get("bar_color", "bg-[color:var(--primary)]")
    card_class = style.get("card_class", "bg-white rounded-lg shadow p-4")

    if abreviar:
        value_fmt = format_currency(value, currency)
        target_fmt = format_currency(target, currency)
    else:
        value_fmt = (
            f"{currency} {value:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        target_fmt = (
            f"{currency} {target:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    return f'''
    <div class="{card_class}">
        <h3 class="{title_size} font-semibold mb-2 {title_color}">
            {title}
        </h3>
        <p class="{text_size} mb-2">
            <strong>{value_fmt}</strong> / {target_fmt} ({format_percent(perc)})
        </p>
        <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div class="h-full {bar_color}"
                 style="width:{min(100, perc)}%"></div>
        </div>
    </div>
    '''


def render_table(
    title,
    data,
    headers,
    progress_columns=None,
    progress_config=None,
):
    progress_columns = progress_columns or []
    progress_config = progress_config or {
        "below": {"bar_color": "bg-red-400", "text_color": "text-white"},
        "met": {"bar_color": "bg-yellow-400", "text_color": "text-black"},
        "above": {"bar_color": "bg-green-500", "text_color": "text-white"},
    }

    rows = ""
    for row in data:
        row_html = ""
        for h in headers:
            valor = str(row.get(h, ""))

            cond = (
                h in progress_columns
                and valor.replace("%", "")
                .replace(",", ".")
                .replace(".", "")
                .isdigit()
            )
            if cond:
                try:
                    perc = float(valor.replace("%", "").replace(",", "."))
                except Exception:
                    perc = 0

                faixa = (
                    "below" if perc < 100 else
                    "met" if perc == 100 else
                    "above"
                )

                bar_color = progress_config[faixa]["bar_color"]
                text_color = progress_config[faixa]["text_color"]

                row_html += (
                    "<td class='px-3 py-2 border-b border-gray-100 text-sm "
                    "align-middle'>"
                    "<div class=\"relative w-full bg-gray-100 rounded h-4 "
                    "overflow-hidden\">"
                    f"<div class=\"absolute left-0 top-0 h-full {bar_color}\" "
                    f"style=\"width:{min(perc, 100)}%\"></div>"
                    f"<div class=\"relative text-center z-10 text-xs "
                    f"leading-4 {text_color}\">"
                    f"{valor}</div>"
                    "</div>"
                    "</td>"
                )
            else:
                row_html += (
                    f"<td class='px-3 py-2 border-b border-gray-100 text-sm'>"
                    f"{valor}</td>"
                )
        rows += f"<tr>{row_html}</tr>"

    header_html = "".join(
        [
            (
                "<th class='text-left text-[color:var(--primary)] "
                "font-semibold text-sm px-3 py-2 bg-gray-100'>"
                f"{h}</th>"
            )
            for h in headers
        ]
    )

    return f'''
    <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-3">{title}</h3>
        <div class="overflow-x-auto">
            <table class="w-full border-collapse">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    '''


def render_chart(chart_type, title, data, options=None):
    return generate_chartjs_block(
        title,
        data,
        chart_type=chart_type,
        options=options,
    )


def render_box(content, style=None):
    """Return a generic container box."""
    style = style or {}
    border = style.get("border", "border")
    padding = style.get("padding", "p-4")
    background = style.get("background", "bg-white")
    width = style.get("width", "w-full")
    height = style.get("height")

    class_attr = f"{background} {border} {padding} {width}".strip()
    style_attr = f"height:{height};" if height else ""

    return f"<div class=\"{class_attr}\" style=\"{style_attr}\">{content}</div>"


def render_text(text, style=None):
    """Return a styled text element."""
    style = style or {}
    size = style.get("size", "text-base")
    weight = style.get("weight", "normal")
    color = style.get("color", "text-[color:var(--text)]")
    align = style.get("align", "left")

    return (
        f"<p class=\"{size} font-{weight} {color} text-{align}\">{text}</p>"
    )


def render_image(path, style=None):
    """Embed an image using a base64 data URI."""
    style = style or {}
    width = style.get("width", "auto")
    height = style.get("height", "auto")
    align = style.get("align", "center")

    img_b64 = image_to_base64(path)

    align_class = {
        "center": "mx-auto",
        "left": "mr-auto",
        "right": "ml-auto",
    }.get(align, "mx-auto")

    style_attr = f"width:{width};height:{height};"

    return (
        f"<img src=\"data:image/png;base64,{img_b64}\" class=\"{align_class}\" "
        f"style=\"{style_attr}\">"
    )


def render_progress_bar(percent, style=None):
    """Render a horizontal progress bar."""
    style = style or {}
    track_color = style.get("track_color", "bg-gray-200")
    bar_color = style.get("bar_color", "bg-[color:var(--primary)]")
    height = style.get("height", "h-2")
    width = style.get("width", "w-full")

    clamped = max(0, min(100, calculate_performance(percent, 100)))

    return (
        f"<div class=\"relative {track_color} {height} {width} rounded-full "
        f"overflow-hidden\">"
        f"<div class=\"absolute left-0 top-0 h-full {bar_color}\" "
        f"style=\"width:{clamped}%\"></div>"
        "</div>"
    )
