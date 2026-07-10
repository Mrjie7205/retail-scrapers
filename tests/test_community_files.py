from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEMPLATES = ROOT / ".github" / "ISSUE_TEMPLATE"


def test_bug_report_collects_reproduction_and_safety_context():
    text = (ISSUE_TEMPLATES / "bug_report.yml").read_text(encoding="utf-8")

    assert "name: Adapter bug report" in text
    assert "id: channel" in text
    assert "id: command" in text
    assert "id: expected" in text
    assert "id: actual" in text
    assert "credentials, cookies, personal information" in text


def test_channel_request_collects_public_adapter_entry_points():
    text = (ISSUE_TEMPLATES / "channel_request.yml").read_text(encoding="utf-8")

    assert "name: New retailer request" in text
    assert "id: catalog_url" in text
    assert "id: product_url" in text
    assert "id: desired_modes" in text
    assert "id: discovery" in text
    assert "work without login, cookies, or private credentials" in text


def test_issue_forms_are_the_default_support_path():
    text = (ISSUE_TEMPLATES / "config.yml").read_text(encoding="utf-8")

    assert "blank_issues_enabled: false" in text
    assert "Responsible use reminder" in text
