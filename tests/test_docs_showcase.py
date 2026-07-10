from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readmes_link_to_showcase_docs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    assert "[Project showcase](docs/showcase.md)" in readme
    assert "[项目橱窗](docs/showcase.zh-CN.md)" in readme_zh


def test_showcase_docs_cover_the_three_core_loops():
    showcase = (ROOT / "docs" / "showcase.md").read_text(encoding="utf-8")
    showcase_zh = (ROOT / "docs" / "showcase.zh-CN.md").read_text(encoding="utf-8")

    for text in (showcase, showcase_zh):
        assert "retail-scrape catalog" in text
        assert "retail-scrape scaffold" in text
        assert "retail-scrape schema catalog --format markdown" in text
        assert "examples/github-actions/scheduled-scrape.yml" in text
        assert "retail-scrape-output-*" in text
