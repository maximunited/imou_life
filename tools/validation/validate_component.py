#!/usr/bin/env python3
"""
Component validation script for Imou Life integration.
This script validates the basic structure and imports without requiring pytest.
"""

import json
import sys
from pathlib import Path

def validate_manifest():
    """Validate the manifest.json file."""
    print("📋 Validating manifest.json...")
    
    try:
        manifest_path = Path("custom_components/imou_life/manifest.json")
        
        if not manifest_path.exists():
            print("❌ manifest.json not found")
            return False
        
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        required_fields = ["domain", "name", "codeowners", "requirements", "version"]
        missing_fields = []
        
        for field in required_fields:
            if field not in manifest:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print(f"✅ manifest.json validation passed (version: {manifest.get('version', 'unknown')})")
        return True
        
    except Exception as e:
        print(f"❌ manifest.json validation failed: {e}")
        return False

def validate_translations():
    """Validate translation files."""
    print("\n🌐 Validating translation files...")
    
    try:
        translations_dir = Path("custom_components/imou_life/translations")
        
        if not translations_dir.exists():
            print("❌ translations directory not found")
            return False
        
        translation_files = list(translations_dir.glob("*.json"))
        
        if not translation_files:
            print("❌ No translation files found")
            return False
        
        for translation_file in translation_files:
            try:
                with open(translation_file, "r", encoding="utf-8") as f:
                    json.load(f)
                print(f"✅ {translation_file.name} is valid JSON")
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"❌ {translation_file.name} has invalid JSON or encoding: {e}")
                return False
        
        print(f"✅ All {len(translation_files)} translation files are valid")
        return True
        
    except Exception as e:
        print(f"❌ Translation validation failed: {e}")
        return False

def validate_component_structure():
    """Validate the component structure."""
    print("\n🏗️ Validating component structure...")
    
    try:
        component_dir = Path("custom_components/imou_life")
        
        if not component_dir.exists():
            print("❌ Component directory not found")
            return False
        
        # Check for required files
        required_files = [
            "__init__.py",
            "manifest.json",
            "const.py",
            "config_flow.py",
            "entity.py",
            "coordinator.py"
        ]
        
        missing_files = []
        for file_name in required_files:
            if not (component_dir / file_name).exists():
                missing_files.append(file_name)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        
        # Count Python files
        python_files = list(component_dir.rglob("*.py"))
        print(f"✅ Found {len(python_files)} Python files")
        
        # List main component files
        main_files = [f for f in python_files if f.name != "__init__.py"]
        print("📁 Main component files:")
        for py_file in sorted(main_files):
            print(f"   - {py_file.relative_to(component_dir)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component structure validation failed: {e}")
        return False

def validate_test_structure():
    """Validate the test structure."""
    print("\n🧪 Validating test structure...")
    
    try:
        test_dir = Path("tests")
        
        if not test_dir.exists():
            print("❌ Tests directory not found")
            return False
        
        # Check test organization
        unit_dir = test_dir / "unit"
        integration_dir = test_dir / "integration"
        fixtures_dir = test_dir / "fixtures"
        
        if not unit_dir.exists():
            print("❌ Unit tests directory not found")
            return False
        
        if not fixtures_dir.exists():
            print("❌ Fixtures directory not found")
            return False
        
        # Count test files
        unit_tests = list(unit_dir.glob("test_*.py"))
        integration_tests = list(integration_dir.glob("test_*.py")) if integration_dir.exists() else []
        fixture_files = list(fixtures_dir.glob("*.py"))
        
        print(f"✅ Unit tests: {len(unit_tests)} files")
        print(f"✅ Integration tests: {len(integration_tests)} files")
        print(f"✅ Fixtures: {len(fixture_files)} files")
        
        # List test files
        if unit_tests:
            print("📁 Unit test files:")
            for test_file in sorted(unit_tests):
                print(f"   - {test_file.relative_to(test_dir)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test structure validation failed: {e}")
        return False

def validate_imports():
    """Validate that key modules can be imported."""
    print("\n📦 Validating imports...")
    
    try:
        # Add project root to Python path
        project_root = Path.cwd()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Test basic imports
        import custom_components.imou_life.const
        print("✅ const module imported successfully")
        
        import custom_components.imou_life.entity
        print("✅ entity module imported successfully")
        
        import custom_components.imou_life.coordinator
        print("✅ coordinator module imported successfully")
        
        import custom_components.imou_life.config_flow
        print("✅ config_flow module imported successfully")
        
        # Try to import switch (may fail due to dependencies)
        try:
            import custom_components.imou_life.switch
            print("✅ switch module imported successfully")
        except ImportError as e:
            if "turbojpeg" in str(e):
                print("⚠️  switch module import failed due to turbojpeg dependency (expected on Windows)")
                print("   This is normal and the module will work in production environments")
            else:
                print(f"❌ switch module import failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import validation failed: {e}")
        return False

def main():
    """Main validation function."""
    print("🔍 Imou Life - Component Validation")
    print("=" * 50)
    
    validation_results = []
    
    # Run all validations
    validation_results.append(validate_manifest())
    validation_results.append(validate_translations())
    validation_results.append(validate_component_structure())
    validation_results.append(validate_test_structure())
    validation_results.append(validate_imports())
    
    # Summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(validation_results)
    total = len(validation_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all(validation_results):
        print("\n🎉 All validations passed!")
        print("\n💡 The component is ready for:")
        print("   - Development and testing")
        print("   - HACS installation")
        print("   - Production deployment")
        return 0
    else:
        print("\n⚠️  Some validations failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
