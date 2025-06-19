from agents import AsyncComputer
from playwright.async_api import Browser, Page

from ..shared.base_playwright import BasePlaywrightComputer


class LocalPlaywrightBrowser(BasePlaywrightComputer, AsyncComputer):
    """Launches Chrome via CDP or falls back to Playwright Chromium."""

    def __init__(
        self, debug_port: int = 9222, initial_url: str = "https://www.google.com", show_cursor: bool = True
    ):
        """Initialize the browser.

        Args:
            debug_port: Port for Chrome remote debugging
            initial_url: Initial URL to navigate to
        """
        super().__init__(initial_url=initial_url)
        self.debug_port = debug_port
        self.show_cursor = show_cursor

    async def _get_browser_and_page(self) -> tuple[Browser, Page]:
        """Connect to Chrome via CDP or fall back to Playwright browser."""
        width, height = self.dimensions

        print(f"Checking for Chrome on debug port {self.debug_port}")

        # Try connecting to Chrome via CDP
        try:
            print(f"Port {self.debug_port} is accessible, attempting CDP connection...")
            # Connect to existing Chrome
            assert self._playwright is not None, "Playwright not initialized"
            browser = await self._playwright.chromium.connect_over_cdp(
                f"http://localhost:{self.debug_port}"
            )
            print(f"Connected to Chrome! Contexts: {len(browser.contexts)}")
            context = browser.contexts[0]

            # Find a regular web page (not extension pages)
            page = None
            for p in context.pages:
                url = p.url
                if not url.startswith(
                    ("chrome-extension://", "chrome://", "chrome-untrusted://")
                ):
                    page = p
                    print(f"Using existing page: {url}")
                    break

            # If no regular page found, create a new one
            if not page:
                page = await context.new_page()
                await page.goto("about:blank")
                print("Created new blank page")

            await page.set_viewport_size({"width": width, "height": height})
            print("Using existing Chrome session")
            return browser, page
        except Exception as e:
            print(f"Failed to connect to Chrome: {e}")

        # Fall back to regular Playwright browser
        print("Falling back to Playwright browser")
        assert self._playwright is not None, "Playwright not initialized"
        browser = await self._playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_viewport_size({"width": width, "height": height})
        return browser, page

    async def _handle_new_page(self, page: Page):
        """Handle the creation of a new page."""
        print("New page created")
        self._page = page
        page.on("close", self._handle_page_close)

    async def _handle_page_close(self, page: Page):
        """Handle the closure of a page."""
        print("Page closed")
        if self._page == page:
            assert self._browser is not None, "Browser not initialized"
            if self._browser.contexts[0].pages:
                self._page = self._browser.contexts[0].pages[-1]
            else:
                print("Warning: All pages have been closed.")
                # create a new page and assign it to the active page
                self._page = await self._browser.new_page()
