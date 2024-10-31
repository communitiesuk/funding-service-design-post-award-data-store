from flask_babel import gettext


def get_formatted(value: str):
    languages = {"en": gettext("English"), "cy": gettext("Welsh")}

    return languages.get(value, value)
