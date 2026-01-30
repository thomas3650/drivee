# CI/CD Pipeline Documentation

## Overview

This directory contains GitHub Actions workflows for automated quality checks on pull requests and pushes to main branches.

## Workflows

### `pr-validation.yml` - Comprehensive PR Validation

Runs automatically on:
- Pull requests to `main` or `master` branches
- Direct pushes to `main` or `master` branches

## Quality Checks

### 1. **Linting & Formatting** (Required ✅)
- **Tool**: Ruff
- **Checks**:
  - Code style compliance (PEP 8)
  - Import sorting
  - Common Python mistakes
  - Formatting consistency
- **Fails on**: Any linting errors or formatting issues
- **Fix locally**:
  ```bash
  ruff check .
  ruff format .
  ```

### 2. **Type Checking** (Advisory ⚠️)
- **Tool**: mypy
- **Checks**:
  - Type hint correctness
  - Type consistency
  - Missing type annotations
- **Fails on**: Currently set to advisory (won't fail build)
- **Fix locally**:
  ```bash
  mypy . --ignore-missing-imports --check-untyped-defs
  ```

### 3. **Home Assistant Validation** (Required ✅)
- **Tool**: hassfest (official HA validator)
- **Checks**:
  - `manifest.json` structure and requirements
  - `strings.json` format and translations
  - Integration metadata
  - Dependencies compatibility
- **Fails on**: Any HA-specific validation errors
- **Fix locally**: Install Home Assistant and run hassfest

### 4. **Tests** (Advisory ⚠️)
- **Tool**: pytest
- **Checks**:
  - Unit tests for coordinator
  - Cache behavior tests
  - Error handling tests
- **Runs on**: Python 3.11 and 3.12
- **Fails on**: Currently advisory (requires HA dev environment)
- **Fix locally**:
  ```bash
  pip install -r requirements_test.txt
  pytest tests/ -v
  ```

### 5. **Manifest Validation** (Required ✅)
- **Checks**:
  - `manifest.json` is valid JSON
  - `strings.json` is valid JSON
  - Required files exist (`__init__.py`, `const.py`, etc.)
- **Fails on**: Missing or malformed files
- **Fix locally**: Validate JSON files manually

### 6. **Security Checks** (Advisory ⚠️)
- **Tool**: pip-audit
- **Checks**:
  - Known vulnerabilities in dependencies
  - CVE database checks
- **Fails on**: Currently advisory
- **Fix locally**:
  ```bash
  pip install pip-audit
  pip-audit -r requirements_test.txt
  ```

### 7. **Code Quality Metrics** (Informational ℹ️)
- **Tool**: radon
- **Reports**:
  - Cyclomatic complexity
  - Maintainability index
- **Fails on**: Never (informational only)
- **View locally**:
  ```bash
  pip install radon
  radon cc . -a
  radon mi .
  ```

### 8. **Spell Check** (Advisory ⚠️)
- **Tool**: codespell
- **Checks**: Common spelling mistakes in code and comments
- **Fails on**: Currently advisory
- **Fix locally**:
  ```bash
  codespell --ignore-words-list=hass .
  ```

### 9. **Summary** (Required ✅)
- Aggregates results from all required checks
- **Passes if**: All required checks pass
- **Fails if**: Any required check fails

## Required vs Advisory Checks

### Required (Must Pass) ✅
These checks **must** pass for the PR to be merged:
1. Linting & Formatting
2. Home Assistant Validation (hassfest)
3. Manifest Validation

### Advisory (Nice to Have) ⚠️
These checks run but don't block merging:
1. Type Checking (transitioning to required)
2. Tests (requires HA dev environment)
3. Security Checks (informational)

### Informational (Metrics) ℹ️
These provide insights but never fail:
1. Code Quality Metrics
2. Spell Check

## Local Development

### Before Committing

Run these commands locally to catch issues before pushing:

```bash
# 1. Format code
ruff format .

# 2. Check linting
ruff check .

# 3. Validate JSON files
python -c "import json; json.load(open('manifest.json'))"
python -c "import json; json.load(open('strings.json'))"

# 4. Run type checking (optional)
mypy . --ignore-missing-imports

# 5. Run tests (if in HA dev environment)
pytest tests/ -v
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks:

```bash
pip install pre-commit
pre-commit install
```

This will run:
- Ruff formatting and linting
- YAML validation
- JSON validation
- Trailing whitespace fixes
- Spell checking

## Workflow Configuration

### Adding New Checks

To add a new check to the pipeline:

1. Add a new job to `.github/workflows/pr-validation.yml`
2. Set `continue-on-error: true` for advisory checks
3. Add to the `needs` array in the `summary` job if required
4. Document the check in this README

### Modifying Required Checks

To make an advisory check required:

1. Remove `continue-on-error: true` from the job
2. Add the job to `needs` array in the `summary` job
3. Update this documentation

## Troubleshooting

### Workflow Not Running

- Check that the workflow file is in `.github/workflows/`
- Verify YAML syntax is correct
- Ensure you're creating a PR to `main` or `master`

### Check Failing Locally But Passing in CI

- Ensure you're using the same Python version (3.11+)
- Check for platform-specific issues (Windows vs Linux)
- Verify all dependencies are installed

### Check Passing Locally But Failing in CI

- May be due to environment differences
- Check GitHub Actions logs for detailed error messages
- Verify file line endings (CRLF vs LF)

## CI/CD Best Practices

1. **Run checks locally first** - Catch issues before pushing
2. **Keep checks fast** - Slow CI discourages frequent commits
3. **Make failures clear** - Good error messages help debugging
4. **Don't over-check** - Balance thoroughness with practicality
5. **Use caching** - Speed up dependency installation

## Metrics and Goals

### Current Status
- Required checks: 3 (Lint, hassfest, manifest)
- Advisory checks: 3 (Type, tests, security)
- Average CI run time: ~5-8 minutes

### Goals
- Move type checking to required (after fixing all type errors)
- Achieve >80% test coverage
- Keep CI run time under 10 minutes

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
