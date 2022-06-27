import re
from os import getenv


def sanitize_text(text):
    """
    Sanitizes the text for tts.
       What gets removed:
    - following characters`^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
    - any http or https links
    """

    # remove any urls from the text
    regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
    result = re.sub(regex_urls, " ", text)

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", result)

    # Subreddit "Macro" changer
    pattern = re.compile(str(getenv("REDDITMACRO")), re.IGNORECASE)
    result = pattern.sub("Explain like I'm 5", result)

    # remove extra whitespace
    return " ".join(result.split())
