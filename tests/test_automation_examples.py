from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_github_actions_template_is_copy_paste_ready():
    template = ROOT / "examples" / "github-actions" / "scheduled-scrape.yml"
    text = template.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "schedule:" in text
    assert "retail-scrape catalog" in text
    assert "retail-scrape prices" in text
    assert "actions/upload-artifact@v4" in text
    assert ".github/workflows" not in str(template)
