import click

from sciop_scraping.cli.api import sciop_api
from sciop_scraping.cli.state import state_cli
from sciop_scraping.quests.chronicling.cli import chronicling_america


@click.group("sciop-scrape")
def cli() -> None:
    """Distributed scraping with sciop :)"""
    pass


# global groups
cli.add_command(state_cli)
cli.add_command(sciop_api)

# quest groups
cli.add_command(chronicling_america)
