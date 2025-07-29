#!/bin/bash
set -e

echo "🚀 Publishing dreipc-python to PyPI"
echo "===================================="

# Define the path to pyproject.toml
PYPROJECT_TOML="pyproject.toml"

# Function to update the version in pyproject.toml
update_version() {
    local part_to_increment=$1 # "major", "minor", "patch"

    # Read the current version
    current_version=$(grep '^version =' "$PYPROJECT_TOML" | sed -E 's/version = "(.*)"/\1/')
    echo "Current version: $current_version"

    # Split the version into components
    IFS='.' read -r major minor patch <<< "$current_version"

    case "$part_to_increment" in
        major|breaking)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Invalid version increment part: $part_to_increment. Using 'patch' as default."
            patch=$((patch + 1))
            ;;
    esac

    new_version="$major.$minor.$patch"
    echo "New version: $new_version"

    # Update the pyproject.toml file
    # Using sed to replace the version line
    sed -i '' -E "s/^(version = \").*(\")/\1$new_version\2/" "$PYPROJECT_TOML"
    echo "Updated $PYPROJECT_TOML to version $new_version"
}

# Parse command line arguments for version increment
VERSION_INCREMENT="patch" # Default increment
if [ "$#" -gt 0 ]; then
    case "$1" in
        major|breaking)
            VERSION_INCREMENT="major"
            ;;
        minor)
            VERSION_INCREMENT="minor"
            ;;
        patch)
            VERSION_INCREMENT="patch"
            ;;
        *)
            echo "Usage: $0 [major|minor|patch]"
            echo "Defaulting to 'patch' increment."
            ;;
    esac
fi

# Increment the version
update_version "$VERSION_INCREMENT"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/

# Build package
echo "📦 Building package..."
python -m build

# Check package
echo "🔍 Checking package..."
python -m twine check dist/*

# Upload to TestPyPI first
echo "🧪 Uploading to TestPyPI..."
python -m twine upload --repository testpypi dist/* --verbose

echo "✅ Published to TestPyPI!"
echo "Test with: pip install --index-url https://test.pypi.org/simple/ dreipc-python"
echo ""
echo "If everything works, publish to PyPI with:"
echo "python -m twine upload dist/*"