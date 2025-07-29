# Vulkan Utils

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.6-orange.svg)](https://github.com/msemelman/vulkan_utils)

A simple yet powerful command-line utility for managing Vulkan SDK operations. This tool simplifies downloading, installing, and managing Vulkan SDK versions across different platforms.

## 🚀 Features

- **Cross-platform support**: Works on Linux, macOS, and Windows
- **Automatic platform detection**: Intelligently detects your current platform
- **Version management**: Download specific versions or always get the latest
- **Download-only mode**: Download SDKs without installation for offline use
- **SHA verification**: Built-in integrity checking for downloaded files
- **Progress tracking**: Real-time download progress indicators
- **Smart installation**: Platform-specific installation with helpful setup instructions
- **Installation management**: Detects existing installations and provides upgrade options

## 📦 Installation

### Using uvx (One-time execution)

Run vulkan_utils directly without installing it globally:

```bash
# Run commands directly with uvx
uvx vulkan_utils install-sdk
uvx vulkan_utils latest-version
uvx vulkan_utils sdk-info
```

### Using uv (Project installation)

```bash
uv add vulkan_utils
```

### Using pip

```bash
pip install vulkan_utils
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/msemelman/vulkan_utils.git
cd vulkan_utils

# Install in development mode
uv sync
```

## 🛠️ Usage

After installation, the `vulkan-utils` command will be available in your terminal. Alternatively, you can run commands directly with `uvx vulkan_utils` without installing.

### Basic Commands

```bash
# Show help
vulkan-utils --help
# or with uvx
uvx vulkan_utils --help

# Show version
vulkan-utils --version
# or with uvx
uvx vulkan_utils --version
```

### Installing Vulkan SDK

#### Quick Start (Recommended)

```bash
# Download and install the latest Vulkan SDK for your platform
vulkan-utils install-sdk

# or run directly with uvx (no installation required)
uvx vulkan_utils install-sdk
```

#### Advanced Usage

```bash
# Install a specific version
vulkan-utils install-sdk --version 1.3.224.0
# or with uvx
uvx vulkan_utils install-sdk --version 1.3.224.0

# Install for a specific platform
vulkan-utils install-sdk --platform linux

# Install to a custom directory
vulkan-utils install-sdk --install-path /opt/VulkanSDK

# Download only (don't install)
vulkan-utils install-sdk --download-only --install-path ./downloads
```

### Getting Version Information

```bash
# Get the latest available version for your platform
vulkan-utils latest-version
# or with uvx
uvx vulkan_utils latest-version

# Get latest version for a specific platform
vulkan-utils latest-version --platform windows

# Get detailed SDK information
vulkan-utils sdk-info
# or with uvx
uvx vulkan_utils sdk-info

# Get info for a specific version
vulkan-utils sdk-info --version 1.3.224.0 --platform mac
```

## 🔧 Command Reference

### `install-sdk`

Downloads and installs the Vulkan SDK.

**Options:**
- `--version`: SDK version to download (default: "latest")
- `--platform`: Target platform - `linux`, `mac`, `windows`, or `auto` (default: "auto")
- `--install-path`: Installation directory (default: `~/VulkanSDK`)
- `--download-only`: Only download, don't extract/install

**Examples:**
```bash
# Basic installation
vulkan-utils install-sdk
# or with uvx
uvx vulkan_utils install-sdk

# Specific version for Linux
vulkan-utils install-sdk --version 1.3.224.0 --platform linux
# or with uvx
uvx vulkan_utils install-sdk --version 1.3.224.0 --platform linux

# Download to custom location without installing
vulkan-utils install-sdk --download-only --install-path ./my-downloads
```

### `latest-version`

Get the latest available Vulkan SDK version.

**Options:**
- `--platform`: Target platform (default: auto-detect)

**Examples:**
```bash
vulkan-utils latest-version
# or with uvx
uvx vulkan_utils latest-version

vulkan-utils latest-version --platform windows
```

### `sdk-info`

Get detailed information about a Vulkan SDK version.

**Options:**
- `--version`: SDK version (default: "latest")
- `--platform`: Target platform (default: auto-detect)

**Examples:**
```bash
vulkan-utils sdk-info
# or with uvx
uvx vulkan_utils sdk-info

vulkan-utils sdk-info --version 1.3.224.0
```

## 🖥️ Platform-Specific Notes

### macOS

After installation, you may need to set environment variables if system-wide installation fails:

```bash
export VULKAN_SDK=~/VulkanSDK
export PATH=$VULKAN_SDK/bin:$PATH
export DYLD_LIBRARY_PATH=$VULKAN_SDK/lib:$DYLD_LIBRARY_PATH
export VK_LAYER_PATH=$VULKAN_SDK/share/vulkan/explicit_layer.d
```

Add these to your `~/.zshrc` or `~/.bash_profile` for persistence.

### Linux

Set the following environment variables:

```bash
export VULKAN_SDK=~/VulkanSDK
export PATH=$VULKAN_SDK/bin:$PATH
export LD_LIBRARY_PATH=$VULKAN_SDK/lib:$LD_LIBRARY_PATH
export VK_LAYER_PATH=$VULKAN_SDK/share/vulkan/explicit_layer.d
```

### Windows

Windows installations should work system-wide automatically. No additional configuration typically required.

## 🔍 Examples

### Complete Workflow Example

```bash
# Check latest available version
vulkan-utils latest-version
# or with uvx
uvx vulkan_utils latest-version
# Output: Latest Vulkan SDK version for mac: 1.3.250.1

# Get detailed information about the latest SDK
vulkan-utils sdk-info
# or with uvx
uvx vulkan_utils sdk-info
# Output: 
# SDK Version: 1.3.250.1
# Platform: mac
# Filename: vulkan_sdk.zip
# Download URL: https://sdk.lunarg.com/sdk/download/latest/mac/vulkan_sdk.zip?Human=true
# SHA Hash: abc123...

# Download and install
vulkan-utils install-sdk
# or with uvx
uvx vulkan_utils install-sdk
# Downloads, extracts, and installs with progress indicators and platform-specific instructions
```

### Download for Offline Installation

```bash
# Download multiple versions for different platforms
vulkan-utils install-sdk --version 1.3.250.1 --platform linux --download-only --install-path ./offline-sdks
vulkan-utils install-sdk --version 1.3.250.1 --platform windows --download-only --install-path ./offline-sdks
vulkan-utils install-sdk --version 1.3.250.1 --platform mac --download-only --install-path ./offline-sdks

# or with uvx (useful for CI/CD or one-time usage)
uvx vulkan_utils install-sdk --version 1.3.250.1 --platform linux --download-only --install-path ./offline-sdks
uvx vulkan_utils install-sdk --version 1.3.250.1 --platform windows --download-only --install-path ./offline-sdks
uvx vulkan_utils install-sdk --version 1.3.250.1 --platform mac --download-only --install-path ./offline-sdks
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/msemelman/vulkan_utils.git
cd vulkan_utils

# Install dependencies with uv
uv sync

# Run in development mode
uv run vulkan-utils --help
```

### Running Tests

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest
```

### Code Style

This project follows Python best practices:
- **Type hints**: Full type annotations using modern Python syntax
- **Documentation**: NumPy-style docstrings for all public functions
- **Data validation**: Pydantic models for robust data structures
- **Testing**: pytest framework with fixtures for reusable test data
- **Dependency management**: Uses `uv` for fast, reliable dependency resolution

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

1. Follow the existing code style and conventions
2. Add type hints to all function parameters and return values
3. Write comprehensive docstrings using NumPy format
4. Use Pydantic models for data structures
5. Write tests for new functionality using pytest
6. Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/msemelman/vulkan_utils/issues) page
2. Create a new issue with detailed information about your problem
3. Include your platform, Python version, and error messages

## 🔗 Related Projects

- [Vulkan SDK](https://vulkan.lunarg.com/) - Official Vulkan SDK
- [Vulkan Documentation](https://vulkan.org/) - Official Vulkan documentation
- [Vulkan Tutorial](https://vulkan-tutorial.com/) - Comprehensive Vulkan learning resource

---

**Note**: This tool is not affiliated with the Khronos Group or LunarG. It's a community tool designed to simplify Vulkan SDK management.
