from time import sleep

import click
from rich.console import Console


@click.command()
def main():
    """A simple script with click and rich"""
    console = Console(stderr=True)
    with console.status("Boiling water..."):
        sleep(1)
    with console.status("Preparing ☕️..."):
        sleep(1)
    console.print("😄")
