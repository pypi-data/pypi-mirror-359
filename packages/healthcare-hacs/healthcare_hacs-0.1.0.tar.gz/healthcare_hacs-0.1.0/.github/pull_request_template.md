# Pull Request

## 📋 Description

**Brief description of changes:**

**Related Issue(s):**
- Fixes #issue_number
- Closes #issue_number
- Related to #issue_number

## 🔄 Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🧪 Test improvements
- [ ] 🔧 Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🏥 Healthcare/FHIR compliance improvement

## 🏥 Healthcare Impact

**Clinical relevance and safety considerations:**
- [ ] No clinical impact
- [ ] Improves clinical workflow
- [ ] Affects patient data handling
- [ ] Impacts FHIR compliance
- [ ] Requires clinical validation

**FHIR Compliance:**
- [ ] No FHIR changes
- [ ] Maintains FHIR compliance
- [ ] Improves FHIR compliance
- [ ] Requires FHIR validation

## 🧪 Testing

**Test coverage:**
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Performance tests added/updated
- [ ] FHIR round-trip tests added/updated
- [ ] All existing tests pass

**Manual testing performed:**
- [ ] Tested locally with sample data
- [ ] Tested CLI commands (if applicable)
- [ ] Tested API endpoints (if applicable)
- [ ] Tested protocol adapters (if applicable)

## 📊 Performance Impact

**Performance considerations:**
- [ ] No performance impact
- [ ] Performance improvement
- [ ] Potential performance regression (explained below)
- [ ] Performance benchmarks maintained (<300ms CRUD operations)

**Benchmark results (if applicable):**
```
CREATE: X.XXms
READ: X.XXms
UPDATE: X.XXms
DELETE: X.XXms
```

## 📚 Documentation

**Documentation updates:**
- [ ] Code comments added/updated
- [ ] API documentation updated
- [ ] Module documentation updated
- [ ] Examples added/updated
- [ ] README updated (if needed)
- [ ] Changelog updated

## 🔒 Security Considerations

**Security impact:**
- [ ] No security impact
- [ ] Improves security
- [ ] Requires security review
- [ ] Affects Actor permissions
- [ ] Impacts audit trails

## 🤖 Agent Integration

**Agent framework impact:**
- [ ] No agent impact
- [ ] Improves agent capabilities
- [ ] Affects memory/evidence systems
- [ ] Updates protocol adapters
- [ ] Changes LLM integration

## 📦 Package Impact

**Which packages are affected:**
- [ ] hacs-core
- [ ] hacs-models
- [ ] hacs-fhir
- [ ] hacs-tools
- [ ] hacs-cli
- [ ] hacs-api

## 🔄 Breaking Changes

**List any breaking changes:**
- None

**Migration path (if breaking changes):**
```python
# Before
old_api_usage()

# After
new_api_usage()
```

## 📝 Additional Notes

**Additional context or notes for reviewers:**

## ✅ Checklist

**Code Quality:**
- [ ] Code follows HACS style guidelines
- [ ] Code is properly typed (100% type coverage)
- [ ] Code passes ruff linting (`uv run ruff check .`)
- [ ] Code is formatted (`uv run ruff format .`)
- [ ] Code passes type checking (`uv run pyright`)

**Testing:**
- [ ] All tests pass (`uv run pytest`)
- [ ] Integration tests pass (`uv run python tests/test_integration_e2e.py`)
- [ ] New tests cover the changes
- [ ] Performance benchmarks maintained

**Healthcare Compliance:**
- [ ] FHIR compliance maintained/improved
- [ ] Clinical accuracy validated (if applicable)
- [ ] Privacy considerations addressed
- [ ] Audit requirements met

**Documentation:**
- [ ] Code is self-documenting with clear names
- [ ] Public APIs have docstrings
- [ ] Examples provided for new features
- [ ] Documentation updated for changes

**Community:**
- [ ] Changes align with project goals
- [ ] Backward compatibility considered
- [ ] Community impact assessed
- [ ] Contribution guidelines followed

## 🏷️ Labels

**Suggested labels:**
- Component: `core`, `models`, `fhir`, `tools`, `cli`, `api`
- Type: `bug`, `feature`, `docs`, `performance`, `refactor`
- Priority: `low`, `medium`, `high`, `critical`
- Healthcare: `fhir-compliance`, `clinical-safety`, `agent-integration`

---

**Thank you for contributing to HACS! 🎉**

Your contribution helps advance healthcare AI and improves patient care through better agent communication standards. 