import asyncio
from dashgen.core.renderer import render_html_to_image

class DummyPage:
    def __init__(self, scroll_height):
        self.scroll_height = scroll_height
        self.initial_viewport = None
        self.final_viewport = None
        self.screenshot_path = None

    async def set_content(self, html, wait_until=None):
        self.html = html

    async def evaluate(self, script):
        return self.scroll_height

    async def set_viewport_size(self, size):
        self.final_viewport = size

    async def screenshot(self, path, full_page=False):
        self.screenshot_path = path

class DummyBrowser:
    def __init__(self, page):
        self.page = page

    async def new_page(self, viewport):
        self.page.initial_viewport = viewport
        return self.page

    async def close(self):
        pass

class DummyBrowserType:
    def __init__(self, page):
        self.page = page

    async def launch(self):
        return DummyBrowser(self.page)

class DummyPlaywright:
    def __init__(self, page):
        self.page = page

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    @property
    def chromium(self):
        return DummyBrowserType(self.page)

def test_auto_height(monkeypatch, tmp_path):
    page = DummyPage(scroll_height=600)
    monkeypatch.setattr('dashgen.core.renderer.async_playwright', lambda: DummyPlaywright(page))
    output = tmp_path / "out.png"
    asyncio.run(render_html_to_image('<html></html>', str(output), 400, None))
    assert page.initial_viewport == {"width": 400, "height": 800}
    assert page.final_viewport == {"width": 400, "height": 600}

def test_fixed_height(monkeypatch, tmp_path):
    page = DummyPage(scroll_height=1000)
    monkeypatch.setattr('dashgen.core.renderer.async_playwright', lambda: DummyPlaywright(page))
    output = tmp_path / "out.png"
    asyncio.run(render_html_to_image('<html></html>', str(output), 400, 300))
    assert page.initial_viewport == {"width": 400, "height": 300}
    assert page.final_viewport == {"width": 400, "height": 300}
