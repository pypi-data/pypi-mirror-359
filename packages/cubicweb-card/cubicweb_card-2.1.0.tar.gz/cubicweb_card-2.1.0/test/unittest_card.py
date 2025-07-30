"Card unit test"

import re
import unittest

from cubicweb.devtools import BASE_URL
from cubicweb.devtools.testlib import MAILBOX
from cubicweb_web.devtools.testlib import WebCWTC
from cubicweb_web.ext.rest import rest_publish


class CardTests(WebCWTC):
    def test_notifications(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.create_entity(
                "Card", title="sample card", synopsis="this is a sample card"
            )
            self.assertEqual(len(MAILBOX), 0)
            cnx.commit()
        self.assertEqual(len(MAILBOX), 1)
        self.assertEqual(
            re.sub(r"#\d+", "#EID", MAILBOX[0].subject), "New Card #EID (admin)"
        )


class RestTC(WebCWTC):
    def context(self, cnx):
        return cnx.execute('CWUser X WHERE X login "admin"').get_entity(0, 0)

    def test_card_role_create(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertEqual(
                rest_publish(self.context(cnx), ":card:`index`"),
                f'<p><a class="doesnotexist reference" '
                f'href="{BASE_URL}card/index">index</a></p>\n',
            )

    def test_card_role_create_subpage(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertEqual(
                rest_publish(self.context(cnx), ":card:`foo/bar`"),
                f'<p><a class="doesnotexist reference" '
                f'href="{BASE_URL}card/foo/bar">foo/bar</a></p>\n',
            )  # noqa

    def test_card_role_link(self):
        with self.admin_access.client_cnx() as cnx:
            cnx.create_entity(
                "Card", wikiid="index", title="Site index page", synopsis="yo"
            )
            self.assertEqual(
                rest_publish(self.context(cnx), ":card:`index`"),
                f'<p><a class="reference" '
                f'href="{BASE_URL}card/index">index</a></p>\n',
            )

    def test_nocard_create(self):
        with self.admin_access.web_request("card/foobar") as req:
            content = self.app_handle_request(req)
            create_url = req.build_url("add/Card?wikiid=foobar")
            self.assertIn(f' href="{create_url}"'.encode(), content)
            self.assertEqual(req.status_out, 404)


if __name__ == "__main__":
    unittest.main()
