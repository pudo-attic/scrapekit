import re


def collapse_whitespace(text):
    """ Collapse all consecutive whitespace, newlines and tabs
    in a string into single whitespaces, and strip the outer
    whitespace. This will also accept an ``lxml`` element and
    extract all text. """
    if text is None:
        return None
    if hasattr(text, 'xpath'):
        text = text.xpath('string()')
    text = re.sub('\s+', ' ', text)
    return text.strip()
