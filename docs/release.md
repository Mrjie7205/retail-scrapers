# Release checklist

This project is prepared for PyPI publishing, but publishing should happen only after the repository home is final.

## Before the first publish

1. Decide whether the package should live under a personal account or a neutral organization.
2. Add final project URLs to `pyproject.toml`.
3. Create a PyPI project and enable Trusted Publishing for the GitHub Actions release workflow.
4. Create a GitHub release or push a version tag such as `v0.1.0`.
5. Confirm the package builds locally.

## Local release checks

```bash
ruff check .
mypy src/retail_scrapers
pytest
python -m pip wheel . --no-deps --wheel-dir dist
python -m build
python -m retail_scrapers channels
```

## Versioning

- Patch version: parser fixes, retry tuning, and adapter maintenance.
- Minor version: new channel adapters or new public output fields.
- Major version: breaking changes to CLI flags, Python API, or record models.
