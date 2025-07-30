from pytest_snapshot.plugin import Snapshot

import haitch as H
from tests.helpers import get_snapshot_name, prettify


def test_form(snapshot: Snapshot) -> None:
    dom = H.form(action="", method="get")(
        H.fieldset(
            H.legend("Find users"),
            H.label(for_="name")("Enter name: "),
            H.input(type_="text", name="name", id_="name", required=True),
            H.button("Search"),
        ),
    )

    snapshot.assert_match(prettify(dom), get_snapshot_name())
