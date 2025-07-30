from playwright.async_api import async_playwright


async def render_html_to_image(html, output_path, width, height):
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Usa altura fornecida ou provisória
        initial_height = height if height is not None else 800
        page = await browser.new_page(
            viewport={"width": width, "height": initial_height}
        )
        await page.set_content(html, wait_until="networkidle")

        if height is None:
            # Aguarda o scrollHeight estabilizar
            await page.evaluate(
                """
          () => {
            return new Promise((resolve) => {
              let last = 0;
              let count = 0;

              const interval = setInterval(() => {
                const current = document.body.scrollHeight;
                if (current === last) {
                  count++;
                  if (count >= 3) {
                    clearInterval(interval);
                    resolve();
                  }
                } else {
                  count = 0;
                  last = current;
                }
              }, 100);
            });
          }
        """
            )

            # Captura a altura real
            final_height = await page.evaluate(
                "document.documentElement.scrollHeight"
            )
        else:
            final_height = height

        # Reajusta apenas a altura (largura continua fixa)
        await page.set_viewport_size({"width": width, "height": final_height})

        # Screenshot somente da área visível (sem scroll horizontal)
        await page.screenshot(path=output_path, full_page=False)

        await browser.close()
