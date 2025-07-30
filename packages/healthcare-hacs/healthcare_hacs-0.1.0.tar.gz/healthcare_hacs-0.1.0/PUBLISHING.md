# HACS PyPI Publishing Guide

This guide covers how to publish HACS packages to PyPI (Python Package Index).

## 📋 Prerequisites

### 1. PyPI Account Setup
- Create accounts on both [PyPI](https://pypi.org/account/register/) and [TestPyPI](https://test.pypi.org/account/register/)
- Set up API tokens for secure authentication
- Configure `~/.pypirc` file with your credentials

### 2. Environment Setup
```bash
# Install publishing dependencies
uv add --dev twine keyring

# Verify tools are available
uv run python -m twine --version
```

### 3. Authentication Configuration
Create `~/.pypirc` file:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-token-here
```

## 🚀 Publishing Process

### Option 1: Using the Publishing Script (Recommended)

```bash
# 1. Validate all packages
python publish.py --check

# 2. Test publish to TestPyPI
python publish.py --test

# 3. Publish to production PyPI
python publish.py --production

# 4. Publish specific package only
python publish.py --package hacs-core --production
```

### Option 2: Manual Publishing

#### Step 1: Validate Package Configuration
```bash
# Check each package has proper metadata
for package in packages/*/; do
    echo "Checking $package"
    cd "$package"
    uv build
    uv run python -m twine check dist/*
    cd ../..
done
```

#### Step 2: Build Packages
```bash
# Build in dependency order
packages=("hacs-core" "hacs-models" "hacs-fhir" "hacs-tools" "hacs-api" "hacs-cli")

for package in "${packages[@]}"; do
    echo "Building $package"
    cd "packages/$package"
    rm -rf dist/
    uv build
    cd ../..
done

# Build main package
uv build
```

#### Step 3: Test on TestPyPI
```bash
# Upload to TestPyPI first
for package in "${packages[@]}"; do
    cd "packages/$package"
    uv run python -m twine upload --repository testpypi dist/*
    cd ../..
done

# Upload main package
uv run python -m twine upload --repository testpypi dist/*
```

#### Step 4: Verify TestPyPI Installation
```bash
# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ hacs-core
pip install --index-url https://test.pypi.org/simple/ hacs
```

#### Step 5: Publish to PyPI
```bash
# Upload to production PyPI
for package in "${packages[@]}"; do
    cd "packages/$package"
    uv run python -m twine upload dist/*
    cd ../..
done

# Upload main package
uv run python -m twine upload dist/*
```

## 📦 Package Structure

HACS follows a multi-package architecture:

```
hacs/                           # Main workspace package
├── packages/hacs-core/         # Core models and base classes
├── packages/hacs-models/       # Clinical models (Patient, Observation, etc.)
├── packages/hacs-fhir/         # FHIR integration
├── packages/hacs-tools/        # CRUD tools and adapters
├── packages/hacs-api/          # FastAPI service
└── packages/hacs-cli/          # Command-line interface
```

### Publishing Order
Packages must be published in dependency order:
1. `hacs-core` (no dependencies)
2. `hacs-models` (depends on hacs-core)
3. `hacs-fhir` (depends on hacs-core, hacs-models)
4. `hacs-tools` (depends on hacs-core, hacs-models, hacs-fhir)
5. `hacs-api` (depends on all above)
6. `hacs-cli` (depends on all above)
7. `hacs` (main package, depends on all above)

## 🔍 Pre-Publication Checklist

### Package Metadata
- [ ] Correct version number in `pyproject.toml`
- [ ] Author information updated to "Solano Todeschini"
- [ ] License specified as "Apache-2.0"
- [ ] Keywords and classifiers properly set
- [ ] Repository URLs point to `https://github.com/solanovisitor/hacs`
- [ ] README.md exists and is properly formatted

### Code Quality
- [ ] All tests pass: `uv run pytest`
- [ ] Type checking passes: `uv run pyright`
- [ ] Linting passes: `uv run ruff check`
- [ ] No security vulnerabilities
- [ ] Documentation is up to date

### Dependencies
- [ ] All dependencies properly specified
- [ ] Version constraints are appropriate
- [ ] Workspace dependencies correctly configured
- [ ] No circular dependencies

### Build Validation
- [ ] Package builds successfully: `uv build`
- [ ] Built package passes validation: `twine check dist/*`
- [ ] Package installs correctly from wheel
- [ ] Import statements work correctly

## 🏷️ Version Management

HACS uses semantic versioning (SemVer):
- `MAJOR.MINOR.PATCH` format
- Current version: `0.1.0`
- All packages maintain version synchronization

### Version Bumping
```bash
# Update version in all pyproject.toml files
# This should be done consistently across all packages

# Example for version 0.1.1
find . -name "pyproject.toml" -exec sed -i 's/version = "0.1.0"/version = "0.1.1"/' {} \;
```

## 📊 Post-Publication Verification

### 1. Installation Testing
```bash
# Test installation from PyPI
pip install hacs
pip install hacs-core
pip install hacs-models
pip install hacs-fhir
pip install hacs-tools
pip install hacs-api
pip install hacs-cli

# Verify imports work
python -c "import hacs_core; print('✅ hacs-core')"
python -c "import hacs_models; print('✅ hacs-models')"
python -c "import hacs_fhir; print('✅ hacs-fhir')"
python -c "import hacs_tools; print('✅ hacs-tools')"
python -c "import hacs_api; print('✅ hacs-api')"
python -c "import hacs_cli; print('✅ hacs-cli')"
```

### 2. Functionality Testing
```bash
# Test CLI
hacs --help

# Test API
python -c "from hacs_api.main import app; print('✅ API imports')"

# Test core functionality
python -c "
from hacs_models import Patient
from hacs_core import Actor
patient = Patient(display_name='Test')
actor = Actor(actor_id='test', actor_type='clinician')
print('✅ Core functionality works')
"
```

### 3. Documentation Verification
- [ ] PyPI package pages display correctly
- [ ] README renders properly on PyPI
- [ ] Links to documentation work
- [ ] Installation instructions are accurate

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```bash
# Error: 403 Forbidden
# Solution: Check API token in ~/.pypirc
keyring set https://upload.pypi.org/legacy/ __token__
```

#### 2. Package Already Exists
```bash
# Error: File already exists
# Solution: You cannot overwrite existing versions
# Increment version number and republish
```

#### 3. Dependency Resolution
```bash
# Error: Package dependencies cannot be resolved
# Solution: Ensure all dependencies are published first
# Check dependency order in PACKAGE_ORDER
```

#### 4. Build Failures
```bash
# Error: Build failed
# Solution: Check pyproject.toml configuration
uv build --verbose  # For detailed error messages
```

#### 5. Metadata Validation
```bash
# Error: Invalid metadata
# Solution: Validate with twine
twine check dist/*
```

## 🛡️ Security Considerations

### API Token Security
- Use API tokens instead of passwords
- Store tokens securely (use keyring)
- Rotate tokens regularly
- Use separate tokens for TestPyPI and PyPI

### Package Signing
```bash
# Sign packages with GPG (optional but recommended)
gpg --detach-sign -a dist/*.whl
twine upload dist/* --sign
```

### Vulnerability Scanning
```bash
# Scan for vulnerabilities before publishing
uv run safety check
uv run bandit -r packages/
```

## 📈 Monitoring and Maintenance

### Package Statistics
- Monitor download statistics on PyPI
- Track package usage and adoption
- Monitor for security vulnerabilities
- Keep dependencies updated

### Update Process
1. Update code and tests
2. Update version numbers
3. Update changelog
4. Test thoroughly
5. Publish to TestPyPI
6. Verify installation
7. Publish to PyPI
8. Update documentation

## 🎯 Success Metrics

After successful publication, verify:
- [ ] All packages appear on PyPI
- [ ] Installation works from PyPI
- [ ] Documentation links work
- [ ] Package metadata is correct
- [ ] Dependencies resolve properly
- [ ] Examples and tutorials work

## 📚 Additional Resources

- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Twine Documentation](https://twine.readthedocs.io/en/latest/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [Semantic Versioning](https://semver.org/)

## 🤝 Contributing to Publishing

If you're helping with package publishing:
1. Follow this guide exactly
2. Test on TestPyPI first
3. Verify all packages work together
4. Update documentation as needed
5. Coordinate with maintainers for production releases

---

**Note**: Publishing to PyPI makes packages publicly available. Always test thoroughly on TestPyPI first! 