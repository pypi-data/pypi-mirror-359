"""Command line interface for vulkan_utils."""

import click
from importlib.metadata import version
from _version import __version__



@click.group()
@click.version_option(version=__version__, prog_name="vulkan-utils")
def main() -> None:
    """
    Vulkan utilities CLI.
    
    A simple command-line interface for various Vulkan-related operations.
    Currently provides basic greeting functionality as a demonstration.
    """
    pass



if __name__ == "__main__":
    main()
