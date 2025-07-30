# pylint: disable=W0622
"""cubicweb-editorjs application packaging information"""


modname = "cubicweb_editorjs"
distname = "cubicweb-editorjs"

numversion = (0, 3, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Add editorjs format for RichString"
web = "http://www.cubicweb.org/project/%s" % distname

__depends__ = {
    "cubicweb": ">=4.5.2,<6.0.0",
    "cubicweb-web": ">=1.0.0,<2.0.0",
}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python :: 3",
    "Programming Language :: JavaScript",
]
