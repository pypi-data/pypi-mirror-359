# pylint: disable=W0622
"""cubicweb-squareui application packaging information"""

modname = "squareui"
distname = "cubicweb-squareui"

numversion = (2, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "data-centric user interface for cubicweb based on bootstrap"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"

__depends__ = {
    "cubicweb": ">= 4.5.2, < 6.0.0",
    "cubicweb-web": ">= 1.0.0, < 2.0.0",
    "cubicweb-bootstrap": ">= 2.0.0, < 3.0.0",
}

__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]
