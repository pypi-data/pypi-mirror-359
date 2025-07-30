# pylint: disable=W0622
"""cubicweb-sioc application packaging information"""

modname = "sioc"
distname = "cubicweb-sioc"

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Specific views for SIOC (Semantically-Interlinked Online Communities)"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"
classifiers = [
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
]

__depends__ = {
    "cubicweb": ">= 4.10.0, < 6.0.0",
    "cubicweb-web": ">= 1.5.2, < 2.0.0",
}
__recommends__ = {}
