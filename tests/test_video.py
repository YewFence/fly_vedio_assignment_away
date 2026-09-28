import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from rich.progress import TaskID

from fly_video_assignment_away.automation.exception_context import BrowserClosedError
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


WATCHED = ".num-gksc > span"
PERCENT = ".num-bfjd > span"
REQUIRED = ".tips > span:not(.tips-completion)"
STATUS = ".tips-completion"


def platform_page(texts: dict[str, str], error: Exception | None = None) -> MagicMock:
    """按选择器返回文本的假页面，未列出的选择器视为元素不存在"""

    def locator_for(selector: str) -> MagicMock:
        locator = MagicMock()
        text = texts.get(selector)
        locator.count = AsyncMock(return_value=0 if text is None else 1)
        locator.first.text_content = AsyncMock(return_value=text, side_effect=error)
        return locator

    page = MagicMock()
    page.locator = MagicMock(side_effect=locator_for)
    return page


@pytest.mark.parametrize(
    ("method", "selector"),
    [
        ("get_platform_watched_seconds", WATCHED),
        ("get_platform_progress_percent", PERCENT),
        ("get_platform_required_percent", REQUIRED),
    ],
)
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (" 2795 ", 2795.0),
        ("17.8", 17.8),
        ("90%", 90.0),
        (None, None),
        ("", None),
        ("--", None),
    ],
)
def test_platform_numbers_are_parsed_or_none(
    method: str, selector: str, text: str | None, expected: float | None
) -> None:
    texts = {} if text is None else {selector: text}
    manager = VideoManager(platform_page(texts), MagicMock())

    assert asyncio.run(getattr(manager, method)()) == expected


def test_platform_read_failure_falls_back_instead_of_raising() -> None:
    page = platform_page(
        {WATCHED: "411", STATUS: "已完成"},
        error=PlaywrightTimeoutError("Timeout 2000ms exceeded."),
    )
    manager = VideoManager(page, MagicMock())

    assert asyncio.run(manager.get_platform_watched_seconds()) is None
    assert asyncio.run(manager.check_video_completed()) is False


def test_platform_read_still_reports_browser_closed() -> None:
    page = platform_page(
        {WATCHED: "411"},
        error=PlaywrightError("Target page, context or browser has been closed"),
    )

    with pytest.raises(BrowserClosedError):
        asyncio.run(VideoManager(page, MagicMock()).get_platform_watched_seconds())


@pytest.mark.parametrize(
    ("status", "expected"), [("已完成", True), ("未完成", False), (None, False)]
)
def test_check_video_completed(status: str | None, expected: bool) -> None:
    texts = {} if status is None else {STATUS: status}
    manager = VideoManager(platform_page(texts), MagicMock())

    assert asyncio.run(manager.check_video_completed()) is expected


VIDEO_DURATION = 2314.24
# 平台要求 90%：需观看 2082.8 秒（即 34:42）
TARGET_DURATION = VIDEO_DURATION * 0.9


def run_platform_progress(texts: dict[str, str]) -> MagicMock:
    progress = MagicMock()
    asyncio.run(
        VideoManager(platform_page(texts), MagicMock()).update_platform_progress(
            progress, TaskID(1), 90.0, TARGET_DURATION
        )
    )
    return progress


def test_platform_progress_uses_target_as_baseline() -> None:
    progress = run_platform_progress({PERCENT: "17.8", WATCHED: "411"})

    kwargs = progress.update.call_args.kwargs
    # 平台进度 17.8% / 目标 90%，达到目标即为 100%
    assert kwargs["completed"] == pytest.approx(17.8 / 90 * 100)
    assert kwargs["visible"] is True
    assert "6:51" in kwargs["description"]
    assert "34:42" in kwargs["description"]
    assert "%" not in kwargs["description"]


def test_platform_progress_reaching_target_is_full() -> None:
    progress = run_platform_progress({PERCENT: "98", WATCHED: "2795"})

    assert progress.update.call_args.kwargs["completed"] == 100


