import json
from pathlib import Path
import typing as t
import datetime as dt
import sys

from dataPipelines.gc_crawler.data_model import Document
from dataPipelines.gc_ingest.config import Config
from dataPipelines.gc_db_utils.orch.models import VersionedDoc, Publication
from common.utils.s3 import S3Utils
from common.utils.parsers import parse_timestamp
from pydantic import BaseModel
from enum import Enum


class ArchiveType(Enum):
    RAW = 'raw'
    PARSED = 'parsed'
    METADATA = 'metadata'
    THUMBNAIL = 'thumbnails'


class GenericIngestableDoc(BaseModel):
    local_path: Path
    s3_path: t.Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        extra = 'forbid'


class IngestableRawDoc(GenericIngestableDoc):
    pass


class IngestableMetadataDoc(GenericIngestableDoc):
    metadata: Document


class IngestableThumbnailDoc(GenericIngestableDoc):
    pass


class IngestableParsedDoc(GenericIngestableDoc):
    pass


class IngestableDocGroup(BaseModel):
    raw_idoc: IngestableRawDoc
    parsed_idoc: t.Optional[IngestableParsedDoc] = None
    metadata_idoc: t.Optional[IngestableMetadataDoc] = None
    thumbnail_idoc: t.Optional[IngestableThumbnailDoc] = None


