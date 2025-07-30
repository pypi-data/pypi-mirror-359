"""Test the CLI interface."""

from click.testing import CliRunner

from vulkan_utils.cli import main


def test_cli_help() -> None:
    """Test that CLI help command works.

    This is a basic smoke test for the CLI interface.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Vulkan utilities CLI" in result.output


def test_cli_version() -> None:
    """Test that CLI version command works.

    This tests the version option of the CLI.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "vulkan-utils" in result.output


def test_install_sdk_help() -> None:
    """Test install-sdk command help.

    This tests that the install-sdk subcommand shows help correctly.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["install-sdk", "--help"])
    assert result.exit_code == 0
    assert "install-sdk" in result.output


def test_latest_version_help() -> None:
    """Test latest-version command help.

    This tests that the latest-version subcommand shows help correctly.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["latest-version", "--help"])
    assert result.exit_code == 0
    assert "latest-version" in result.output


def test_sdk_info_help() -> None:
    """Test sdk-info command help.

    This tests that the sdk-info subcommand shows help correctly.
    """
    runner = CliRunner()
    result = runner.invoke(main, ["sdk-info", "--help"])
    assert result.exit_code == 0
    assert "sdk-info" in result.output
