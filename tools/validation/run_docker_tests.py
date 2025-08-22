"""
Docker-specific test runner for Imou Life integration.
This version focuses on testing what's available without Home Assistant.
"""

import json
import sys
from pathlib import Path


def test_manifest():
    """Test manifest.json validity."""
    print("📋 Validating manifest.json...")
    try:
        manifest_path = Path("custom_components/imou_life/manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Check required fields
        required_fields = ["domain", "name", "version", "requirements"]
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field: {field}")
                return False

        print("✅ manifest.json validation passed")
        return True
    except Exception as e:
        print(f"❌ manifest.json validation failed: {e}")
        return False


def test_translations():
    """Test translation files validity."""
    print("🌐 Validating translation files...")
    translations_dir = Path("custom_components/imou_life/translations")

    if not translations_dir.exists():
        print("❌ Translations directory not found")
        return False

    valid_count = 0
    total_count = 0

    for json_file in translations_dir.glob("*.json"):
        total_count += 1
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"✅ {json_file.name} is valid JSON")
            valid_count += 1
        except Exception as e:
            print(f"❌ {json_file.name} validation failed: {e}")

    if valid_count == total_count:
        print("✅ All translation files are valid")
        return True
    else:
        print(f"⚠️  {valid_count}/{total_count} translation files are valid")
        return False


def test_file_structure():
    """Test component file structure."""
    print("📊 Running file structure analysis...")

    component_dir = Path("custom_components/imou_life")
    test_dir = Path("tests")

    # Count component files
    component_files = list(component_dir.glob("*.py"))
    test_files = list(test_dir.glob("*.py"))

    print(f"📁 Component Python files: {len(component_files)}")
    print(f"🧪 Test files: {len(test_files)}")

    print("\n📁 Component files:")
    for file in sorted(component_files):
        print(f"   - {file.name}")

    print("\n🧪 Test files:")
    for file in sorted(test_files):
        print(f"   - {file.name}")

    return True


def test_imouapi_import():
    """Test if imouapi can be imported."""
    print("🔌 Testing imouapi import...")
    try:
        import imouapi

        print("✅ imouapi module imported successfully")

        # Verify module is actually available (use it to avoid flake8 warnings)
        assert imouapi is not None

        # Test specific classes
        from imouapi.device import ImouDevice

        print("✅ ImouDevice class available")

        from imouapi.device_entity import ImouBinarySensor, ImouSensor, ImouSwitch

        print("✅ Device entity classes available")

        # Verify classes are actually available (use them to avoid flake8 warnings)
        assert ImouDevice is not None
        assert ImouBinarySensor is not None
        assert ImouSensor is not None
        assert ImouSwitch is not None

        return True
    except ImportError as e:
        print(f"❌ imouapi import failed: {e}")
        return False


def test_turbojpeg():
    """Test turbojpeg availability."""
    print("🖼️  Testing turbojpeg availability...")
    try:
        import turbojpeg

        print("✅ turbojpeg module available")

        # Verify module is actually available (use it to avoid flake8 warnings)
        assert turbojpeg is not None

        return True
    except ImportError:
        print("⚠️  turbojpeg not available (this is expected in some environments)")
        return True  # Not a failure, just a limitation


def main():
    """Main test runner."""
    print("🚀 Imou Life Integration Docker Test Runner")
    print("=" * 50)

    # Add current directory to Python path
    sys.path.insert(0, str(Path.cwd()))

    tests = [
        test_manifest,
        test_translations,
        test_file_structure,
        test_imouapi_import,
        test_turbojpeg,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
