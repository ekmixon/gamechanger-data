from pathlib import Path
from dataPipelines.gc_crawler.data_model import Document, DownloadableItem
import filetype

Accepted_document_groups = ["Memo", "pdf"]


class ManualMetadata:

    def __init__(self, input_directory, document_group):
        self.input_directory = input_directory
        self.document_group = document_group
        p = Path(self.input_directory).glob("**/*")
        self.files = [
            x
            for x in p
            if x.is_file()
            and (
                str(x).endswith("pdf")
                or str(x).endswith("html")
                or filetype.guess(str(x)) is not None
                and filetype.guess(str(x)).mime in ["pdf", "application/pdf"]
            )
        ]

        self.metadata_files = [Path(x).stem for x in p if x.is_file() and filetype.guess(str(x)) is not None and (
                filetype.guess(str(x)).mime == "metadata")]

    def create_document(self, file) -> Document:
        doc = None
        if self.document_group == "Memo":
            pdi = DownloadableItem(doc_type="pdf", web_url="manual.ingest")
            version_hash_fields = {"filename": Path(file).name}
            doc = Document(
                doc_name=Path(file).stem,
                doc_title=Path(file).stem,
                doc_num="",
                doc_type="Memo",
                publication_date="N/A",
                cac_login_required=True,
                crawler_used="Memo",
                source_page_url="manual.ingest",
                version_hash_raw_data=version_hash_fields,
                downloadable_items=[pdi]
            )
        elif self.document_group == "pdf":
            pdi = DownloadableItem(doc_type="pdf", web_url="manual.ingest")
            version_hash_fields = {"filename": Path(file).name}
            doc = Document(
                doc_name=Path(file).stem,
                doc_title=Path(file).stem,
                doc_num="",
                doc_type="pdf",
                publication_date="N/A",
                cac_login_required=True,
                crawler_used="pdf",
                source_page_url="manual.ingest",
                version_hash_raw_data=version_hash_fields,
                downloadable_items=[pdi]
            )

        return doc

    def create_metadata(self):
        if self.document_group not in Accepted_document_groups:
            return
        for file in self.files:
            print(self.metadata_files)
            if Path(file).stem not in self.metadata_files:
                doc = self.create_document(file)

                outname = f'{str(file)}.metadata'
                print(outname)
                if doc:
                    with open(outname, "w") as f:
                        f.write(doc.to_json())



