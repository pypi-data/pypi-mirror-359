# pylint: disable=W0622
"""cubicweb-sentry application packaging information"""

modname = "sentry"
distname = "cubicweb-sentry"

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "support for Sentry (getsentry.com)"
web = f"https://forge.extranet.logilab.fr/cubicweb/cubes/{distname}"

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]

__depends__ = {
    "cubicweb": ">= 4.5.2,< 6.0.0",
    "sentry-sdk": ">= 2.8.0, < 3.0.0",
}
__recommends__ = {}
