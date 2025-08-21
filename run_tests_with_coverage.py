"""
Test runner script with coverage for Imou Life integration.
This script runs tests and generates coverage reports.
"""

import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ["pytest", "pytest_cov", "coverage"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements_test.txt")
        return False

    print("✅ All required packages are installed")
    return True


def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    print("\n🧪 Running tests with coverage...")

    # Run pytest with coverage
    coverage_command = [
        "python",
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--cov=custom_components/imou_life",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml",
        "--cov-fail-under=70",  # Fail if coverage is below 70%
    ]

    try:
        subprocess.run(coverage_command, check=True)
        print("✅ Tests completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def generate_coverage_report():
    """Generate a detailed coverage report."""
    print("\n📊 Generating coverage report...")

    try:
        # Generate HTML report
        subprocess.run(["coverage", "html"], check=True)
        print("✅ HTML coverage report generated in htmlcov/")

        # Generate XML report for Coveralls
        subprocess.run(["coverage", "xml"], check=True)
        print("✅ XML coverage report generated as coverage.xml")

        # Show terminal report
        subprocess.run(["coverage", "report"], check=True)

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Coverage report generation failed: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Imou Life Integration Test Runner with Coverage")
    print("=" * 55)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Run tests with coverage
    if not run_tests_with_coverage():
        print("❌ Test execution failed")
        sys.exit(1)

    # Generate coverage reports
    if not generate_coverage_report():
        print("❌ Coverage report generation failed")
        sys.exit(1)

    print("\n🎉 All tasks completed successfully!")
    print("\n📋 Coverage reports available:")
    print("   - HTML: htmlcov/index.html")
    print("   - XML: coverage.xml (for Coveralls)")
    print("   - Terminal: See above for summary")

    print("\n🔧 Next steps:")
    print("   1. Open htmlcov/index.html in your browser for detailed coverage")
    print("   2. Push to GitHub to see coverage on Coveralls")
    print("   3. Aim for at least 70% code coverage")


if __name__ == "__main__":
    main()
