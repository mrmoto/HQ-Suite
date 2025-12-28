# DigiDoc Testing Guide

This guide explains how to test the DigiDoc application components.

## Prerequisites

Before running tests, ensure you have:

1. **Python 3.8+** installed
2. **Dependencies installed**:
   ```bash
   pip install -r requirements_ocr.txt
   ```

   For full testing (including image processing), you'll also need:
   ```bash
   pip install opencv-python numpy pillow
   ```

## Test Suites

### 1. Configuration Tests

Tests the configuration system:
- Config file loading
- Environment variable overrides
- Variable substitution
- Type conversion

**Run:**
```bash
python3 ocr_service/test_config.py
```

### 2. Full Pipeline Tests

Tests the complete processing pipeline:
- Configuration loading
- File storage utilities
- Image preprocessing (requires OpenCV)
- Structural fingerprinting (requires OpenCV)
- Queue utilities
- Full processing workflow (requires OpenCV)

**Run:**
```bash
python3 ocr_service/test_full_pipeline.py
```

**Note:** Tests that require OpenCV will be skipped if it's not installed, but other tests will still run.

### 3. GUI Component Tests

Tests GUI utilities without requiring Streamlit:
- Queue utilities
- Visualization utilities
- Image loading
- Metadata operations

**Run:**
```bash
python3 ocr_service/test_gui_components.py
```

### 4. Run All Tests

Run all test suites with a single command:

**Run:**
```bash
./ocr_service/run_tests.sh
```

Or:
```bash
bash ocr_service/run_tests.sh
```

## Testing Streamlit GUI

To test the Streamlit GUI interactively:

1. **Start the Streamlit app:**
   ```bash
   cd /Users/scottroberts/Library/CloudStorage/Dropbox/cloud_storage/DigiDoc
   streamlit run ocr_service/gui/app.py
   ```

2. **Access the GUI:**
   - Open your browser to the URL shown (typically `http://localhost:8501`)
   - Navigate between "Queue View" and "Visual Match" pages
   - Test queue item selection and visualization

## Manual Testing Checklist

### Configuration
- [ ] Config file loads without errors
- [ ] Environment variable overrides work
- [ ] Paths are correctly expanded to absolute paths (e.g., `~/Dropbox/...` → `/Users/username/Dropbox/...`)
- [ ] All file operations use absolute paths after expansion
- [ ] All sections are accessible

**Note**: Configuration paths using `~` are expanded to absolute paths during configuration loading. All apps use absolute paths internally after expansion. See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" for requirements.

### File Storage
- [ ] Queue item directories are created correctly
- [ ] Original files are saved
- [ ] Preprocessed images are saved
- [ ] Match visualizations are saved
- [ ] Metadata files are saved

### Image Preprocessing
- [ ] Images are deskewed correctly
- [ ] Denoising works
- [ ] Binarization works
- [ ] Scale normalization works
- [ ] Border removal works

### Template Matching
- [ ] Structural fingerprints are computed
- [ ] Fingerprints use ratios (not absolute pixels)
- [ ] Fingerprint comparison works
- [ ] Match scores are between 0.0 and 1.0

### GUI
- [ ] Queue view displays items
- [ ] Status filtering works
- [ ] Thumbnails display correctly
- [ ] Navigation to visual match works
- [ ] Three-panel view displays all images
- [ ] Images are proportionally scaled
- [ ] Match metadata displays correctly

## Expected Test Results

When all dependencies are installed, you should see:

```
✅ Configuration Loading: PASSED
✅ File Storage Utilities: PASSED
✅ Image Preprocessing: PASSED
✅ Structural Fingerprinting: PASSED
✅ Queue Utilities: PASSED
✅ Full Processing Workflow: PASSED
```

If OpenCV is not installed, some tests will be skipped but marked as passed (since they can't run without dependencies).

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
1. Check that you're in the correct directory (DigiDoc root)
2. Verify dependencies are installed: `pip install -r requirements_ocr.txt`
3. For image processing tests, install OpenCV: `pip install opencv-python`

### Configuration Errors

If config loading fails:
1. Verify `digidoc_config.yaml` exists in the DigiDoc root
2. Check file permissions
3. Verify YAML syntax is correct

### Path Errors

If file paths are incorrect:
1. Check `digidoc_config.yaml` paths section
2. Verify `storage_base` is set correctly
3. Check that directories exist or can be created

## Continuous Integration

For CI/CD pipelines, run:

```bash
# Install dependencies
pip install -r requirements_ocr.txt

# Run all tests
./ocr_service/run_tests.sh

# Exit code will be 0 if all tests pass, 1 otherwise
```
