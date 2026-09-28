import os
from pathlib import Path
from typing import Any

import pytest

from fly_video_assignment_away import setup_wizard

NEW_CONFIG = {
    "BROWSER": "chrome",
    "HEADLESS": "true",
    "VIDEO_LIST_URL": "https://moodle.scnu.edu.cn/course/view.php?id=12345",
}


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.chdir(tmp_path)
    for key in (*setup_wizard.MANAGED_ENV_KEYS, "COOKIE_FILE"):
        # setenv 先记录原值，保证 delenv 以及测试中 load_dotenv 写入的值都会被还原
        monkeypatch.setenv(key, "")
        monkeypatch.delenv(key)
    return tmp_path


def _patch_prompts(
    monkeypatch: pytest.MonkeyPatch,
    prompt_ask: Any,
    confirm_ask: Any,
) -> None:
    monkeypatch.setattr(setup_wizard.Prompt, "ask", staticmethod(prompt_ask))
    monkeypatch.setattr(setup_wizard.Confirm, "ask", staticmethod(confirm_ask))


def test_merge_updates_managed_keys_and_keeps_the_rest() -> None:
    existing = (
        "# 自定义注释\n"
        "BROWSER=msedge  # 行尾注释\n"
        "COOKIE_FILE=my_cookies.json\n"
        "export VIDEO_LIST_URL=https://moodle.scnu.edu.cn/course/view.php?id=YOUR_COURSE_ID\n"
    )

    merged = setup_wizard._merge_env_content(existing, NEW_CONFIG)

    assert merged.splitlines() == [
        "# 自定义注释",
        'BROWSER="chrome"  # 行尾注释',
        "COOKIE_FILE=my_cookies.json",
        f'export VIDEO_LIST_URL="{NEW_CONFIG["VIDEO_LIST_URL"]}"',
        "",
        'HEADLESS="true"',
    ]


def test_read_existing_defaults_prefers_real_env_vars(
    isolated_env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (isolated_env / ".env").write_text(
        'BROWSER="chrome"\n'
        'VIDEO_LIST_URL="https://moodle.scnu.edu.cn/course/view.php?id=12345"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("BROWSER", "msedge")

    defaults = setup_wizard._read_existing_defaults()

    assert defaults == {
        "BROWSER": "msedge",
        "HEADLESS": None,
        "VIDEO_LIST_URL": "https://moodle.scnu.edu.cn/course/view.php?id=12345",
    }


def test_run_wizard_reuses_existing_env_as_defaults(
    isolated_env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (isolated_env / ".env").write_text(
        'BROWSER="chrome"\nHEADLESS="true"\n'
        'VIDEO_LIST_URL="https://moodle.scnu.edu.cn/course/view.php?id=12345"\n',
        encoding="utf-8",
    )
    # 模拟用户对每个问题直接回车：沿用默认值
    asked: list[Any] = []

    def fake_prompt_ask(prompt: str, **kwargs: Any) -> str:
        asked.append(kwargs.get("default"))
        default = kwargs.get("default")
        return default if default is not None else ""

    def fake_confirm_ask(prompt: str, **kwargs: Any) -> bool:
        asked.append(kwargs.get("default"))
        return bool(kwargs.get("default"))

    _patch_prompts(monkeypatch, fake_prompt_ask, fake_confirm_ask)

    config = setup_wizard._run_wizard()

    assert config == NEW_CONFIG
    # 三项旧配置都作为默认值出现，回车即可沿用
    assert "chrome" in asked
    assert True in asked
    assert NEW_CONFIG["VIDEO_LIST_URL"] in asked


def test_run_wizard_requires_valid_url_when_missing(
    isolated_env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # 无默认值时依次输入：空、占位符，最终输入有效链接
    url_answers = iter(
        [
            "",
            "https://moodle.scnu.edu.cn/course/view.php?id=YOUR_COURSE_ID",
            NEW_CONFIG["VIDEO_LIST_URL"],
        ]
    )

    def fake_prompt_ask(prompt: str, **kwargs: Any) -> str:
        default = kwargs.get("default")
        if default is None:
            return next(url_answers)
        return default

    _patch_prompts(monkeypatch, fake_prompt_ask, lambda prompt, **kwargs: False)

    config = setup_wizard._run_wizard()

    assert config["VIDEO_LIST_URL"] == NEW_CONFIG["VIDEO_LIST_URL"]


def test_write_env_merges_and_refreshes_environ(isolated_env: Path) -> None:
    original = (
        "COOKIE_FILE=my_cookies.json\n"
        "VIDEO_LIST_URL=https://moodle.scnu.edu.cn/course/view.php?id=YOUR_COURSE_ID\n"
    )
    env_path = isolated_env / ".env"
    env_path.write_text(original, encoding="utf-8")
    # 模拟向导读取默认值时已把旧的占位符加载进 os.environ
    setup_wizard._read_existing_defaults()

    setup_wizard._write_env(NEW_CONFIG)

    assert "COOKIE_FILE=my_cookies.json" in env_path.read_text(encoding="utf-8")
    assert os.environ["VIDEO_LIST_URL"] == NEW_CONFIG["VIDEO_LIST_URL"]
    assert os.environ["BROWSER"] == "chrome"


def test_write_env_skips_rewrite_when_unchanged(isolated_env: Path) -> None:
    setup_wizard._write_env(NEW_CONFIG)
    env_path = isolated_env / ".env"
    marker_time = 1_000_000
    os.utime(env_path, (marker_time, marker_time))

    setup_wizard._write_env(NEW_CONFIG)

    assert os.stat(env_path).st_mtime == marker_time
