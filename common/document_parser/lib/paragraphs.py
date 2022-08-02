import syntok.segmenter as segmenter

import re
import string
from gamechangerml.src.utilities.text_utils import utf8_pass, clean_text


def get_paragraph_text(segmented):
    return "".join(
        " ".join([token.value for token in sentence]) for sentence in segmented
    )


def create_paragraph_dict(page_num, paragraph_num, paragraph_text, doc_dict):
    par = {
        "type": "paragraph",
        "filename": doc_dict["filename"],
        "par_inc_count": doc_dict["par_count_i"],
        "id": doc_dict["filename"] + "_" + str(doc_dict["par_count_i"]),
    }

    doc_dict["par_count_i"] += 1
    par["par_count_i"] = paragraph_num
    par["page_num_i"] = page_num

    par["par_raw_text_t"] = utf8_pass(paragraph_text)

    par["entities"] = []

    return par


def handle_page_paragraphs(page_num, page_text, doc_dict):
    for paragraph_num, paragraph in enumerate(segmenter.process(page_text)):
        paragraph_text = get_paragraph_text(paragraph)
        paragraph_dict = create_paragraph_dict(
            page_num, paragraph_num, paragraph_text, doc_dict)
        doc_dict["paragraphs"].append(paragraph_dict)


def handle_paragraphs(doc_dict):
    doc_dict["paragraphs"] = []
    for page_num, page in enumerate(doc_dict["pages"]):
        page_text = page["p_raw_text"]
        handle_page_paragraphs(page_num, page_text, doc_dict)
