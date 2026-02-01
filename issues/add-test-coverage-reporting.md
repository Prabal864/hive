# Issue: Add Test Coverage Reporting and Improve Coverage for Core Framework

## Summary

The Hive project lacks automated test coverage reporting, making it difficult to:
1. Track which parts of the codebase are well-tested vs. untested
2. Ensure new contributions include adequate tests
3. Identify critical gaps in test coverage for production-critical code
4. Maintain and improve code quality over time

This issue proposes adding pytest-cov integration and establishing coverage baselines for both the `core/` framework and `tools/` packages.

## Current State

### What Exists
- ✅ Core framework has basic test infrastructure (`core/tests/`)
- ✅ Tools package has test suite (`tools/tests/`)
- ✅ CI runs tests via `make test` (core only)
- ✅ `pyproject.toml` files configured for both packages

### What's Missing
- ❌ No coverage reporting configured
- ❌ No coverage metrics visible in CI
- ❌ No coverage baseline requirements
- ❌ No coverage badges in README
- ❌ Unknown which modules lack tests

## Problem Impact

**For Maintainers:**
- Cannot objectively assess PR test quality
- Risk accepting code with insufficient tests
- No visibility into technical debt hotspots

**For Contributors:**
- Unclear how much testing is "enough"
- Cannot verify their tests are comprehensive
- May waste time over-testing well-covered code

**For Users:**
- Higher risk of bugs in untested code paths
- Lower confidence in framework reliability

## Proposed Solution

### Phase 1: Add Coverage Infrastructure

**1. Add pytest-cov to dependencies**

`core/pyproject.toml`:
```toml
dependencies = [
  # ... existing deps ...
  "pytest-cov>=5.0.0",
]
```

`tools/pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-asyncio>=0.21.0",
  "pytest-cov>=5.0.0",  # NEW
]
```

**2. Add coverage configuration**

`core/pyproject.toml`:
```toml
[tool.coverage.run]
source = ["framework"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__main__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

`tools/pyproject.toml`:
```toml
[tool.coverage.run]
source = ["src/aden_tools"]
omit = [
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

**3. Update Makefile**

```makefile
test: ## Run all tests with coverage
	cd core && python -m pytest tests/ -v --cov --cov-report=term-missing --cov-report=html
	cd tools && python -m pytest tests/ -v --cov --cov-report=term-missing --cov-report=html

test-core: ## Run core tests with coverage
	cd core && python -m pytest tests/ -v --cov --cov-report=term-missing

test-tools: ## Run tools tests with coverage
	cd tools && python -m pytest tests/ -v --cov --cov-report=term-missing

coverage-report: ## Generate HTML coverage reports
	cd core && python -m pytest tests/ --cov --cov-report=html
	cd tools && python -m pytest tests/ --cov --cov-report=html
	@echo "Coverage reports generated:"
	@echo "  Core: core/htmlcov/index.html"
	@echo "  Tools: tools/htmlcov/index.html"
```

**4. Update .gitignore**

```gitignore
# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.pytest_cache/
```

### Phase 2: Establish Coverage Baselines

After implementing Phase 1, run coverage and document baselines:

```bash
make test-core
make test-tools
```

Create a `TESTING.md` file documenting:
- Current coverage percentages
- Minimum acceptable coverage for new code (e.g., 80%)
- High-priority modules requiring coverage improvement
- Testing best practices

### Phase 3: CI Integration (Future Enhancement)

Add coverage reporting to GitHub Actions:
- Generate coverage reports in CI
- Post coverage comments on PRs
- Enforce minimum coverage thresholds
- Optional: Integrate with Codecov/Coveralls for badges

## Implementation Checklist

- [ ] Add `pytest-cov` to core dependencies
- [ ] Add `pytest-cov` to tools dev dependencies
- [ ] Add coverage configuration to `core/pyproject.toml`
- [ ] Add coverage configuration to `tools/pyproject.toml`
- [ ] Update Makefile with coverage commands
- [ ] Update `.gitignore` to exclude coverage artifacts
- [ ] Run coverage analysis and document baselines
- [ ] Create `TESTING.md` with coverage guidelines
- [ ] Update `CONTRIBUTING.md` to reference coverage requirements
- [ ] (Optional) Add coverage badge to README.md

## Benefits

1. **Objective Quality Metrics**: Coverage percentage provides concrete data
2. **Better PRs**: Contributors can verify their tests are comprehensive
3. **Reduced Bugs**: Higher coverage correlates with fewer production issues
4. **Technical Debt Visibility**: Easily identify untested legacy code
5. **Confidence**: Users and maintainers trust well-tested code

## Related Issues

- [#2805](https://github.com/adenhq/hive/issues/2805) - Tool integrations (coverage ensures new tools are tested)
- Roadmap item: "Eval System" - requires strong test infrastructure

## Testing Strategy

**This change is self-testing:**
1. Run `make test-core` and verify coverage report is generated
2. Run `make test-tools` and verify coverage report is generated
3. Check that `core/htmlcov/index.html` exists and displays coverage
4. Verify `make check` still passes (linting unchanged)

## Notes

- Start with reporting only; enforcement can come later
- Don't require 100% coverage initially
- Focus on critical paths first (graph executor, LLM integration, credentials)
- Coverage is a tool, not a goal - quality matters more than percentage

## Success Criteria

✅ Coverage reports generate successfully for core and tools
✅ Coverage data is easily accessible locally
✅ Documentation guides contributors on coverage expectations
✅ No breaking changes to existing workflow
