import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from fly_video_assignment_away.automation.video import VideoManager

URL_PATTERN = "https://moodle.scnu.edu.cn/mod/fsresource/view.php?id="
COURSE_URL = "https://moodle.scnu.edu.cn/course/view.php?id=19853"


def get_links(monkeypatch: pytest.MonkeyPatch, hrefs: list[str]) -> tuple:
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    locator = MagicMock()
    locator.evaluate_all = AsyncMock(return_value=hrefs)
    page = MagicMock()
    page.goto = AsyncMock()
    page.locator = MagicMock(return_value=locator)

    links = asyncio.run(
        VideoManager(page, MagicMock()).get_video_links_by_pattern(
            COURSE_URL, URL_PATTERN
        )
    )
    return page, links


def test_video_links_are_scoped_to_course_activities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page, _links = get_links(monkeypatch, [f"{URL_PATTERN}870722"])

    page.locator.assert_called_once_with(f'li.activity a[href*="{URL_PATTERN}"]')


def test_video_links_are_deduplicated_in_page_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _page, links = get_links(
        monkeypatch,
        [
            f"{URL_PATTERN}870730",
            f"{URL_PATTERN}870730",
            f"{URL_PATTERN}870722",
            f"{URL_PATTERN}870730",
        ],
    )

    assert links == [f"{URL_PATTERN}870730", f"{URL_PATTERN}870722"]
