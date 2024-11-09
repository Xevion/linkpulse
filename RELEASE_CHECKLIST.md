# Release Checklist

1. Ensure `backend/pyproject.toml` and `frontend/package.json` have the correct version number for the upcoming release.
2. Ensure `CHANGELOG.md` contains all changes for the upcoming release, with the correct version number and date labeled.
   - `Unreleased` section should not exist.
   - The version should match `pyproject.toml` and `package.json`.
3. Ensure all tests pass locally, as well as the CI/CD pipeline.
4. Correct all linting errors and warnings.
