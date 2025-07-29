# PyPI Publishing Guide

## Preparation for PyPI Release

### 1. Update Version
Update version in `pyproject.toml`:
```toml
version = "0.3.0"  # Increment as needed
```

### 2. Build Package
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# dist/apc_protocol-0.3.0-py3-none-any.whl
# dist/apc_protocol-0.3.0.tar.gz
```

### 3. Test Package Locally
```bash
# Install from local build
pip install dist/apc_protocol-0.3.0-py3-none-any.whl

# Test basic functionality
python -c "from apc import Worker, Conductor; print('Success!')"
```

### 4. Upload to TestPyPI (Optional)
```bash
# Upload to test PyPI first
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ apc-protocol
```

### 5. Upload to PyPI
```bash
# Upload to production PyPI
twine upload dist/*
```

### 6. Verify Publication
```bash
# Install from PyPI
pip install apc-protocol

# Test installation
python scripts/test_package.py
```

## Release Checklist

- [ ] All tests pass: `python scripts/test_package.py`
- [ ] Demo works: `python scripts/demo.py`
- [ ] Examples work: `python examples/basic/simple_grpc.py`
- [ ] Documentation updated
- [ ] Version bumped in `pyproject.toml`
- [ ] README has correct installation instructions
- [ ] All links in README work
- [ ] GitHub repository is clean and organized
- [ ] License file exists and is correct

## GitHub Release Process

### 1. Create Git Tag
```bash
git tag v0.3.0
git push origin v0.3.0
```

### 2. Create GitHub Release
- Go to GitHub Releases page
- Click "Create a new release"
- Select tag v0.3.0
- Title: "APC Protocol v0.3.0"
- Description: Include changelog and key features

### 3. Attach Release Assets
- Upload the wheel file: `apc_protocol-0.3.0-py3-none-any.whl`
- Upload the source distribution: `apc_protocol-0.3.0.tar.gz`

## Post-Release Tasks

1. **Update README badges** with new version
2. **Announce on social media/forums**
3. **Update documentation** if needed
4. **Create examples** for new features
5. **Monitor PyPI download stats**
6. **Respond to issues** and feedback

## Automated Publishing (GitHub Actions)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        user: __token__
        password: ${{ secrets.PYPI_API_TOKEN }}
```

This will automatically publish to PyPI when you create a GitHub release.