class LoadManager:
    SUPPORTED_RAW_DOC_EXTENSIONS = frozenset({'.pdf', '.html'})
    METADATA_DOC_EXTENSION = '.metadata'
    PARSED_DOC_EXTENSION = '.json'
    THUMBNAIL_EXTENSION = '.png'

    def __init__(self,
                 load_archive_base_prefix: str,
                 bucket_name: str = Config.s3_bucket,
                 **ignored_kwargs):
        """Document load manager
        :param load_archive_base_prefix: base prefix for doc ingest archive
        :param bucket_name: s3 bucket name
        """
        self.s3u = S3Utils(ch=Config.connection_helper, bucket=bucket_name)
        self.load_archive_base_prefix = self.s3u.format_as_prefix(load_archive_base_prefix)
        Config.connection_helper.init_dbs()

    def get_archive_prefix(self, archive_type: t.Union[ArchiveType, str]) -> str:
        """Get prefix for given archive type"""
        archive_type = ArchiveType(archive_type)
        return {
            ArchiveType.RAW: self.s3u.path_join(self.load_archive_base_prefix, ArchiveType.RAW.value),
            ArchiveType.METADATA: self.s3u.path_join(self.load_archive_base_prefix, ArchiveType.METADATA.value),
            ArchiveType.PARSED: self.s3u.path_join(self.load_archive_base_prefix, ArchiveType.PARSED.value),
            ArchiveType.THUMBNAIL: self.s3u.path_join(self.load_archive_base_prefix, ArchiveType.THUMBNAIL.value)
        }[archive_type]

    def get_timestamped_archive_prefix(self, archive_type: t.Union[ArchiveType, str], ts: t.Union[dt.datetime, str]) -> str:
        """Get archive prefix at timestamp"""
        archive_type = ArchiveType(archive_type)
        return self.s3u.get_prefix_at_ts(
            base_prefix=self.get_archive_prefix(archive_type),
            ts=ts,
            ts_fmt=Config.TIMESTAMP_FORMAT
        )

    def get_archive_type_for_idoc(self, idoc: GenericIngestableDoc) -> ArchiveType:
        """Get Archive type for type of given idoc class"""
        return {
            IngestableRawDoc: ArchiveType.RAW,
            IngestableParsedDoc: ArchiveType.PARSED,
            IngestableMetadataDoc: ArchiveType.METADATA,
            IngestableThumbnailDoc: ArchiveType.THUMBNAIL
        }[idoc.__class__]

    def get_timestamped_archive_prefix_for_idoc(self, idoc: GenericIngestableDoc, ts: t.Union[dt.datetime, str]) -> str:
        """Get archive prefix for idoc"""
        return self.get_timestamped_archive_prefix(
            archive_type=self.get_archive_type_for_idoc(idoc),
            ts=ts
        )


    def get_ingestable_docs(self,
                            raw_dir: t.Union[Path, str],
                            metadata_dir: t.Optional[t.Union[Path, str]],
                            parsed_dir: t.Optional[t.Union[Path, str]],
                            thumbnail_dir: t.Optional[t.Union[Path, str]]
                            ) -> t.Iterable[IngestableDocGroup]:
        """Iterate through ingestable document/metadata pairs at given path
        :param raw_dir: Directory with raw pubs
        :param metadata_dir: Directory with metadata
        :param parsed_dir: Directory with parsed docs
        :param thumbnail_dir: Directory with thumbnails
        :return:
        """
        raw_dir = Path(raw_dir).resolve()
        metadata_dir = Path(metadata_dir).resolve() if metadata_dir else None
        parsed_dir = Path(parsed_dir).resolve() if parsed_dir else None
        thumbnail_dir = Path(thumbnail_dir).resolve() if thumbnail_dir else None

        def _get_corresponding_metadata_idoc(raw_doc: Path, metadata_dir: t.Optional[Path]) -> t.Optional[IngestableMetadataDoc]:
            if not metadata_dir:
                return None

            local_path = Path(metadata_dir, raw_doc.name + self.METADATA_DOC_EXTENSION)
            if not local_path.is_file():
                return None

            return IngestableMetadataDoc(
                local_path=local_path,
                metadata=Document.from_dict(json.load(local_path.open("r")))
            )

        def _get_corresponding_parsed_idoc(raw_doc: Path, parsed_dir: t.Optional[Path]) -> t.Optional[IngestableParsedDoc]:
            if not parsed_dir:
                return None

            local_path = Path(parsed_dir, raw_doc.stem + self.PARSED_DOC_EXTENSION)
            if not local_path.is_file():
                return None

            return IngestableParsedDoc(
                local_path=local_path
            )

        def _get_corresponding_thumbnail_idoc(raw_doc: Path, thumbnail_dir: t.Optional[Path]) -> t.Optional[IngestableThumbnailDoc]:
            if not thumbnail_dir:
                return None

            local_path = Path(thumbnail_dir, raw_doc.stem + self.THUMBNAIL_EXTENSION)
            if not local_path.is_file():
                return None

            return IngestableThumbnailDoc(
                local_path=local_path
            )

        for raw_doc_path in (
                p for p in raw_dir.iterdir()
                if p.is_file() and p.suffix.lower() in self.SUPPORTED_RAW_DOC_EXTENSIONS):

            yield IngestableDocGroup(
                raw_idoc=IngestableRawDoc(local_path=raw_doc_path),
                metadata_idoc=_get_corresponding_metadata_idoc(raw_doc=raw_doc_path, metadata_dir=metadata_dir),
                parsed_idoc=_get_corresponding_parsed_idoc(raw_doc=raw_doc_path, parsed_dir=parsed_dir),
                thumbnail_idoc=_get_corresponding_thumbnail_idoc(raw_doc=raw_doc_path, thumbnail_dir=thumbnail_dir)
            )

    def process_db_pub_updates(self, idgs: t.Iterable[IngestableDocGroup]) -> None:
        """Process publications table db updates using given docs
        :param idgs: iterable of IngestableDocGroup's
        :return: N/A, inserts/updates pub table as a side-effect
        """
        pubs: t.Dict[str, Publication] = {}
        with Config.connection_helper.orch_db_session_scope('rw') as session:
            for idg in idgs:
                # if there's no metadata, we can't update the db
                if not idg.metadata_idoc or not idg.thumbnail_idoc:
                    continue

                existing_pub = Publication.get_existing_from_doc(
                    doc=idg.metadata_idoc.metadata,
                    session=session)

                pub = (
                    existing_pub
                    or pubs.get(idg.metadata_idoc.metadata.doc_name)
                    or Publication.create_from_document(doc=idg.metadata_idoc.metadata)
                )

                pubs[pub.name] = pub

            if pubs:
                session.add_all(list(pubs.values()))
                session.commit()

    def process_db_doc_updates(self,
                               idgs: t.Iterable[IngestableDocGroup],
                               ts: t.Union[dt.datetime, str]) -> None:
        """Process versioned_doc table db updates using given docs"""
        ts = parse_timestamp(ts=ts, raise_parse_error=True)

        with Config.connection_helper.orch_db_session_scope('rw') as session:
            for idg in idgs:
                if not idg.metadata_idoc:
                    continue

                metadata = idg.metadata_idoc.metadata
                existing_doc = VersionedDoc.get_existing_from_doc(doc=metadata, session=session)
                if existing_doc:
                    session.add(existing_doc)
                else:
                    pub = Publication.get_or_create_from_document(doc=metadata, session=session)
                    if pub:
                        vdoc = VersionedDoc.create_from_document(
                            doc=metadata,
                            pub=pub,
                            filename=idg.raw_idoc.local_path.name,
                            doc_location=idg.raw_idoc.s3_path or "",
                            batch_timestamp=ts
                        )
                        session.add(vdoc)
            session.commit()

    def upload_docs_to_s3(self,
                          idgs: t.Iterable[IngestableDocGroup],
                          ts: t.Union[dt.datetime, str]) -> t.Iterable[IngestableDocGroup]:
        """Upload all raw/parsed/metadata docs in a group to s3"""
        ts = parse_timestamp(ts, raise_parse_error=True)

        def _upload_to_s3(idoc: GenericIngestableDoc, ts=dt.datetime) -> str:
            print(f"Uploading doc {idoc.local_path!s} to S3 ... ", file=sys.stderr)
            s3_location = Config.s3_utils.upload_file(
                file=idoc.local_path,
                object_prefix=self.get_timestamped_archive_prefix_for_idoc(idoc=idoc, ts=ts)
            )
            return s3_location

        for idg in idgs:
            idg.raw_idoc.s3_path = _upload_to_s3(idg.raw_idoc, ts=ts)
            if idg.parsed_idoc:
                idg.parsed_idoc.s3_path = _upload_to_s3(idg.parsed_idoc, ts=ts)
            if idg.metadata_idoc:
                idg.metadata_idoc.s3_path = _upload_to_s3(idg.metadata_idoc, ts=ts)
            if idg.thumbnail_idoc:
                idg.thumbnail_idoc.s3_path = _upload_to_s3(idg.thumbnail_idoc, ts=ts)

            yield idg

    def load(self,
             raw_dir: t.Union[Path, str],
             metadata_dir: t.Optional[t.Union[Path, str]],
             parsed_dir: t.Optional[t.Union[Path, str]],
             thumbnail_dir: t.Optional[t.Union[Path, str]],
             ingest_ts: t.Union[dt.datetime, str],
             update_s3: bool,
             update_db: bool) -> None:
        """Process all doc/pub updates for eligible files"""
        ingest_ts = parse_timestamp(ts=ingest_ts, raise_parse_error=True)
        print(f"Running load:\n\traw_dir={raw_dir}\n\tmetadata_dir={metadata_dir}\n\tparsed_dir={parsed_dir}\n\t"
              f"thumbnail_dir={thumbnail_dir}")

        idgs = list(self.get_ingestable_docs(
            raw_dir=raw_dir,
            metadata_dir=metadata_dir,
            parsed_dir=parsed_dir,
            thumbnail_dir=thumbnail_dir
        ))

        if update_db:
            print("Updating S3: Updating pub entries in 'publications' table ...", file=sys.stderr)
            self.process_db_pub_updates(idgs=idgs)
        else:
            print("Skipping updates to 'publications' table ...", file=sys.stderr)

        uploaded_idgs = None
        if update_s3:
            print("Uploading docs to S3 ...", file=sys.stderr)
            uploaded_idgs = list(self.upload_docs_to_s3(idgs=idgs, ts=ingest_ts))
        else:
            print("Skipping s3 uploads of docs ...", file=sys.stderr)

        if update_db:
            print("Updating S3: Updating pub entries in 'publications' table ...", file=sys.stderr)
            self.process_db_doc_updates(idgs=uploaded_idgs or idgs, ts=ingest_ts)
        else:
            print("Skipping updates to 'versioned_docs' table ...", file=sys.stderr)
