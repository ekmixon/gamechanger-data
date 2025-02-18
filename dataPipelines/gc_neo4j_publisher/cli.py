import click
from .utils import Neo4jJobManager
from .utils import only_write_infobox


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    ctx.obj = Neo4jJobManager()


pass_njm = click.make_pass_decorator(Neo4jJobManager)


@cli.command()
@click.option(
    '--csv-file-path',
    help='The file path of the csv with list of entities to scrape info for',
    type=click.Path(resolve_path=True, exists=True, dir_okay=False, file_okay=True),
    required=True
)
@click.option(
    '--infobox-dir',
    help='Directory path of where to write the infobox.json files',
    type=click.Path(resolve_path=True, dir_okay=True, file_okay=False),
    required=True
)
def scrape(csv_file_path: str, infobox_dir: str) -> None:
    only_write_infobox(csv_file_path, infobox_dir)


@cli.command()
@click.option(
    '-s',
    '--source',
    help='A source directory to be processed.',
    type=click.Path(resolve_path=True, exists=True, dir_okay=True, file_okay=False),
    required=True,
)
@click.option(
    '--clear',
    help='Clears out all data from the neo4j database before populating it',
    is_flag=True
)
@click.option(
    '--max-threads',
    help='Max threads to run on',
    type=int,
    default=-1
)
@click.option(
    '--without-web-scraping',
    help='Designates if this is being run in an environment without internet. Instead of scraping from wiki, it will '
         'get info from jsons in the common/data/infobox folder',
    is_flag=True
)
@click.option(
    '--infobox-dir',
    help='Directory path of where to write the infobox.json files',
    type=click.Path(resolve_path=True, exists=True, dir_okay=True, file_okay=False),
    required=False
)
@pass_njm
def run(njm: Neo4jJobManager, source: str, clear: bool, max_threads: int, without_web_scraping: bool, infobox_dir: str) -> None:
    njm.run_update(
        source=source,
        clear=clear,
        max_threads=max_threads,
        without_web_scraping=without_web_scraping,
        scrape_wiki=(without_web_scraping == False),
        infobox_dir=infobox_dir
    )
