from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_multimedia(snapshot: Snapshot) -> None:
    dom = H.fragment(
        H.video(
            H.source(src="friday.webm", type_="video/webm"),
            H.track(default=True, src="friday.vtt"),
        ),
        H.figure(
            H.img(src="elephant.jpg", alt="Elephant at sunset"),
            H.figcaption("An elephant at sunset"),
        ),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
