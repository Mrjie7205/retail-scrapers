"""Local environment checks for first-time Retail Scrapers users."""

from __future__ import annotations

import importlib.metadata
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .registry import list_channels


@dataclass(slots=True)
class DoctorCheck:
    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "message": self.message}


def _status(ok: bool) -> str:
    return "ok" if ok else "error"


def check_python() -> DoctorCheck:
    version = sys.version_info
    ok = version >= (3, 11)
    return DoctorCheck(
        name="python",
        status=_status(ok),
        message=f"{platform.python_version()} at {sys.executable}",
    )


def check_package_metadata() -> DoctorCheck:
    try:
        version = importlib.metadata.version("retail-scrapers")
    except importlib.metadata.PackageNotFoundError:
        return DoctorCheck(
            name="package",
            status="warning",
            message="retail-scrapers is importable but not installed as package metadata",
        )
    return DoctorCheck(name="package", status="ok", message=f"retail-scrapers {version}")


def check_playwright_import() -> DoctorCheck:
    try:
        import playwright  # noqa: F401
    except Exception as exc:
        return DoctorCheck(
            name="playwright",
            status="error",
            message=f"Playwright import failed: {exc}",
        )
    return DoctorCheck(name="playwright", status="ok", message="Playwright package is importable")


def check_project_root(root: Path | None = None) -> DoctorCheck:
    base = root or Path.cwd()
    expected = [base / "pyproject.toml", base / "src" / "retail_scrapers"]
    ok = all(path.exists() for path in expected)
    return DoctorCheck(
        name="project-root",
        status=_status(ok),
        message=str(base) if ok else f"{base} does not look like the project root",
    )


def check_channels() -> DoctorCheck:
    channels = [str(row["id"]) for row in list_channels()]
    ok = bool(channels)
    return DoctorCheck(
        name="channels",
        status=_status(ok),
        message=", ".join(channels) if channels else "no adapters registered",
    )


async def check_chromium_launch() -> DoctorCheck:
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        return DoctorCheck(
            name="chromium",
            status="error",
            message=f"Playwright import failed: {exc}",
        )

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
    except Exception as exc:
        return DoctorCheck(
            name="chromium",
            status="warning",
            message=(
                f"Chromium launch failed. Try: python -m playwright install chromium. Detail: {exc}"
            ),
        )
    return DoctorCheck(name="chromium", status="ok", message="Chromium launches successfully")


async def run_doctor(*, check_browser: bool = True, root: Path | None = None) -> dict[str, Any]:
    checks = [
        check_python(),
        check_package_metadata(),
        check_playwright_import(),
        check_project_root(root),
        check_channels(),
    ]
    if check_browser:
        checks.append(await check_chromium_launch())

    has_error = any(check.status == "error" for check in checks)
    has_warning = any(check.status == "warning" for check in checks)
    if has_error:
        status = "error"
    elif has_warning:
        status = "warning"
    else:
        status = "ok"
    return {"status": status, "checks": [check.to_dict() for check in checks]}
