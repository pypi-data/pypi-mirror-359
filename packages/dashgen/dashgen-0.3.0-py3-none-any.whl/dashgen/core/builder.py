import asyncio
import json
from jinja2 import Template
from dashgen.core.utils import image_to_base64
from dashgen.core.renderer import render_html_to_image
from dashgen.core.layout import Row
from pathlib import Path


class Dashboard:
    def __init__(
        self,
        title="Dashboard",
        logo_path=None,
        size=(1080, 1080),
        theme=None,
        auto_size=False,
        title_style=None,
        gap_x=6,
        gap_y=6,
    ):
        self.title = title
        self.logo_b64 = image_to_base64(logo_path) if logo_path else ""
        self.width, self.height = size
        self.components = []
        self.pages = []
        self.theme = theme or {}
        self.auto_size = auto_size
        self.title_style = (
            title_style
            or "text-xl font-semibold text-[color:var(--primary)]"
        )
        self._dynamic_height = 0  # Acumulador de altura estimada
        self.gap_x = gap_x
        self.gap_y = gap_y

    def add(self, *elements):
        for layout in elements:
            if isinstance(layout, Row):
                layout.gap_x = self.gap_x
                layout.gap_y = self.gap_y

            if self.auto_size and hasattr(layout, "estimate_height"):
                self._dynamic_height += layout.estimate_height()

            if hasattr(layout, "render"):
                self.components.append(layout.render())
            else:
                self.components.append(str(layout))

    def save_theme(self, path):
        """Save current theme configuration to a JSON file."""
        Path(path).write_text(json.dumps(self.theme, indent=2), encoding="utf-8")

    def load_theme(self, path):
        """Load theme configuration from a JSON file."""
        p = Path(path)
        if p.exists():
            self.theme = json.loads(p.read_text(encoding="utf-8"))

    def generate_page(self):
        """Add current components as a page and reset for a new page."""
        self.pages.append(list(self.components))
        self.components = []
        self._dynamic_height = 0
    def _render(self, components, output_path):
        base_html_path = (
            Path(__file__).parent.parent / "templates" / "base.html"
        )
        css_path = Path(__file__).parent.parent / "themes" / "default.css"

        with open(css_path, encoding="utf-8") as f:
            theme_css = f.read()

        custom_root = ":root {\n" + "\n".join([
            f"  --{k}: {v};" for k, v in self.theme.items()
        ]) + "\n}\n"

        if ":root {" in theme_css:
            theme_css = (
                custom_root
                + css_path.read_text(encoding="utf-8").split("}", 1)[1]
            )
        else:
            theme_css = custom_root + theme_css

        with open(base_html_path, encoding="utf-8") as f:
            template = Template(f.read())

        rendered_html = template.render(
            title=self.title,
            title_style=self.title_style,
            logo_b64=self.logo_b64,
            components="\n".join(components),
            theme_css=theme_css,
            theme=self.theme
        )

        final_height = (
            self._dynamic_height if self.auto_size else self.height
        )

        asyncio.run(
            render_html_to_image(
                rendered_html,
                output_path,
                self.width,
                final_height,
            )
        )

    def generate(self, output_path):
        """Generate images for one or multiple pages."""
        if isinstance(output_path, (list, tuple)):
            pages = self.pages + [self.components]
            if len(output_path) != len(pages):
                raise ValueError("Number of paths must match number of pages")
            for comps, path in zip(pages, output_path):
                self._render(comps, path)
        else:
            self._render(self.components, output_path)
