"""
🔥 Calcifer — Playwright Browser Base
"""
import asyncio
from playwright.async_api import async_playwright

class PlaywrightBrowser:
    def __init__(self, module_name: str = "base"):
        self.module_name = module_name
        self.playwright  = None
        self.browser     = None
        self.context     = None
        self.page        = None

    async def init(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1366,768",
            ]
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        self.page = await self.context.new_page()

    async def navigate(self, url: str):
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

    async def close(self):
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