def test_platform_progress_falls_back_to_watched_seconds() -> None:
    progress = run_platform_progress({WATCHED: "411"})

    assert progress.update.call_args.kwargs["completed"] == pytest.approx(
        411 / TARGET_DURATION * 100
    )


def test_platform_progress_stays_hidden_without_platform_data() -> None:
    progress = run_platform_progress({})

    progress.update.assert_not_called()


def make_play_manager(
    monkeypatch: pytest.MonkeyPatch,
    completed: AsyncMock,
    *,
    duration: float | None = VIDEO_DURATION,
    watched: float = 411.0,
    video_state: dict | None = None,
) -> VideoManager:
    monkeypatch.setattr(asyncio, "sleep", AsyncMock())
    page = MagicMock()
    page.goto = AsyncMock()
    page.click = AsyncMock()
    page.is_closed = MagicMock(return_value=False)
    auth = MagicMock()
    auth.refresh_cookies = AsyncMock()
    auth.check_cookie_validity = AsyncMock(return_value=True)
    manager = VideoManager(page, auth)
    patches = {
        "check_video_completed": completed,
        "get_video_duration": AsyncMock(return_value=duration),
        "get_platform_required_percent": AsyncMock(return_value=90.0),
        "get_platform_watched_seconds": AsyncMock(return_value=watched),
        "get_platform_progress_percent": AsyncMock(return_value=None),
        "pass_human_challenge": AsyncMock(),
        "ensure_video_playing": AsyncMock(return_value=video_state),
    }
    for name, mock in patches.items():
        monkeypatch.setattr(manager, name, mock)
    return manager


def run_play(manager: VideoManager, caplog: pytest.LogCaptureFixture) -> list[str]:
    with caplog.at_level("INFO"):
        asyncio.run(manager.play_video("https://example.test/video", "video", ".play"))
    return [r.getMessage() for r in caplog.records]


@pytest.mark.parametrize(
    ("watched", "expected_remaining"),
    # 剩余按需观看时长计算：2082.8 - 411 = 1671.8 秒；已超过需观看时长时显示 0:00
    [(411.0, "27:51"), (2100.0, "0:00")],
)
def test_play_video_remaining_is_display_only(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    watched: float,
    expected_remaining: str,
) -> None:
    # 进入页面时未完成，第一次轮询时平台标记完成
    completed = AsyncMock(side_effect=[False, True])
    manager = make_play_manager(monkeypatch, completed, watched=watched)

    messages = run_play(manager, caplog)

    info = next(m for m in messages if "总时长" in m)
    assert f"剩余: {expected_remaining}" in info
    assert "需观看: 34:42 (90%)" in info
    assert info.index("剩余") < info.index("需观看")
    # 即使估算剩余为 0 也必须进入等待循环，由平台完成标记决定是否完成
    assert completed.await_count == 2
    assert "✓ 平台已标记视频完成" in messages


def test_play_video_timeout_is_not_reported_as_completed(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    manager = make_play_manager(
        monkeypatch, AsyncMock(return_value=False), duration=4.0
    )

    messages = run_play(manager, caplog)

    assert any("仍未确认完成" in m for m in messages)
    assert "✓ 平台已标记视频完成" not in messages
    assert "✓ 视频已播放到结尾" not in messages


def test_play_video_falls_back_to_video_reaching_the_end(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    ended_state = {
        "paused": True,
        "currentTime": VIDEO_DURATION,
        "duration": VIDEO_DURATION,
        "ended": True,
    }
    manager = make_play_manager(
        monkeypatch, AsyncMock(return_value=False), video_state=ended_state
    )

    messages = run_play(manager, caplog)

    assert "✓ 视频已播放到结尾" in messages
    assert not any("仍未确认完成" in m for m in messages)


def test_play_video_without_duration_does_not_claim_completion(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    manager = make_play_manager(
        monkeypatch, AsyncMock(return_value=False), duration=None
    )

    messages = run_play(manager, caplog)

    assert any("无法确认该链接是否完成" in m for m in messages)
    assert not any(m.startswith("✓") and "完成" in m for m in messages)
