import pytest
from invoke import MockContext
from invoke import Result
from tasks import find_missing_trans
from tasks import fix_trans_tags


@pytest.mark.parametrize(
    "input, expected",
    [
        pytest.param(
            "{% trans %}\n\n Random\nString\tExample \n\n{% endtrans %}",
            "\n\n {% trans %}Random String Example{% endtrans %} \n\n",
        ),
        pytest.param(
            "<html>{% trans %}\n\n Random\nString\tExample \n\n{% endtrans %}</html>",
            "<html>\n\n {% trans %}Random String Example{% endtrans %} \n\n</html>",
        ),
        pytest.param(
            "\n{% trans %}\nNew\nline\n{% endtrans %}\n{%trans%}\nA\ntab\t{%endtrans%}",
            "\n\n{% trans %}New line{% endtrans %}\n\n\n{%trans%}A tab{%endtrans%}\t",
        ),
    ],
)
def test_remove_whitespace_newlines_from_trans_tags_file(tmpdir, input, expected):
    c = MockContext(run=Result("Darwin\n"))

    f = tmpdir.join("f.html")
    f.write(input)

    assert fix_trans_tags(c, f.strpath) == 0

    assert f.read() == expected


def test_remove_whitespace_newlines_from_trans_tags_dir(tmpdir):
    c = MockContext(run=Result("Darwin\n"))

    f = tmpdir.join("f.html")
    f2 = tmpdir.join("f.html")
    f.write("{% trans %}a\nb{% endtrans %}")
    f2.write("{% trans %}a\nb{% endtrans %}")

    assert fix_trans_tags(c, str(tmpdir)) == 0

    assert f.read() == "{% trans %}a b{% endtrans %}"
    assert f2.read() == "{% trans %}a b{% endtrans %}"


def test_find_missing_trans(tmpdir, capsys):
    c = MockContext(run=Result("Darwin\n"))

    f = tmpdir.join("f.po")
    f.write(
        "# Welsh translations for PROJECT.\n"
        "# Copyright (C) 2022 ORGANIZATION\n"
        "\n"
        "#: example/file.html:1\n"
        'msgid "A missing translation"\n'
        'msgstr ""\n'
        "\n"
        'msgid "A non-missing translation"\n'
        'msgstr "A non-missing translation"\n'
        "\n"
        'msgid "Another missing translation"\n'
        'msgstr ""\n'
        "\n"
        "#: example/file.html:1\n"
        'msgid ""\n'
        '"A third missing translation, that spans multiple"\n'
        '" lines.  We want to capture all of its content."\n'
        'msgstr ""\n'
        "\n"
        'msgid ""\n'
        '"A fourth missing translation, that spans multiple"\n'
        '" lines.  We want to capture all of its content."\n'
        'msgstr ""\n'
        "\n"
        'msgid ""\n'
        '"Not missing multi line translation."\n'
        '"Second line"\n'
        'msgstr "Translated."\n'
    )

    assert find_missing_trans(c, f.strpath) == 0

    stdoutput = capsys.readouterr().out
    assert (
        stdoutput
        == f"Missing translations in {f.strpath}:\n  A missing translation\n "
        " Another missing translation\n  A third missing translation, that"
        " spans multiple lines.  We want to capture all of its content.\n "
        " A fourth missing translation, that spans multiple lines.  We"
        " want to capture all of its content.\n\n"
    )
