import click

from scripts import categorize, encrypt, graph, import_activity


@click.group()
def cli() -> None:
    """
    Run financial analysis on finance.ods within the git directoy.
    For results to be seen, file must be closed before running any scripts.
    """
    pass


cli.add_command(encrypt.encrypt)
cli.add_command(encrypt.decrypt)
cli.add_command(import_activity.import_activity)
cli.add_command(categorize.categorize)
cli.add_command(graph.graph)

if __name__ == "__main__":
    cli()
