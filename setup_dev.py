"""
Development setup script for Imou Life integration.
Installs pre-commit hooks and development dependencies.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dev_dependencies():
    """Install development dependencies."""
    if os.path.exists("requirements_dev.txt"):
        return run_command(
            "pip install -r requirements_dev.txt", "Installing development dependencies"
        )
    else:
        print("⚠️  requirements_dev.txt not found, skipping dependency installation")
        return True


def install_pre_commit():
    """Install pre-commit hooks."""
    return run_command("pre-commit install", "Installing pre-commit hooks")


def run_pre_commit_update():
    """Update pre-commit hooks."""
    return run_command("pre-commit autoupdate", "Updating pre-commit hooks")


def validate_setup():
    """Validate the development setup."""
    print("\n🔍 Validating setup...")

    # Check if pre-commit is installed
    try:
        subprocess.run(["pre-commit", "--version"], check=True, capture_output=True)
        print("✅ pre-commit is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pre-commit is not installed")
        return False

    # Check if .pre-commit-config.yaml exists
    if os.path.exists(".pre-commit-config.yaml"):
        print("✅ .pre-commit-config.yaml found")
    else:
        print("❌ .pre-commit-config.yaml not found")
        return False

    # Check if custom_components directory exists
    if os.path.exists("custom_components/imou_life"):
        print("✅ custom_components/imou_life directory found")
    else:
        print("❌ custom_components/imou_life directory not found")
        return False

    return True


def main():
    """Main setup function."""
    print("🚀 Setting up Imou Life development environment...\n")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install development dependencies
    if not install_dev_dependencies():
        print("❌ Failed to install development dependencies")
        sys.exit(1)

    # Install pre-commit hooks
    if not install_pre_commit():
        print("❌ Failed to install pre-commit hooks")
        sys.exit(1)

    # Update pre-commit hooks
    if not run_pre_commit_update():
        print("❌ Failed to update pre-commit hooks")
        sys.exit(1)

    # Validate setup
    if not validate_setup():
        print("❌ Setup validation failed")
        sys.exit(1)

    print("\n🎉 Development environment setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Make your changes to the code")
    print("   2. Run 'pre-commit run --all-files' to check code quality")
    print("   3. Run 'python -m pytest tests/' to run tests")
    print("   4. Commit your changes (pre-commit hooks will run automatically)")

    print("\n🔧 Available commands:")
    print("   - pre-commit run --all-files  # Run all pre-commit hooks")
    print("   - black .                     # Format code with Black")
    print("   - isort .                     # Sort imports")
    print("   - flake8 .                    # Lint code")
    print("   - pytest                      # Run tests")


if __name__ == "__main__":
    main()
