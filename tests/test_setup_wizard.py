import os
from pathlib import Path

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


def test_needs_setup_skips_wizard_when_env_var_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VIDEO_LIST_URL", NEW_CONFIG["VIDEO_LIST_URL"])

    assert not setup_wizard._needs_setup()


def test_needs_setup_rejects_placeholder_in_env_file(isolated_env: Path) -> None:
    (isolated_env / ".env").write_text(
        "VIDEO_LIST_URL=https://moodle.scnu.edu.cn/course/view.php?id=YOUR_COURSE_ID\n",
        encoding="utf-8",
    )

    assert setup_wizard._needs_setup()


def test_write_env_backs_up_and_refreshes_environ(isolated_env: Path) -> None:
    original = (
        "COOKIE_FILE=my_cookies.json\n"
        "VIDEO_LIST_URL=https://moodle.scnu.edu.cn/course/view.php?id=YOUR_COURSE_ID\n"
    )
    env_path = isolated_env / ".env"
    env_path.write_text(original, encoding="utf-8")
    # 模拟 _needs_setup 已把旧的占位符加载进 os.environ
    assert setup_wizard._needs_setup()

    setup_wizard._write_env(NEW_CONFIG)

    assert (isolated_env / ".env.bak").read_text(encoding="utf-8") == original
    assert "COOKIE_FILE=my_cookies.json" in env_path.read_text(encoding="utf-8")
    assert os.environ["VIDEO_LIST_URL"] == NEW_CONFIG["VIDEO_LIST_URL"]
    assert os.environ["BROWSER"] == "chrome"
    assert not setup_wizard._needs_setup()
