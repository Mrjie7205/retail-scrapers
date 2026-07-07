from pathlib import Path

import pytest

from retail_scrapers.doctor import check_channels, check_project_root, check_python, run_doctor


def test_check_python_reports_current_interpreter():
    check = check_python()
    assert check.name == "python"
    assert check.status == "ok"
    assert check.message


def test_check_channels_lists_builtin_adapters():
    check = check_channels()
    assert check.status == "ok"
    assert "elkjop-no" in check.message


def test_check_project_root_detects_missing_project(tmp_path: Path):
    check = check_project_root(tmp_path)
    assert check.status == "error"


@pytest.mark.asyncio
async def test_run_doctor_without_browser_check():
    report = await run_doctor(check_browser=False)
    names = {row["name"] for row in report["checks"]}
    assert "chromium" not in names
    assert {"python", "package", "playwright", "project-root", "channels"} <= names
    assert report["status"] in {"ok", "warning", "error"}
