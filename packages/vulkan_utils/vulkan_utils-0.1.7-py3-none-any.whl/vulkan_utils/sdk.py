"""Vulkan SDK download and installation utilities."""

import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

import requests
from pydantic import BaseModel, Field


class SDKVersion(BaseModel):
    """Vulkan SDK version information."""

    version: str = Field(description="SDK version string")
    platform: str = Field(description="Target platform")
    download_url: str = Field(description="Download URL for the SDK")
    filename: str = Field(description="Local filename for the downloaded SDK")
    sha_hash: str | None = Field(default=None, description="SHA hash of the SDK file")


class VulkanSDKManager:
    """Manages Vulkan SDK downloads and installations."""

    BASE_URL = "https://vulkan.lunarg.com/sdk"
    DOWNLOAD_BASE_URL = "https://sdk.lunarg.com/sdk/download"

    PLATFORM_MAP = {"Linux": "linux", "Darwin": "mac", "Windows": "windows"}

    FILE_EXTENSIONS = {"linux": "tar.xz", "mac": "zip", "windows": "exe"}

    def __init__(self) -> None:
        """Initialize the SDK manager."""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "vulkan-utils-cli/1.0"})

    def get_current_platform(self) -> str:
        """
        Get the current platform identifier for Vulkan SDK.

        Returns
        -------
        str
            Platform identifier ('linux', 'mac', or 'windows')

        Raises
        ------
        ValueError
            If the platform is not supported
        """
        system = platform.system()
        if system not in self.PLATFORM_MAP:
            raise ValueError(f"Unsupported platform: {system}")
        return self.PLATFORM_MAP[system]

    def get_latest_version(self, target_platform: str | None = None) -> str:
        """
        Get the latest SDK version for a platform.

        Parameters
        ----------
        target_platform : str, optional
            Target platform ('linux', 'mac', 'windows').
            If None, uses current platform.

        Returns
        -------
        str
            Latest SDK version string

        Raises
        ------
        requests.RequestException
            If the request fails
        ValueError
            If the platform is invalid
        """
        if target_platform is None:
            target_platform = self.get_current_platform()

        url = f"{self.BASE_URL}/latest/{target_platform}.txt"
        response = self.session.get(url)
        response.raise_for_status()
        return response.text.strip()

    def get_sdk_info(
        self, version: str = "latest", target_platform: str | None = None
    ) -> SDKVersion:
        """
        Get SDK information for download.

        Parameters
        ----------
        version : str, default="latest"
            SDK version to get info for
        target_platform : str, optional
            Target platform. If None, uses current platform.

        Returns
        -------
        SDKVersion
            SDK version information including download details
        """
        if target_platform is None:
            target_platform = self.get_current_platform()

        if version == "latest":
            actual_version = self.get_latest_version(target_platform)
        else:
            actual_version = version

        file_ext = self.FILE_EXTENSIONS[target_platform]
        filename = f"vulkan_sdk.{file_ext}"
        download_url = f"{self.DOWNLOAD_BASE_URL}/{version}/{target_platform}/{filename}?Human=true"

        # Get SHA hash
        sha_url = f"{self.DOWNLOAD_BASE_URL.replace('/download', '')}/sha/{version}/{target_platform}/{filename}.txt"
        try:
            sha_response = self.session.get(sha_url)
            sha_response.raise_for_status()
            sha_hash = sha_response.text.strip().split()[0]  # First part is the hash
        except requests.RequestException:
            sha_hash = None

        return SDKVersion(
            version=actual_version,
            platform=target_platform,
            download_url=download_url,
            filename=filename,
            sha_hash=sha_hash,
        )

    def download_sdk(self, sdk_info: SDKVersion, download_path: Path) -> Path:
        """
        Download the SDK to the specified path.

        Parameters
        ----------
        sdk_info : SDKVersion
            SDK information including download URL
        download_path : Path
            Directory to download the SDK to

        Returns
        -------
        Path
            Path to the downloaded file

        Raises
        ------
        requests.RequestException
            If the download fails
        """
        download_path.mkdir(parents=True, exist_ok=True)
        file_path = download_path / sdk_info.filename

        print(f"Downloading Vulkan SDK {sdk_info.version} for {sdk_info.platform}...")
        print(f"URL: {sdk_info.download_url}")

        response = self.session.get(sdk_info.download_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end="", flush=True)

        print("\nDownload completed!")
        return file_path

    def extract_sdk(self, file_path: Path, extract_to: Path) -> Path:
        """
        Extract the downloaded SDK.

        Parameters
        ----------
        file_path : Path
            Path to the downloaded SDK file
        extract_to : Path
            Directory to extract the SDK to

        Returns
        -------
        Path
            Path to the extracted SDK directory

        Raises
        ------
        ValueError
            If the file format is not supported
        """
        extract_to.mkdir(parents=True, exist_ok=True)

        print(f"Extracting SDK to {extract_to}...")

        if file_path.suffix == ".zip":
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
        elif file_path.name.endswith(".tar.xz"):
            with tarfile.open(file_path, "r:xz") as tar_ref:
                tar_ref.extractall(extract_to)
        elif file_path.suffix == ".exe":
            # Windows installer - return the installer path for later execution
            print("Windows installer ready for installation.")
            return file_path
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

        # For macOS, fix permissions on extracted .app bundle
        current_platform = self.get_current_platform()
        if current_platform == "mac":
            self._fix_mac_app_permissions(extract_to)

        print("Extraction completed!")
        return extract_to

    def _fix_mac_app_permissions(self, extract_path: Path) -> None:
        """
        Fix permissions on macOS .app bundles after extraction.

        Parameters
        ----------
        extract_path : Path
            Directory containing extracted files
        """
        print("Fixing permissions on macOS app bundle...")
        try:
            # Find all .app directories
            for app_path in extract_path.rglob("*.app"):
                if "vulkansdk" in app_path.name.lower():
                    # Make the entire app bundle executable
                    subprocess.run(
                        ["chmod", "-R", "+x", str(app_path)],
                        check=True,
                        capture_output=True,
                    )
                    print(f"Fixed permissions for {app_path}")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not fix app permissions: {e}")
            print("You may need to run the installer with different permissions")

    def install_sdk(
        self,
        version: str = "latest",
        install_path: Path | None = None,
        target_platform: str | None = None,
    ) -> Path:
        """
        Download and install the Vulkan SDK.

        This method performs the complete installation process:
        1. Downloads the SDK for the specified platform and version
        2. Extracts the SDK to the specified directory
        3. Runs platform-specific installation:
           - macOS: Uses the installer executable with proper flags, then runs
             install_vulkan.py for system-wide installation
           - Linux: Copies extracted files to installation directory
           - Windows: Runs the installer executable in silent mode

        Parameters
        ----------
        version : str, default="latest"
            SDK version to install
        install_path : Path, optional
            Installation directory. If None, uses a default location.
        target_platform : str, optional
            Target platform. If None, uses current platform.

        Returns
        -------
        Path
            Path to the installed SDK
        """
        if target_platform is None:
            target_platform = self.get_current_platform()

        if install_path is None:
            install_path = Path.home() / "VulkanSDK"

        # Get SDK info
        sdk_info = self.get_sdk_info(version, target_platform)

        # Check for existing installation
        if self._is_existing_installation(install_path):
            self._handle_existing_installation(install_path)

        # Create temporary download directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Download SDK
            downloaded_file = self.download_sdk(sdk_info, temp_path)

            # For macOS, extract to temp directory and run installer
            # For other platforms, extract directly to install path
            if target_platform == "mac":
                extracted_path = self.extract_sdk(
                    downloaded_file, temp_path / "extracted"
                )
            else:
                extracted_path = self.extract_sdk(downloaded_file, install_path)

            # Install SDK
            if target_platform == "mac":
                return self._install_mac_sdk(extracted_path, install_path)
            elif target_platform == "linux":
                return self._install_linux_sdk(extracted_path, install_path)
            elif target_platform == "windows":
                return self._install_windows_sdk(downloaded_file, install_path)
            else:
                raise ValueError(f"Unsupported target platform: {target_platform}")

    def _find_installer_app(self, extract_path: Path) -> Path | None:
        """
        Find the macOS installer app in the extracted directory.

        Parameters
        ----------
        extract_path : Path
            Directory where SDK was extracted

        Returns
        -------
        Path | None
            Path to the installer app, or None if not found
        """
        for item in extract_path.rglob("*.app"):
            if "vulkansdk" in item.name.lower():
                return item
        return None

    def _install_mac_sdk(self, extract_path: Path, install_path: Path) -> Path:
        """
        Install Vulkan SDK on macOS.

        Parameters
        ----------
        extract_path : Path
            Directory containing extracted SDK
        install_path : Path
            Target installation directory

        Returns
        -------
        Path
            Path to the installed SDK

        Raises
        ------
        RuntimeError
            If installation fails
        """
        print("Installing Vulkan SDK on macOS...")

        # Find the installer app
        installer_app = self._find_installer_app(extract_path)
        if not installer_app:
            raise RuntimeError("Could not find macOS installer app in extracted files")

        # Find the actual installer executable
        installer_executable = installer_app / "Contents" / "MacOS"
        executable_files = list(installer_executable.glob("*"))
        if not executable_files:
            raise RuntimeError(
                f"Could not find installer executable in {installer_executable}"
            )

        installer_exe = executable_files[0]

        print(f"Found installer: {installer_exe}")

        # Step 1: Run the installer with proper flags
        cmd = [
            str(installer_exe),
            "--al",  # Accept license
            "--am",  # Accept EULA
            "-c",  # Command line mode
            "-t",
            str(install_path),  # Target directory
            "install",
        ]

        print(f"Running installer command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Check if the process completed successfully
        if result.returncode == 0:
            print("Installer process completed successfully!")
            if result.stdout:
                print(f"stdout: {result.stdout}")
        else:
            print(f"Installer process failed with return code {result.returncode}")
            if result.stderr:
                print(f"stderr: {result.stderr}")
            if result.stdout:
                print(f"stdout: {result.stdout}")
            raise RuntimeError(
                f"Installer failed with return code {result.returncode}: {result.stderr}"
            )

        print("SDK extraction completed successfully!")

        # Step 2: Add source of setup-env.sh to the shell profile if not already present
        setup_env_script = install_path / "setup-env.sh"
        if setup_env_script.exists():
            print(f"Adding {setup_env_script} to shell profile...")
            if os.getenv("SHELL") == "/bin/bash":
                shell_profile = Path.home() / ".bash_profile"
                if not shell_profile.exists():
                    shell_profile = Path.home() / ".bashrc"
            elif os.getenv("SHELL") == "/bin/zsh":
                shell_profile = Path.home() / ".zshrc"
            else:
                raise RuntimeError(
                    "Unsupported shell. Please add the source command manually."
                )

            if str(setup_env_script) not in shell_profile.read_text():
                with open(shell_profile, "a") as profile_file:
                    profile_file.write(
                        f"\n# Source Vulkan SDK environment\nsource {setup_env_script}\n"
                    )
                print(f"Added source command to {shell_profile}")

        return install_path

    def _install_linux_sdk(self, extract_path: Path, install_path: Path) -> Path:
        """
        Install Vulkan SDK on Linux.

        Parameters
        ----------
        extract_path : Path
            Directory containing extracted SDK
        install_path : Path
            Target installation directory

        Returns
        -------
        Path
            Path to the installed SDK
        """
        print("Installing Vulkan SDK on Linux...")

        # Linux SDK is typically just extracted files that need to be moved
        # Look for the version directory
        version_dirs = [d for d in extract_path.iterdir() if d.is_dir()]

        if len(version_dirs) == 1:
            source_dir = version_dirs[0]
        else:
            # Multiple directories, look for one with version number
            source_dir = None
            for d in version_dirs:
                if any(char.isdigit() for char in d.name):
                    source_dir = d
                    break

            if source_dir is None:
                source_dir = extract_path

        print(f"Copying SDK from {source_dir} to {install_path}")

        # Copy the SDK to the install path
        if source_dir != extract_path:
            shutil.copytree(source_dir, install_path, dirs_exist_ok=True) # type: ignore[arg-type]
        else:
            # Copy all contents
            install_path.mkdir(parents=True, exist_ok=True)
            for item in source_dir.iterdir():
                dest = install_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        print("Linux SDK installation completed!")
        return install_path

    def _install_windows_sdk(self, installer_path: Path, install_path: Path) -> Path:
        """
        Install Vulkan SDK on Windows.

        Parameters
        ----------
        installer_path : Path
            Path to the Windows installer executable
        install_path : Path
            Target installation directory

        Returns
        -------
        Path
            Path to the installed SDK

        Raises
        ------
        RuntimeError
            If installation fails
        """
        print("Installing Vulkan SDK on Windows...")

        # Run the Windows installer in silent mode
        cmd = [
            str(installer_path),
            "/S",  # Silent install
            f"/D={install_path}",  # Installation directory
        ]

        print(f"Running installer: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Windows SDK installation completed!")
            return install_path

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Windows installer failed: {e.stderr}") from e

    def _is_existing_installation(self, install_path: Path) -> bool:
        """
        Check if the version path contains an existing Vulkan SDK installation.

        Parameters
        ----------
        version_path : Path
            Path to check for existing installation

        Returns
        -------
        bool
            True if an existing installation is detected, False otherwise
        """
        if not install_path.exists():
            return False

        # Check for common SDK directory structure
        sdk_indicators = [
            "bin",
            "lib",
            "include/vulkan",
            "share/vulkan",
            "install_vulkan.py",
            "uninstall.sh",
            "setup-env.sh",
        ]

        # If at least 2 indicators are present, consider it an installation
        found_indicators = sum(
            1 for indicator in sdk_indicators if (install_path / indicator).exists()
        )

        return found_indicators >= 2

    def _get_user_confirmation(self, message: str) -> bool:
        """
        Get user confirmation for an action.

        Parameters
        ----------
        message : str
            Message to display to the user

        Returns
        -------
        bool
            True if user confirms, False otherwise
        """
        while True:
            response = input(f"{message} (y/N): ").lower().strip()
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no", ""):
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")

    def _run_uninstall_script(self, version_path: Path) -> bool:
        """
        Run the uninstall.sh script if it exists in the version path.

        Parameters
        ----------
        version_path : Path
            Path containing the SDK installation

        Returns
        -------
        bool
            True if uninstall was successful or no script found, False if failed
        """
        uninstall_script = version_path / "uninstall.sh"

        if not uninstall_script.exists():
            print(f"No uninstall.sh script found at {uninstall_script}")
            return True  # Consider successful if no script exists

        print(f"Running uninstall script: {uninstall_script}")

        try:
            # Make script executable
            subprocess.run(
                ["chmod", "+x", str(uninstall_script)], check=True, capture_output=True
            )

            # Run the uninstall script
            result = subprocess.run(
                ["sudo", str(uninstall_script)],
                cwd=str(version_path),
                check=True,
                capture_output=True,
                text=True,
            )

            print("Uninstall script completed successfully!")
            print(f"Output: {result.stdout}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Uninstall script failed with return code {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error running uninstall script: {e}")
            return False

    def _remove_installation_directory(self, install_path: Path) -> bool:
        """
        Remove the installation directory and its contents.

        Parameters
        ----------
        version_path : Path
            Path to the installation directory to remove

        Returns
        -------
        bool
            True if removal was successful, False otherwise
        """
        try:
            if install_path.exists():
                print(f"Removing installation directory: {install_path}")
                shutil.rmtree(install_path)
                print("Installation directory removed successfully!")
            return True
        except Exception as e:
            print(f"Error removing installation directory: {e}")
            return False

    def _handle_existing_installation(self, install_path: Path) -> bool:
        """
        Handle existing installation by prompting user and running uninstall if confirmed.

        Parameters
        ----------
        version_path : Path
            Path to the existing installation

        Returns
        -------
        bool
            True if existing installation was handled successfully, False otherwise
        """
        print(f"Existing Vulkan SDK installation detected at: {install_path}")

        # Ask user for confirmation
        confirm_message = (
            "An existing installation was found. Do you want to uninstall it "
            "and proceed with the new installation?"
        )

        if not self._get_user_confirmation(confirm_message):
            print("Installation cancelled by user.")
            return False

        # Remove the installation directory
        return self._remove_installation_directory(install_path)
