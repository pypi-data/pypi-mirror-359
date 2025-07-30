# pylint: disable-msg=W0622
"""cubicweb-card application packaging information"""

modname = "cubicweb_card"
distname = "cubicweb-card"

numversion = (2, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"
description = "card/wiki component for the CubicWeb framework"
classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">= 4.5.2, < 6.0.0",
    "cubicweb-web": ">= 1.0.0, < 2.0.0",
    "docutils": None,
}
__recommends__ = {
    "cubicweb-preview": None,
    "cubicweb-seo": None,
}
