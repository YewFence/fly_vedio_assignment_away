import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from fly_video_assignment_away.automation import browser as browser_module
from fly_video_assignment_away.automation.browser import BrowserManager


@pytest.fixture
def fake_chromium(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    context = SimpleNamespace(new_page=AsyncMock(), close=AsyncMock())
    fake_browser = SimpleNamespace(
        new_context=AsyncMock(return_value=context),
        is_connected=MagicMock(return_value=True),
        close=AsyncMock(),
    )
    chromium = SimpleNamespace(
        launch=AsyncMock(return_value=fake_browser),
        connect_over_cdp=AsyncMock(return_value=fake_browser),
    )
    playwright = SimpleNamespace(chromium=chromium, stop=AsyncMock())
    starter = SimpleNamespace(start=AsyncMock(return_value=playwright))
    monkeypatch.setattr(browser_module, "async_playwright", lambda: starter)
    return chromium


def test_setup_connects_over_cdp_when_endpoint_is_set(
    fake_chromium: SimpleNamespace,
) -> None:
    manager = BrowserManager(cdp_endpoint="http://127.0.0.1:9222")

    asyncio.run(manager.setup())

    fake_chromium.connect_over_cdp.assert_awaited_once_with("http://127.0.0.1:9222")
    fake_chromium.launch.assert_not_awaited()


def test_setup_launches_channel_without_endpoint(
    fake_chromium: SimpleNamespace,
) -> None:
    manager = BrowserManager(browser_type="chrome", headless=True)

    asyncio.run(manager.setup())

    fake_chromium.connect_over_cdp.assert_not_awaited()
    kwargs = fake_chromium.launch.await_args.kwargs
    assert kwargs["channel"] == "chrome"
    assert kwargs["executable_path"] is None
    assert kwargs["headless"] is True


def test_setup_launches_executable_path_instead_of_channel(
    fake_chromium: SimpleNamespace,
) -> None:
    edge = "/var/lib/flatpak/exports/bin/com.microsoft.Edge"
    manager = BrowserManager(browser_type="chrome", executable_path=edge)

    asyncio.run(manager.setup())

    kwargs = fake_chromium.launch.await_args.kwargs
    assert kwargs["executable_path"] == edge
    assert kwargs["channel"] is None


def test_cdp_endpoint_takes_precedence_over_executable_path(
    fake_chromium: SimpleNamespace,
) -> None:
    manager = BrowserManager(
        executable_path="/usr/bin/edge", cdp_endpoint="http://127.0.0.1:9222"
    )

    asyncio.run(manager.setup())

    fake_chromium.connect_over_cdp.assert_awaited_once()
    fake_chromium.launch.assert_not_awaited()
