import asyncio
import base64
from enum import Enum
from typing import List, Literal, cast

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from ..utils import check_blocklisted_url


class MouseButton(Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    BACK = "back"
    FORWARD = "forward"
    WHEEL = "wheel"


CUA_KEY_TO_PLAYWRIGHT_KEY = {
    "/": "Divide",
    "\\": "Backslash",
    "alt": "Alt",
    "arrowdown": "ArrowDown",
    "arrowleft": "ArrowLeft",
    "arrowright": "ArrowRight",
    "arrowup": "ArrowUp",
    "backspace": "Backspace",
    "capslock": "CapsLock",
    "cmd": "Meta",
    "ctrl": "Control",
    "delete": "Delete",
    "end": "End",
    "enter": "Enter",
    "esc": "Escape",
    "home": "Home",
    "insert": "Insert",
    "option": "Alt",
    "pagedown": "PageDown",
    "pageup": "PageUp",
    "shift": "Shift",
    "space": " ",
    "super": "Meta",
    "tab": "Tab",
    "win": "Meta",
}


async def apply_virtual_mouse(context: BrowserContext):
    """Apply a virtual mouse to the browser context."""
    await context.add_init_script("""
        // Only run in the top frame
        if (window.self === window.top) {
            function initCursor() {
                const CURSOR_ID = '__cursor__';

                // Check if cursor element already exists
                if (document.getElementById(CURSOR_ID)) return;

                const cursor = document.createElement('div');
                cursor.id = CURSOR_ID;
                Object.assign(cursor.style, {
                    position: 'fixed',
                    top: '0px',
                    left: '0px',
                    width: '20px',
                    height: '20px',
                    backgroundImage: 'url("data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 24 24\\' fill=\\'black\\' stroke=\\'white\\' stroke-width=\\'1\\' stroke-linejoin=\\'round\\' stroke-linecap=\\'round\\'><polygon points=\\'2,2 2,22 8,16 14,22 17,19 11,13 20,13\\'/></svg>")',
                    backgroundSize: 'cover',
                    pointerEvents: 'none',
                    zIndex: '99999',
                    transform: 'translate(-2px, -2px)',
                });

                document.body.appendChild(cursor);

                document.addEventListener("mousemove", (e) => {
                    cursor.style.top = e.clientY + "px";
                    cursor.style.left = e.clientX + "px";
                });
            }

            // Use requestAnimationFrame for early execution
            requestAnimationFrame(function checkBody() {
                if (document.body) {
                    initCursor();
                } else {
                    requestAnimationFrame(checkBody);
                }
            });
        }
        """)


class BasePlaywrightComputer:
    """
    Abstract base for Playwright-based computers:

      - Subclasses override `_get_browser_and_page()` to do local or remote connection,
        returning (Browser, Page).
      - This base class handles context creation (`__aenter__`/`__aexit__`),
        plus standard "Computer" actions like click, scroll, etc.
      - We also have extra browser actions: `goto(url)` and `back()`.
    """

    @property
    def environment(self):
        return "browser"

    @property
    def dimensions(self):
        return (1024, 768)

    def __init__(
        self, initial_url: str = "https://www.google.com", show_cursor: bool = True
    ):
        self._playwright = None  # Will be initialized in __aenter__
        self._browser: Browser = None  # type: ignore[assignment]
        self._page: Page = None  # type: ignore[assignment]
        self.initial_url = initial_url
        self.show_cursor = show_cursor

    async def __aenter__(self):
        # Start Playwright and call the subclass hook for getting browser/page
        self._playwright = await async_playwright().start()
        self._browser, self._page = await self._get_browser_and_page()

        # Apply virtual mouse cursor if enabled
        if self.show_cursor:
            await apply_virtual_mouse(self._page.context)

        # Set up network interception to flag URLs matching domains in BLOCKED_DOMAINS
        async def handle_route(route, request):
            url = request.url
            if check_blocklisted_url(url):
                print(f"Flagging blocked domain: {url}")
                await route.abort()
            else:
                await route.continue_()

        assert self._page is not None, "Page not initialized"
        await self._page.route("**/*", handle_route)

        # Navigate to initial URL
        if self.initial_url and not self._page.url.startswith(
            ("chrome://", "chrome-extension://", "chrome-untrusted://")
        ):
            print(f"Navigating to initial URL: {self.initial_url}")
            try:
                await self._page.goto(self.initial_url)
            except Exception as e:
                print(f"Failed to navigate to initial URL: {e}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    def get_current_url(self) -> str:
        return self._page.url

    # --- Common "Computer" actions ---
    async def screenshot(self) -> str:
        """Capture only the viewport (not full_page)."""
        print("Taking screenshot...")
        try:
            print("page:", self._page)
            png_bytes = await self._page.screenshot(
                full_page=False, timeout=0, type="png"
            )
            print(f"Screenshot taken, size: {len(png_bytes)} bytes")
            return base64.b64encode(png_bytes).decode("utf-8")
        except Exception as e:
            print(f"Screenshot failed: {e}")
            raise

    async def click(self, x: int, y: int, button: str = "left") -> None:
        # Handle special button actions
        if button == MouseButton.BACK.value:
            await self.back()
        elif button == MouseButton.FORWARD.value:
            await self.forward()
        elif button == MouseButton.WHEEL.value:
            await self._page.mouse.wheel(x, y)
        else:
            # Handle normal mouse clicks
            if button in [
                MouseButton.LEFT.value,
                MouseButton.RIGHT.value,
                MouseButton.MIDDLE.value,
            ]:
                await self._page.mouse.click(
                    x, y, button=cast(Literal["left", "right", "middle"], button)
                )
            else:
                # Default to left click for unknown buttons
                await self._page.mouse.click(x, y, button="left")

    async def double_click(self, x: int, y: int) -> None:
        await self._page.mouse.dblclick(x, y)

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        await self._page.mouse.move(x=x, y=y)
        await self._page.mouse.wheel(
            delta_x=scroll_x,
            delta_y=scroll_y,
        )

    async def type(self, text: str) -> None:
        await self._page.keyboard.type(text)

    async def wait(self, ms: int = 3000) -> None:
        await asyncio.sleep(ms / 1000)

    async def move(self, x: int, y: int) -> None:
        await self._page.mouse.move(x, y)

    async def keypress(self, keys: List[str]) -> None:
        mapped_keys = [CUA_KEY_TO_PLAYWRIGHT_KEY.get(key.lower(), key) for key in keys]
        for key in mapped_keys:
            await self._page.keyboard.down(key)
        for key in reversed(mapped_keys):
            await self._page.keyboard.up(key)

    async def drag(self, path: list[tuple[int, int]]) -> None:
        if not path:
            return
        await self._page.mouse.move(path[0][0], path[0][1])
        await self._page.mouse.down()
        for point in path[1:]:
            await self._page.mouse.move(point[0], point[1])
        await self._page.mouse.up()

    async def goto(self, url: str) -> None:
        try:
            await self._page.goto(url)
        except Exception as e:
            print(f"Error navigating to {url}: {e}")

    async def back(self) -> None:
        await self._page.go_back()

    async def forward(self) -> None:
        await self._page.go_forward()

    async def _get_browser_and_page(self) -> tuple[Browser, Page]:
        """Subclasses must implement, returning (Browser, Page)."""
        raise NotImplementedError
