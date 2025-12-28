#!/usr/bin/env python3
"""
DigiDoc Configuration System Test Script

Validates that the configuration system works correctly:
- All config sections load correctly
- Environment variable overrides work
- Variable substitution works
- Types are correct
- Can be imported and used by other modules
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ocr_service.config import get_config, reload_config


def test_all_sections_exist():
    """Test that all 8 required sections are accessible."""
    print("=" * 60)
    print("Test 1: All Config Sections Exist")
    print("=" * 60)
    
    config = reload_config()
    
    required_sections = [
        'thresholds',
        'scoring',
        'preprocessing',
        'paths',
        'api',
        'queue',
        'database',
        'llm'
    ]
    
    missing = []
    for section in required_sections:
        if not hasattr(config, section):
            missing.append(section)
        else:
            print(f"  ✓ {section} section exists")
    
    if missing:
        print(f"  ✗ Missing sections: {missing}")
        return False
    
    print(f"\n  ✓ All {len(required_sections)} sections are accessible")
    return True


def test_section_values():
    """Test that key values from each section are accessible and correct types."""
    print("\n" + "=" * 60)
    print("Test 2: Section Values and Types")
    print("=" * 60)
    
    config = reload_config()
    
    tests = [
        # (section.key, expected_type, description)
        ('thresholds.auto_match', float, 'Auto-match threshold'),
        ('thresholds.partial_match_min', float, 'Partial match min'),
        ('preprocessing.target_dpi', int, 'Target DPI'),
        ('preprocessing.deskew_enabled', bool, 'Deskew enabled'),
        ('preprocessing.denoise_level', str, 'Denoise level'),
        ('scoring.structural_weight', float, 'Structural weight'),
        ('paths.storage_base', str, 'Storage base path'),
        ('api.laravel_base_url', str, 'Laravel base URL'),
        ('queue.adapter', str, 'Queue adapter'),
        ('queue.max_retries', int, 'Max retries'),
        ('database.type', str, 'Database type'),
        ('llm.model', str, 'LLM model'),
        ('llm.timeout', int, 'LLM timeout'),
    ]
    
    failed = []
    for key_path, expected_type, description in tests:
        try:
            # Navigate to the value
            parts = key_path.split('.')
            value = config
            for part in parts:
                value = getattr(value, part)
            
            # Check type
            if not isinstance(value, expected_type):
                print(f"  ✗ {key_path}: Expected {expected_type.__name__}, got {type(value).__name__}")
                failed.append(key_path)
            else:
                print(f"  ✓ {key_path}: {value} ({expected_type.__name__}) - {description}")
        except AttributeError as e:
            print(f"  ✗ {key_path}: {e}")
            failed.append(key_path)
    
    if failed:
        print(f"\n  ✗ {len(failed)} value checks failed")
        return False
    
    print(f"\n  ✓ All {len(tests)} value checks passed")
    return True


def test_variable_substitution():
    """Test that variable substitution works correctly."""
    print("\n" + "=" * 60)
    print("Test 3: Variable Substitution")
    print("=" * 60)
    
    config = reload_config()
    
    # Check that storage_base is expanded
    storage_base = config.paths.storage_base
    print(f"  storage_base: {storage_base}")
    
    if storage_base.startswith('~'):
        print(f"  ✗ storage_base not expanded (still contains ~)")
        return False
    if not os.path.isabs(storage_base):
        print(f"  ✗ storage_base not absolute path")
        return False
    print(f"  ✓ storage_base is expanded to absolute path")
    
    # Check that paths using {storage_base} are substituted
    queue_dir = config.paths.queue_directory
    print(f"  queue_directory: {queue_dir}")
    
    if '{storage_base}' in queue_dir:
        print(f"  ✗ Variable substitution failed (still contains {{storage_base}})")
        return False
    if not queue_dir.startswith(storage_base):
        print(f"  ✗ queue_directory doesn't start with storage_base")
        return False
    print(f"  ✓ queue_directory uses substituted storage_base")
    
    # Check database path
    db_path = config.database.path
    print(f"  database.path: {db_path}")
    
    if '{storage_base}' in db_path:
        print(f"  ✗ Variable substitution failed in database.path")
        return False
    if not db_path.startswith(storage_base):
        print(f"  ✗ database.path doesn't start with storage_base")
        return False
    print(f"  ✓ database.path uses substituted storage_base")
    
    print(f"\n  ✓ All variable substitutions work correctly")
    return True


def test_env_var_overrides():
    """Test that environment variable overrides work."""
    print("\n" + "=" * 60)
    print("Test 4: Environment Variable Overrides")
    print("=" * 60)
    
    # Save original env vars if they exist
    original_env = {}
    test_vars = [
        'DIGIDOC_PREPROCESSING_TARGET_DPI',
        'DIGIDOC_PREPROCESSING_DESKEW_ENABLED',
        'DIGIDOC_THRESHOLDS_AUTO_MATCH',
    ]
    
    for var in test_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
    
    try:
        # Test integer override
        os.environ['DIGIDOC_PREPROCESSING_TARGET_DPI'] = '400'
        config = reload_config()
        if config.preprocessing.target_dpi != 400:
            print(f"  ✗ Integer override failed: expected 400, got {config.preprocessing.target_dpi}")
            return False
        if not isinstance(config.preprocessing.target_dpi, int):
            print(f"  ✗ Type conversion failed: expected int, got {type(config.preprocessing.target_dpi)}")
            return False
        print(f"  ✓ Integer override: target_dpi = {config.preprocessing.target_dpi} (int)")
        
        # Test boolean override
        os.environ['DIGIDOC_PREPROCESSING_DESKEW_ENABLED'] = 'false'
        config = reload_config()
        if config.preprocessing.deskew_enabled != False:
            print(f"  ✗ Boolean override failed: expected False, got {config.preprocessing.deskew_enabled}")
            return False
        if not isinstance(config.preprocessing.deskew_enabled, bool):
            print(f"  ✗ Type conversion failed: expected bool, got {type(config.preprocessing.deskew_enabled)}")
            return False
        print(f"  ✓ Boolean override: deskew_enabled = {config.preprocessing.deskew_enabled} (bool)")
        
        # Test float override
        os.environ['DIGIDOC_THRESHOLDS_AUTO_MATCH'] = '0.90'
        config = reload_config()
        if config.thresholds.auto_match != 0.90:
            print(f"  ✗ Float override failed: expected 0.90, got {config.thresholds.auto_match}")
            return False
        if not isinstance(config.thresholds.auto_match, float):
            print(f"  ✗ Type conversion failed: expected float, got {type(config.thresholds.auto_match)}")
            return False
        print(f"  ✓ Float override: auto_match = {config.thresholds.auto_match} (float)")
        
        print(f"\n  ✓ All environment variable overrides work correctly")
        return True
        
    finally:
        # Restore original env vars
        for var in test_vars:
            if var in os.environ:
                del os.environ[var]
            if var in original_env:
                os.environ[var] = original_env[var]


def test_import_usage():
    """Test that config can be imported and used by other modules."""
    print("\n" + "=" * 60)
    print("Test 5: Import and Usage")
    print("=" * 60)
    
    try:
        # Test import
        from ocr_service.config import get_config
        print("  ✓ Can import get_config")
        
        # Test usage
        config = get_config()
        print("  ✓ Can call get_config()")
        
        # Test access
        dpi = config.preprocessing.target_dpi
        print(f"  ✓ Can access config values: preprocessing.target_dpi = {dpi}")
        
        # Test multiple accesses
        values = [
            config.thresholds.auto_match,
            config.paths.storage_base,
            config.queue.adapter,
        ]
        print(f"  ✓ Can access multiple config sections")
        
        print(f"\n  ✓ Config can be imported and used by other modules")
        return True
        
    except Exception as e:
        print(f"  ✗ Import/usage test failed: {e}")
        return False


def main():
    """Run all configuration tests."""
    print("\n" + "=" * 60)
    print("DigiDoc Configuration System Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("All Sections Exist", test_all_sections_exist),
        ("Section Values and Types", test_section_values),
        ("Variable Substitution", test_variable_substitution),
        ("Environment Variable Overrides", test_env_var_overrides),
        ("Import and Usage", test_import_usage),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ✗ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  ✓ All configuration tests passed!")
        return 0
    else:
        print(f"\n  ✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
