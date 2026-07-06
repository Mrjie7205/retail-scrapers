"""按需启动的 Playwright 运行时。"""

from __future__ import annotations

import random
from typing import Any

from playwright.async_api import Browser, BrowserContext, Playwright, async_playwright

USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
)

BROWSER_ARGS = (
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--disable-dev-shm-usage",
    "--no-sandbox",
)

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
"""


class BrowserRuntime:
    """API渠道不启动Chromium；只有adapter申请context时才启动浏览器。"""

    def __init__(self, *, headless: bool = True) -> None:
        self.headless = headless
        self.playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def __aenter__(self) -> BrowserRuntime:
        self.playwright = await async_playwright().start()
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._browser:
            await self._browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def browser(self) -> Browser:
        if self.playwright is None:
            raise RuntimeError("BrowserRuntime尚未启动")
        if self._browser is None:
            self._browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=list(BROWSER_ARGS),
            )
        return self._browser

    async def new_context(
        self,
        *,
        locale: str,
        timezone_id: str,
        user_agent: str | None = None,
    ) -> BrowserContext:
        browser = await self.browser()
        context = await browser.new_context(
            user_agent=user_agent or random.choice(USER_AGENTS),
            viewport={"width": random.choice((1366, 1440, 1536)), "height": 900},
            locale=locale,
            timezone_id=timezone_id,
        )
        await context.add_init_script(STEALTH_JS)
        return context

    async def new_request_context(
        self,
        *,
        locale: str = "en-US",
        referer: str | None = None,
    ):
        if self.playwright is None:
            raise RuntimeError("BrowserRuntime尚未启动")
        headers = {
            "accept-language": f"{locale},en;q=0.8",
        }
        if referer:
            headers["referer"] = referer
        return await self.playwright.request.new_context(
            user_agent=random.choice(USER_AGENTS),
            extra_http_headers=headers,
        )
