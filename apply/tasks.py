import glob
import os
import re

from invoke import task

_VALID_JINJA_EXTENSIONS = (".html", ".jinja", ".jinja2", ".j2")


def _remove_whitespace_newlines_from_trans_tags(file, content: str):
    matches = re.findall(r"({%\s*trans\s*%}(.|[\S\s]*?){%\s*endtrans\s*%})", content)

    content_replaced = content
    for outer, center in matches:
        normalised_whitespace_trans = re.sub(r"\s+", " ", center).strip()

        outer_replaced = outer.replace(center, normalised_whitespace_trans)

        rwhitespace = center[len(center.rstrip()) :]  # noqa: E203
        lwhitespace = center[: len(center) - len(center.lstrip())]

        outer_replaced_whitespace = lwhitespace + outer_replaced + rwhitespace
        content_replaced = content_replaced.replace(outer, outer_replaced_whitespace)

    if content != content_replaced:
        with open(file, "w") as f:
            f.write(content_replaced)
        print(f"Removed newlines/tabs from {file}")
    else:
        print(f"No newlines/tabs to remove from {file}")

    return 0


def _find_missing_translations(file, content: str):
    matches = list(
        re.findall(
            r"(msgid (?:\".*\"\n)+)(?=msgstr" r" \"\"(?!\n\")\n*(?=\n|msgid|\"\"))",
            content,
        )
    )

    missing_translations = []
    for match in matches:
        original = "".join(re.findall(r"\"(.*)\"", match))
        missing_translations.append(original)

    # echo missing translations to stdout with a newline between each
    if missing_translations:
        print(f"Missing translations in {file}:")
        for translation in missing_translations:
            print(f"  {translation}")
        print()
    else:
        print(f"No missing translations in {file}")

    return 0


def _process_file(file: str, function: callable):
    with open(file, "r") as f:
        content = f.read()
    return function(file, content)


def _traverse_files(path: str, function: callable, extensions: tuple[str]):
    ret = 0

    if os.name == "nt":
        path = path.replace("/", "\\")

    filepath = os.path.join(os.getcwd(), path)
    if os.path.isfile(filepath) and filepath.endswith(extensions):
        ret |= _process_file(filepath, function)

    for full_filepath in glob.glob(filepath + "/**", recursive=True):
        if full_filepath.endswith(extensions):
            ret |= _process_file(full_filepath, function)

    return ret


@task
def fix_trans_tags(_, path="app/templates"):
    return _traverse_files(
        path,
        _remove_whitespace_newlines_from_trans_tags,
        _VALID_JINJA_EXTENSIONS,
    )


@task
def find_missing_trans(_, path="app/translations/cy/LC_MESSAGES/messages.po"):
    return _traverse_files(path, _find_missing_translations, (".po",))


@task
def pybabel_extract(c):
    c.run("pybabel extract -F babel.cfg -o messages.pot .")


@task
def pybabel_update(c):
    c.run("pybabel update -i messages.pot -d app/translations")


@task
def pybabel_compile(c):
    c.run("pybabel compile -d app/translations")
