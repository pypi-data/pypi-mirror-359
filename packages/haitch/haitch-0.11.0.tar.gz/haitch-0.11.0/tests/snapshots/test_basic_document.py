from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_basic_document(snapshot: Snapshot) -> None:
    styles = """
    p {
        color: green;
    }
    """
    dom = H.html(lang="en")(
        H.head(
            H.meta(charset="utf-8"),
            H.meta(name="viewport", content="width=device-width, initial-scale=1"),
            H.meta(http_equiv="x-ua-compatible", content="ie=edge"),
            H.title("Basic page"),
            H.link(href="main.css", rel="stylesheet"),
            H.link(href="custom.css", rel="stylesheet"),
            H.script(src="main.js", defer=True),
            H.style(styles),
        ),
        H.body(class_="container")(
            H.noscript("JavaScript is not enabled. Good job."),
            H.div(
                H.p("This is a ", H.mark("mark"), "."),
                H.p("The date is ", H.time(datetime="2018-07-07")("July 7th")),
                H.a(href="#")("Hyperlink"),
                H.hr(),
                H.img(src="image.png", alt="cool image"),
                H.br(),
                H.ol(
                    H.li("First point"),
                    H.li("Second point"),
                ),
            ),
            H.pre("print('hello, world')"),
            H.unsafe("You can pass <i>raw</i> HTML with unsafe tag."),
        ),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
