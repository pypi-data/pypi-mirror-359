from dashgen.core.components import (
    render_card,
    render_table,
    render_chart,
    render_box,
    render_text,
    render_image,
    render_progress_bar,
)


class Column:
    def __init__(
        self,
        width=12,
        *components,
        align=None,
        order=None,
        breakpoints=None,
        margin=None,
        padding=None,
        classes="",
    ):
        self.width = width
        self.align = align or {}
        self.order = order
        self.breakpoints = breakpoints or {}
        self.margin = margin
        self.padding = padding
        self.classes = classes
        self.content = list(components)
        self._types = []
        self._chart_heights = []

    def add(self, *components):
        self.content.extend(components)
        return self

    def add_card(
        self,
        title,
        value,
        target,
        currency="R$",
        style=None,
        abreviar=True,
    ):
        self.add(
            render_card(
                title,
                value,
                target,
                style=style,
                currency=currency,
                abreviar=abreviar,
            )
        )
        self._types.append("card")
        return self

    def add_table(
        self,
        title,
        data,
        headers,
        progress_columns=None,
        progress_config=None,
    ):
        self.add(
            render_table(
                title,
                data,
                headers,
                progress_columns=progress_columns,
                progress_config=progress_config,
            )
        )
        self._types.append("table")
        return self

    def add_chart(self, chart_type, title, data, options=None):
        self.add(render_chart(chart_type, title, data, options=options))
        self._types.append("chart")
        if options and "height" in options:
            self._chart_heights.append(options["height"])
        return self

    def add_box(self, content, style=None):
        self.add(render_box(content, style=style))
        self._types.append("box")
        return self

    def add_text(self, text, style=None):
        self.add(render_text(text, style=style))
        self._types.append("text")
        return self

    def add_image(self, path, style=None):
        self.add(render_image(path, style=style))
        self._types.append("image")
        return self

    def add_progress(self, percent, style=None):
        self.add(render_progress_bar(percent, style=style))
        self._types.append("progress")
        return self

    def render(self):
        classes = [f"col-span-{self.width}"]
        for bp, w in self.breakpoints.items():
            classes.append(f"{bp}:col-span-{w}")
        if self.order is not None:
            classes.append(f"order-{self.order}")
        if self.margin:
            classes.append(self.margin)
        if self.padding:
            classes.append(self.padding)
        if self.align:
            classes.append("flex")
            h = self.align.get("horizontal")
            v = self.align.get("vertical")
            if h:
                classes.append(f"justify-{h}")
            if v:
                classes.append(f"items-{v}")
        if self.classes:
            classes.append(self.classes)

        class_str = " ".join(classes)
        return f'<div class="{class_str}">' + "".join(self.content) + "</div>"

    def get_component_types(self):
        return self._types

    def get_chart_heights(self):
        return self._chart_heights


class Row:
    def __init__(
        self,
        *columns,
        gap_x=6,
        gap_y=6,
        align=None,
        margin=None,
        padding=None,
        classes="",
    ):
        self.columns = columns
        self.gap_x = gap_x
        self.gap_y = gap_y
        self.align = align or {}
        self.margin = margin
        self.padding = padding
        self.classes = classes

    def render(self):
        classes = [
            f"grid grid-cols-12 gap-x-{self.gap_x} gap-y-{self.gap_y} mb-{self.gap_y}"
        ]
        if self.margin:
            classes.append(self.margin)
        if self.padding:
            classes.append(self.padding)
        h = self.align.get("horizontal")
        v = self.align.get("vertical")
        if h:
            classes.append(f"justify-{h}")
        if v:
            classes.append(f"items-{v}")
        if self.classes:
            classes.append(self.classes)

        class_str = " ".join(classes)
        return (
            f'<div class="{class_str}">' + "".join(col.render() for col in self.columns) + "</div>"
        )

    def estimate_height(self):
        height = 0
        for col in self.columns:
            types = col.get_component_types()
            for t in types:
                if t == "card":
                    height = max(height, 180)
                elif t == "table":
                    height = max(height, 320)

            if hasattr(col, "get_chart_heights"):
                for h in col.get_chart_heights():
                    height = max(height, h + 96)
            elif "chart" in types:
                height = max(height, 450)

        return height + 40
