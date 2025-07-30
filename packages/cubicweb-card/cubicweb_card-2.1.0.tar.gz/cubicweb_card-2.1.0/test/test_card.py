"""template automatic tests"""

import unittest

from cubicweb_web.devtools.testlib import WebCWTC


class AutomaticWebTest(WebCWTC):
    def to_test_etypes(self):
        return {"Card"}


class CardTC(WebCWTC):
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.card = cnx.create_entity(
                "Card", title="sample card", synopsis="this is a sample card"
            ).eid
            cnx.commit()

    def test_views(self):
        with self.admin_access.web_request() as req:
            fobj = req.entity_from_eid(self.card)
            self.vreg["views"].select_or_none("inlined", fobj._cw, rset=fobj.cw_rset)


if __name__ == "__main__":
    unittest.main()
