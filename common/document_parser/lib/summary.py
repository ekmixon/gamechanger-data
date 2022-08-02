from gamechangerml.configs.config import BertSummConfig
from gamechangerml.src.featurization.summary import GensimSumm


def get_summary(text: str) -> str:

    long_doc = len(text) >= BertSummConfig.MODEL_ARGS['doc_limit']
    try:
        return GensimSumm(text, long_doc=long_doc, word_count=30).make_summary()
    except Exception as e:
        print(e)
        return ""


def add_summary(doc_dict):
    summary = get_summary(doc_dict["text"])
    doc_dict["summary_30"] = summary
    return doc_dict
