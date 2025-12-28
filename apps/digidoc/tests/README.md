# DigiDoc Test Suite

**Purpose**: Organized test suite for DigiDoc OCR Service following best practices.

## Directory Structure

```
tests/
├── unit/           # Fast, isolated unit tests
├── integration/    # Integration tests (may require external services)
├── e2e/            # End-to-end tests (full system)
└── fixtures/       # Test data and fixtures
```

## Running Tests

### Run all tests with coverage:
```bash
pytest
```

### Run specific test categories:
```bash
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m e2e              # End-to-end tests only
```

### Run with coverage report:
```bash
pytest --cov=ocr_service --cov-report=html
# Open htmlcov/index.html in browser
```

### Run specific test file:
```bash
pytest tests/unit/test_config.py
```

## Test Organization

### Unit Tests (`tests/unit/`)
- Fast, isolated tests
- No external dependencies
- Mock external services
- Test individual functions/classes

### Integration Tests (`tests/integration/`)
- Test component interactions
- May require database, Redis, etc.
- Test API endpoints
- Test queue operations

### E2E Tests (`tests/e2e/`)
- Full system tests
- Test complete workflows
- May require all services running
- Test user-facing features

## Coverage Goals

- **Minimum**: 60% overall coverage
- **Critical paths**: 80%+ coverage (preprocessing, matching, extraction)
- **Non-critical**: 40%+ coverage (utilities, helpers)

## Writing Tests

### Example Unit Test:
```python
import pytest
from ocr_service.utils.image_preprocessing import ImagePreprocessor

def test_deskew_basic():
    """Test basic deskew functionality."""
    # Arrange
    image = load_test_image()
    
    # Act
    result = ImagePreprocessor.preprocess(image)
    
    # Assert
    assert result is not None
    assert result.shape == image.shape
```

### Using Fixtures:
```python
def test_config_loading(config):
    """Test configuration loading."""
    assert config.preprocessing is not None
    assert config.paths.storage_base is not None
```

## Migration from Old Tests

Old test files in `ocr_service/` will be gradually migrated to this structure:
- `test_config.py` → `tests/unit/test_config.py`
- `test_preprocessing.py` → `tests/unit/test_preprocessing.py`
- `test_file_utils.py` → `tests/unit/test_file_utils.py`
- `test_full_pipeline.py` → `tests/integration/test_pipeline.py`
- `test_gui_components.py` → `tests/integration/test_gui.py`

## Test Data

Place test images, sample data, and fixtures in `tests/fixtures/`.

**Note**: Do not commit large test files. Use `.gitignore` to exclude large fixtures.

