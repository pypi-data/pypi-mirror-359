"""Basic tests for vulkan_utils package."""

import vulkan_utils
from vulkan_utils.sdk import SDKVersion, VulkanSDKManager


def test_package_version() -> None:
    """Test that package version is accessible.

    This is a basic smoke test to ensure the package imports correctly
    and the version is properly defined.
    """
    assert hasattr(vulkan_utils, "__version__")
    assert isinstance(vulkan_utils.__version__, str)
    assert len(vulkan_utils.__version__) > 0


def test_sdk_manager_initialization() -> None:
    """Test that VulkanSDKManager can be initialized.

    This tests the basic initialization of the SDK manager class.
    """
    manager = VulkanSDKManager()
    assert manager is not None
    assert hasattr(manager, "BASE_URL")
    assert hasattr(manager, "DOWNLOAD_BASE_URL")


def test_platform_detection() -> None:
    """Test platform detection functionality.

    This tests that the platform detection returns a valid platform string.
    """
    manager = VulkanSDKManager()
    platform = manager.get_current_platform()
    assert platform in ["linux", "mac", "windows"]


def test_sdk_version_model() -> None:
    """Test SDKVersion pydantic model.

    This tests the basic functionality of the SDKVersion data model.
    """
    version_info = SDKVersion(
        version="1.3.0",
        platform="linux",
        download_url="https://example.com/sdk.tar.xz",
        filename="vulkan-sdk-1.3.0.tar.xz",
    )

    assert version_info.version == "1.3.0"
    assert version_info.platform == "linux"
    assert version_info.download_url == "https://example.com/sdk.tar.xz"
    assert version_info.filename == "vulkan-sdk-1.3.0.tar.xz"
    assert version_info.sha_hash is None


def test_sdk_version_model_with_hash() -> None:
    """Test SDKVersion model with SHA hash.

    This tests the SDKVersion model when including a SHA hash.
    """
    version_info = SDKVersion(
        version="1.3.0",
        platform="linux",
        download_url="https://example.com/sdk.tar.xz",
        filename="vulkan-sdk-1.3.0.tar.xz",
        sha_hash="abc123def456",
    )

    assert version_info.sha_hash == "abc123def456"
