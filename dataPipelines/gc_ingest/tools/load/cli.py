import click
from .utils import LoadManager
import typing as t
from dataPipelines.gc_ingest.config import Config
from dataPipelines.gc_ingest.common_cli_options import pass_bucket_name_option
import datetime as dt
import functools


def pass_core_load_cli_options(f):
    @click.option(
        '--load-archive-base-prefix',
        type=str,
        help="S3 base prefix for storing loaded files",
        required=True
    )
    @functools.wraps(f)
    def wf(*args, **kwargs):
        return f(*args, **kwargs)
    return wf


@click.group(name="load")
@pass_core_load_cli_options
@pass_bucket_name_option
@click.pass_context
def load_cli(ctx: click.Context, load_archive_base_prefix: str, bucket_name: str):
    """Ingest Docs & Register them in the DB"""
    ctx.obj = LoadManager(
        load_archive_base_prefix=load_archive_base_prefix,
        bucket_name=bucket_name
    )


pass_lm = click.make_pass_decorator(LoadManager)



@load_cli.command()
@click.option(
    '--raw-doc-dir',
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True
    ),
    help="Path to local directory with raw docs",
    required=True
)
@click.option(
    '--metadata-doc-dir',
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True
    ),
    help="Path to directory with metadata files corresponding to raw docs"
)
@click.option(
    '--parsed-doc-dir',
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True
    ),
    help="Path to directory with parsed files corresponding to raw docs"
)
@click.option(
    '--timestamp',
    type=click.DateTime(),
    help="Timestamp that will be used to mark this load batch and relevant s3 paths",
    default=Config.default_batch_timestamp_str
)
@click.option(
    '--skip-s3-upload',
    type=bool,
    default=False,
    show_default=True,
    help="Don't upload any files to s3"
)
@click.option(
    '--skip-db-update',
    type=bool,
    default=False,
    show_default=True,
    help="Don't make any DB updates"
)
@pass_lm
def local(lm: LoadManager,
          raw_doc_dir: str,
          metadata_doc_dir: t.Optional[str],
          parsed_doc_dir: t.Optional[str],
          timestamp: dt.datetime,
          skip_s3_upload: bool,
          skip_db_update: bool) -> None:
    """Ingest from a local directory"""

    lm.load(
        raw_dir=raw_doc_dir,
        parsed_dir=parsed_doc_dir,
        metadata_dir=metadata_doc_dir,
        ingest_ts=timestamp,
        update_s3=not skip_s3_upload,
        update_db=not skip_db_update
    )
