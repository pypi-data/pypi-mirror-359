"""Command line interface for vulkan_utils."""

import sys
from pathlib import Path
from typing import Literal

import click

from . import __version__
from .sdk import VulkanSDKManager


@click.group()
@click.version_option(version=__version__, prog_name="vulkan-utils")
def main() -> None:
    """
    Vulkan utilities CLI.

    A command-line interface for various Vulkan-related operations.
    Provides tools for downloading, installing, and managing the Vulkan SDK.
    """
    pass


@main.command()
@click.option(
    "--version", default="latest", help="SDK version to download (default: latest)"
)
@click.option(
    "--platform",
    type=click.Choice(["linux", "mac", "windows", "auto"]),
    default="auto",
    help="Target platform (default: auto-detect)",
)
@click.option(
    "--install-path",
    type=click.Path(path_type=Path),
    help="Installation directory (default: ~/VulkanSDK)",
)
@click.option(
    "--download-only", is_flag=True, help="Only download, don't extract/install"
)
def install_sdk(
    version: str,
    platform: Literal["linux", "mac", "windows", "auto"],
    install_path: Path | None,
    download_only: bool,
) -> None:
    """
    Download and install the Vulkan SDK.

    This command downloads the latest or specified version of the Vulkan SDK
    for the current platform (or a specified platform) and optionally installs it.

    Examples:

    \b
    # Download and install the latest SDK for current platform
    vulkan-utils install-sdk

    \b
    # Download specific version for Linux
    vulkan-utils install-sdk --version 1.3.224.0 --platform linux

    \b
    # Download only, don't install
    vulkan-utils install-sdk --download-only --install-path ./downloads
    """
    try:
        sdk_manager = VulkanSDKManager()

        # Determine target platform
        if platform == "auto":
            target_platform = sdk_manager.get_current_platform()
            click.echo(f"Auto-detected platform: {target_platform}")
        else:
            target_platform = platform

        # Set default install path
        if install_path is None:
            install_path = Path.home() / "VulkanSDK"

        click.echo(f"Target platform: {target_platform}")
        click.echo(f"SDK version: {version}")
        click.echo(f"Install path: {install_path}")

        if download_only:
            # Get SDK info
            sdk_info = sdk_manager.get_sdk_info(version, target_platform)

            # Download SDK
            download_path = install_path / "downloads"
            downloaded_file = sdk_manager.download_sdk(sdk_info, download_path)

            click.echo("\n✅ SDK downloaded successfully!")
            click.echo(f"Downloaded file: {downloaded_file}")

            if sdk_info.sha_hash:
                click.echo(f"Expected SHA: {sdk_info.sha_hash}")
                click.echo("You can verify the download using: shasum -a 256 <file>")
        else:
            # Download and install
            installed_path = sdk_manager.install_sdk(
                version, install_path, target_platform
            )

            click.echo("\n✅ SDK installed successfully!")
            click.echo(f"Installation path: {installed_path}")

            if target_platform == "mac":
                click.echo("\n📝 macOS Installation Notes:")
                click.echo(
                    "• If system-wide installation succeeded, the SDK should be available automatically"
                )
                click.echo(
                    "• If system-wide installation failed, you may need to set environment variables:"
                )
                click.echo(f"  export VULKAN_SDK={installed_path}")
                click.echo("  export PATH=$VULKAN_SDK/bin:$PATH")
                click.echo(
                    "  export DYLD_LIBRARY_PATH=$VULKAN_SDK/lib:$DYLD_LIBRARY_PATH"
                )
                click.echo(
                    "  export VK_LAYER_PATH=$VULKAN_SDK/share/vulkan/explicit_layer.d"
                )
                click.echo(
                    "• You can add these to your ~/.zshrc or ~/.bash_profile file"
                )
            elif target_platform == "linux":
                click.echo(
                    "\n📝 To use the SDK, you may need to set environment variables:"
                )
                click.echo(f"export VULKAN_SDK={installed_path}")
                click.echo("export PATH=$VULKAN_SDK/bin:$PATH")
                click.echo("export LD_LIBRARY_PATH=$VULKAN_SDK/lib:$LD_LIBRARY_PATH")
                click.echo(
                    "export VK_LAYER_PATH=$VULKAN_SDK/share/vulkan/explicit_layer.d"
                )
            elif target_platform == "windows":
                click.echo("\n📝 Windows installation should be complete.")
                click.echo("The SDK should be available system-wide.")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--platform",
    type=click.Choice(["linux", "mac", "windows", "auto"]),
    default="auto",
    help="Target platform (default: auto-detect)",
)
def latest_version(platform: Literal["linux", "mac", "windows", "auto"]) -> None:
    """
    Get the latest available Vulkan SDK version.

    Examples:

    \b
    # Get latest version for current platform
    vulkan-utils latest-version

    \b
    # Get latest version for specific platform
    vulkan-utils latest-version --platform linux
    """
    try:
        sdk_manager = VulkanSDKManager()

        # Determine target platform
        if platform == "auto":
            target_platform = sdk_manager.get_current_platform()
        else:
            target_platform = platform

        version = sdk_manager.get_latest_version(target_platform)

        click.echo(f"Latest Vulkan SDK version for {target_platform}: {version}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--version", default="latest", help="SDK version to get info for (default: latest)"
)
@click.option(
    "--platform",
    type=click.Choice(["linux", "mac", "windows", "auto"]),
    default="auto",
    help="Target platform (default: auto-detect)",
)
def sdk_info(
    version: str, platform: Literal["linux", "mac", "windows", "auto"]
) -> None:
    """
    Get detailed information about a Vulkan SDK version.

    Examples:

    \b
    # Get info for latest SDK
    vulkan-utils sdk-info

    \b
    # Get info for specific version
    vulkan-utils sdk-info --version 1.3.224.0 --platform linux
    """
    try:
        sdk_manager = VulkanSDKManager()

        # Determine target platform
        if platform == "auto":
            target_platform = sdk_manager.get_current_platform()
        else:
            target_platform = platform

        sdk_info = sdk_manager.get_sdk_info(version, target_platform)

        click.echo(f"SDK Version: {sdk_info.version}")
        click.echo(f"Platform: {sdk_info.platform}")
        click.echo(f"Filename: {sdk_info.filename}")
        click.echo(f"Download URL: {sdk_info.download_url}")
        if sdk_info.sha_hash:
            click.echo(f"SHA Hash: {sdk_info.sha_hash}")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
