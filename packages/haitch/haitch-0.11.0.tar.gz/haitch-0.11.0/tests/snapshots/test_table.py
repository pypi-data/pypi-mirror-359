from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_table(snapshot: Snapshot) -> None:
    dom = H.table(
        H.colgroup(
            H.col(span=2),
        ),
        H.tr(
            H.th("Name"),
            H.th("Age"),
        ),
        H.tr(
            H.td("Maria Sanchez"),
            H.td("28"),
        ),
        H.tr(
            H.td("Michael Johnson"),
            H.td("34"),
        ),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
