import re


def get_value_from_string(string: str) -> str | None:
    result = re.search(r"(\d+г)", string)
    if result:
        return result.group()


def clean_text(text: str | None) -> str:
    if text:
        return text.replace("\n", "").replace("\t", "").replace("\xa0", " ")
